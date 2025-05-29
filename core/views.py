from django.shortcuts import render, redirect
from .forms import RegisterForm
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Group, StudentProfile
from django.shortcuts import render
from notas.mongo import get_collection
from django.db import connection




def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:login')  # o tu dashboard
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token_key = response.data.get('token')
        from rest_framework.authtoken.models import Token as AuthToken
        token = AuthToken.objects.get(key=token_key)
        return Response({'token': token.key, 'user_id': token.user_id, 'username': token.user.username})


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario registrado correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# HTML

def landing_page(request):
    return render(request, 'landing.html')  

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:home') 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('landing')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form}) 



@login_required
def dashboard_view(request):
    user = request.user
    current_semester = "2024-1"
    grades_collection = get_collection("grades")
    
    student_profile = StudentProfile.objects.get(user=user)
    student_code = student_profile.codigo  # o como se llame el campo con el ID

    # 1. Obtener las notas del usuario desde MongoDB
    mongo_grades = list(grades_collection.find({"student_id": student_code}))

    # 2. Filtrar las que sí son del semestre actual según Postgres
    valid_grades = []
    with connection.cursor() as cursor:
        for grade_doc in mongo_grades:
            subject_code = grade_doc.get("subject_code")
            group_number = grade_doc.get("group_number")

            cursor.execute(
                """
                SELECT semester FROM groups
                WHERE subject_code = %s AND number = %s
                """,
                [subject_code, group_number]
            )
            result = cursor.fetchone()
            if result and result[0] == current_semester:
                valid_grades.append(grade_doc)

    # 3. Estadísticas
    subject_codes = {doc["subject_code"] for doc in valid_grades}
    current_semester_subjects = len(subject_codes)

    total_grades = 0
    total_sum = 0.0

    for doc in valid_grades:
        for g in doc.get("grades", []):
            grade_value = g.get("grade")
            if isinstance(grade_value, (int, float)):
                total_grades += 1
                total_sum += grade_value

    current_average = total_sum / total_grades if total_grades > 0 else 0.0

    context = {
        "current_semester_subjects": current_semester_subjects,
        "total_grades": total_grades,
        "current_average": round(current_average, 1),
    }

    return render(request, 'home.html', context)


@login_required
def profile(request):
    # Mostrar datos del usuario para gestión de cuenta (puedes extender con edición)
    return render(request, 'profile.html', {'user': request.user})


def subjects_by_semester_group(request):
    groups = Group.objects.order_by('semester', 'number')
    return render(request, 'subjects.html', {'groups': groups})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Group, Subject, Employee as Professor, Area, Enrollment

@login_required
def subjects_view(request):
    # Obtener filtros
    semester_filter = request.GET.get('semester', '')
    area_filter = request.GET.get('area', '')
    professor_filter = request.GET.get('professor', '')
    search_filter = request.GET.get('search', '')

    # Query base
    groups_query = Group.objects.select_related(
        'subject_code__program_code__area_code'  # Para poder filtrar por área
    )

    # Aplicar filtros
    if semester_filter:
        groups_query = groups_query.filter(semester=semester_filter)

    if area_filter:
        groups_query = groups_query.filter(subject_code__program_code__area_code__code=area_filter)

    if professor_filter:
        groups_query = groups_query.filter(professor_id=professor_filter)

    if search_filter:
        groups_query = groups_query.filter(
            Q(subject_code__name__icontains=search_filter) |
            Q(subject_code__code__icontains=search_filter)
        )

    # Anotar cantidad de inscritos por grupo
    groups_query = groups_query.annotate(
        enrolled_count=Count('enrollment')
    )

    # Verificar inscripciones del usuario actual
    user_enrollments = set(
        Enrollment.objects.filter(student=request.user)
        .values_list('group__subject_code__code', 'group__number', 'group__semester')
    )

    # Organizar por semestre y materia
    subjects_by_semester = {}

    for group in groups_query:
        semester = group.semester
        subject_code = group.subject_code.code

        if semester not in subjects_by_semester:
            subjects_by_semester[semester] = {}

        if subject_code not in subjects_by_semester[semester]:
            subjects_by_semester[semester][subject_code] = {
                'subject': group.subject_code,
                'groups': []
            }

        group.is_enrolled = (subject_code, group.number, semester) in user_enrollments
        subjects_by_semester[semester][subject_code]['groups'].append(group)

    # Convertir a lista ordenada
    subjects_by_semester_list = {
        semester: [subjects_by_semester[semester][code] for code in sorted(subjects_by_semester[semester])]
        for semester in sorted(subjects_by_semester, reverse=True)
    }

    # Estadísticas
    stats = {
        'total_semesters': Group.objects.values('semester').distinct().count(),
        'total_subjects': Subject.objects.count(),
        'total_groups': groups_query.count(),
        'total_professors': Professor.objects.filter(
            id__in=groups_query.values_list('professor_id', flat=True)
        ).count(),
        'available_spots': None  # No se usa max_students
    }

    # Filtros disponibles
    available_semesters = Group.objects.values_list('semester', flat=True).distinct().order_by('-semester')

    available_areas = Area.objects.filter(
        code__in=Subject.objects.filter(
            code__in=groups_query.values_list('subject_code__code', flat=True)
        ).values_list('program_code__area_code__code', flat=True)
    ).distinct()

    available_professors = Professor.objects.filter(
        id__in=groups_query.values_list('professor_id', flat=True)
    ).distinct().order_by('first_name', 'last_name')

    context = {
        'subjects_by_semester': subjects_by_semester_list,
        'stats': stats,
        'available_semesters': available_semesters,
        'available_areas': available_areas,
        'available_professors': available_professors,
    }

    return render(request, 'subjects.html', context)
