from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .mongo import get_collection
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Group
from django.contrib.auth.models import User
from core.models import StudentProfile  # Import StudentProfile


class GradesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.user.profile.codigo
        grades = list(get_collection('grades').find({'student_id': student_id}, {'_id': 0}))
        return Response(grades)

@login_required
def evaluation_plan(request, subject_code, group_number, semester):
    # Obtener el grupo como objeto relacional (ORM)
    group = get_object_or_404(
        Group.objects.select_related(
            'subject_code__program_code__area_code',
            
        ),
        subject_code__code=subject_code,
        number=group_number,
        semester=semester
    )

    # Buscar el plan de evaluación en Mongo
    evaluation_plan = get_collection('evaluation_plans').find_one({
        "group.subject_code": subject_code,
        "group.group_number": group_number,
        "group.semester": semester
    })

    # Actividades
    activities = evaluation_plan.get('activities', []) if evaluation_plan else []
    total_percentage = sum(activity.get('percentage', 0) for activity in activities)

    comments = []
    comments_cursor = get_collection('comments').find({
        "group.subject_code": subject_code,
        "group.group_number": int(group_number),
        "group.semester": semester
    }).sort("created_at", -1)
    comments = list(comments_cursor)

    #  Mapear comentarios a nombre completo del autor
    perfiles = StudentProfile.objects.select_related('user').all()
    codigo_to_name = {p.codigo: f"{p.user.first_name} {p.user.last_name}" for p in perfiles}

    for comment in comments:
        student_id = comment.get('student_id')
        comment['author_name'] = codigo_to_name.get(student_id, student_id)
        comment['created_at'] = comment.get('created_at')

    
    

    # Lógica de permisos
    can_edit_plan = (
        evaluation_plan is None or
        request.user.is_staff 
    )

    context = {
        'group': group,
        'professor': group.get_professor(),
        'author': request.user.profile.codigo,
        'subject_code': subject_code,
        'group_number': group_number,
        'semester': semester,
        'evaluation_plan': evaluation_plan,
        'activities': activities,
        'total_percentage': total_percentage,
        'comments': comments,
        'can_edit_plan': can_edit_plan,
    }

    return render(request, 'evaluation_plan.html', context)

@login_required
def edit_evaluation_plan(request, subject_code, group_number, semester):
    # Aquí iría la lógica para editar el plan
    return render(request, 'edit_evaluation_plan.html', {
        'subject_code': subject_code,
        'group_number': group_number,
        'semester': semester,
    })
    
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .mongo import get_collection
import json
from datetime import datetime

@login_required
@require_POST
def add_comment(request, subject_code, group_number, semester):
    data = json.loads(request.body.decode('utf-8'))
    comment_text = data.get("comment", "").strip()

    if not comment_text:
        return JsonResponse({'error': 'El comentario no puede estar vacío.'}, status=400)

    comment = {
        "student_id": request.user.profile.codigo,
        "target_student_id": request.user.profile.codigo,  # Esto puedes cambiarlo según el caso
        "group": {
            "subject_code": subject_code,
            "group_number": int(group_number),
            "semester": semester
        },
        "comment": comment_text,
        "created_at": datetime.utcnow()
    }

    get_collection('comments').insert_one(comment)

    return JsonResponse({'message': 'Comentario agregado exitosamente.'})