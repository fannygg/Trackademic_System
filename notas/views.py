from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Group
from django.contrib.auth.models import User
from core.models import StudentProfile  # Import StudentProfile
from core.models import Subject, Group, StudentProfile
from django.http import Http404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from trackademic.utils.mongo import get_collection
import json
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from bson.objectid import ObjectId
import datetime
import json

class GradesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.user.profile.codigo
        grades = list(get_collection('grades').find({'student_id': student_id}, {'_id': 0}))
        return Response(grades)


# Helper para obtener el identificador del usuario actual
def get_user_identifier(user):
    student_profile = StudentProfile.objects.filter(user=user).first()
    return student_profile.codigo if student_profile and student_profile.codigo else user.username

@login_required
def evaluation_plans_list(request, subject_code):
    """
    Vista para listar todos los planes de evaluación disponibles para una materia específica.
    """
    # Obtener materia
    try:
        subject = Subject.objects.get(code=subject_code)
    except Subject.DoesNotExist as exc:
        raise Http404("Materia no encontrada") from exc

    # Obtener grupos
    groups = Group.objects.filter(subject_code=subject_code).order_by('-semester', 'number')

    
    # Obtener colecciones de MongoDB usando get_collection()
    collections = get_collection('comments')
    
    comments_collection = get_collection('comments')
    evaluation_plans_collection = get_collection('evaluation_plans')
    grades_collection = get_collection('grades')


    # Identificador del usuario logueado
    user_id = get_user_identifier(request.user)

    groups_with_plans = []

    for group in groups:
        group_filter = {
            "subject_code": subject_code,
            "group_number": group.number,
            "semester": group.semester
        }

        evaluation_plan = evaluation_plans_collection.find_one({"group": group_filter})

        activities = evaluation_plan.get('activities', []) if evaluation_plan else []
        activities_count = len(activities)
        total_percentage = sum(activity.get('percentage', 0) for activity in activities)

        comments_count = comments_collection.count_documents({"group": group_filter})
        professor = group.get_professor()

        # Verifica si el usuario puede editar el plan (solo si lo creó)
        created_by = evaluation_plan.get('created_by') if evaluation_plan else None
        can_edit = created_by == user_id if evaluation_plan else False

        groups_with_plans.append({
            'group': group,
            'professor': professor,
            'has_plan': evaluation_plan is not None,
            'evaluation_plan': evaluation_plan,
            'activities': activities,
            'activities_count': activities_count,
            'total_percentage': total_percentage,
            'comments_count': comments_count,
            'is_complete': total_percentage == 100 if evaluation_plan else False,
            #'can_edit': can_edit,
            'created_at': evaluation_plan.get('created_at') if evaluation_plan else None,
            'created_by': created_by,
        })

    # Estadísticas y filtros
    total_groups = len(groups_with_plans)
    groups_with_plans_count = sum(1 for g in groups_with_plans if g['has_plan'])
    complete_plans_count = sum(1 for g in groups_with_plans if g['is_complete'])

    semester_filter = request.GET.get('semester', '')
    status_filter = request.GET.get('status', '')

    if semester_filter:
        groups_with_plans = [g for g in groups_with_plans if g['group'].semester == semester_filter]
    if status_filter:
        if status_filter == 'complete':
            groups_with_plans = [g for g in groups_with_plans if g['is_complete']]
        elif status_filter == 'incomplete':
            groups_with_plans = [g for g in groups_with_plans if g['has_plan'] and not g['is_complete']]
        elif status_filter == 'no_plan':
            groups_with_plans = [g for g in groups_with_plans if not g['has_plan']]

    all_semesters = sorted(list(set(g['group'].semester for g in groups_with_plans)), reverse=True)

    context = {
        'subject': subject,
        'groups_with_plans': groups_with_plans,
        'total_groups': total_groups,
        'groups_with_plans_count': groups_with_plans_count,
        'complete_plans_count': complete_plans_count,
        'all_semesters': all_semesters,
        'current_semester_filter': semester_filter,
        'current_status_filter': status_filter,
    }

    return render(request, 'evaluation_plans_list.html', context)



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
    evaluation_plans_collection = get_collection('evaluation_plans')
    evaluation_plan = evaluation_plans_collection.find_one({
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
    # Verifica si el usuario puede editar el plan (solo si lo creó)
    created_by = evaluation_plan.get('created_by') if evaluation_plan else None
    can_edit = created_by == request.user.profile.codigo if evaluation_plan else False

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
        'can_edit_plan': can_edit,
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
        "created_at": datetime.now()
    }

    get_collection('comments').insert_one(comment)

    return JsonResponse({'message': 'Comentario agregado exitosamente.'})

login_required
def create_evaluation_plan(request, subject_code, group_number, semester):
    """
    Vista para crear un nuevo plan de evaluación con actividades.
    """
    # Verificar que el grupo existe
    try:
        group = Group.objects.get(
            subject_code=subject_code, 
            number=group_number, 
            semester=semester
        )
    except Group.DoesNotExist:
        messages.error(request, "El grupo especificado no existe.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    # Verificar si ya existe un plan
    group_filter = {
        "subject_code": subject_code,
        "group_number": int(group_number),
        "semester": semester
    }
    
    evaluation_plans_collection = get_collection('evaluation_plans')

    
    existing_plan = evaluation_plans_collection.find_one({"group": group_filter})
    if existing_plan:
        messages.warning(request, "Ya existe un plan de evaluación para este grupo.")
        return redirect('evaluation_plan_detail', 
                       subject_code=subject_code, 
                       group_number=group_number, 
                       semester=semester)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            description = request.POST.get('description', '').strip()
            activities_json = request.POST.get('activities', '[]')
            activities = json.loads(activities_json)
            
            # Validaciones
            if not activities:
                messages.error(request, "Debe agregar al menos una actividad.")
                return render(request, 'create_evaluation_plan.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                })
            
            # Validar que la suma de porcentajes sea 100
            total_percentage = sum(activity.get('percentage', 0) for activity in activities)
            if total_percentage != 100:
                messages.error(request, f"La suma de porcentajes debe ser 100%. Actualmente es {total_percentage}%.")
                return render(request, 'create_evaluation_plan.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                })
            
            # Validar que todas las actividades tengan nombre y porcentaje
            for i, activity in enumerate(activities):
                if not activity.get('name', '').strip():
                    messages.error(request, f"La actividad {i+1} debe tener un nombre.")
                    return render(request, 'create_evaluation_plan.html', {
                        'subject_code': subject_code,
                        'group_number': group_number,
                        'semester': semester,
                    })
                
                if not activity.get('percentage') or activity.get('percentage') <= 0:
                    messages.error(request, f"La actividad '{activity.get('name')}' debe tener un porcentaje válido.")
                    return render(request, 'create_evaluation_plan.html', {
                        'subject_code': subject_code,
                        'group_number': group_number,
                        'semester': semester,
                    })
            
            # Obtener información del usuario
            student_profile = StudentProfile.objects.filter(user=request.user).first()
            created_by = student_profile.codigo if student_profile else request.user.username
            
            # Crear el documento para MongoDB
            new_plan = {
                "group": group_filter,
                "description": description,
                "activities": activities,
                "created_by": created_by,
                "created_at": datetime.now()
            }
            
            # Insertar en MongoDB
            result = evaluation_plans_collection.insert_one(new_plan)
            
            if result.inserted_id:
                messages.success(request, "Plan de evaluación creado exitosamente.")
                return redirect('evaluation_plan_detail', 
                               subject_code=subject_code, 
                               group_number=group_number, 
                               semester=semester)
            else:
                messages.error(request, "Error al guardar el plan en la base de datos.")
                
        except json.JSONDecodeError:
            messages.error(request, "Error en el formato de las actividades.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
    
    # GET request - mostrar formulario
    context = {
        'subject_code': subject_code,
        'group_number': group_number,
        'semester': semester,
        'group': group,
    }
    
    return render(request, 'create_evaluation_plan.html', context)

@login_required
@require_POST
def quick_create_plan(request):
    """
    Vista AJAX para crear rápidamente un plan desde la lista.
    """
    try:
        subject_code = request.POST.get('subject_code')
        group_number = int(request.POST.get('group_number'))
        semester = request.POST.get('semester')
        description = request.POST.get('description', '').strip()
        activities_json = request.POST.get('activities', '[]')
        activities = json.loads(activities_json)

        # Validaciones básicas
        if len(description) < 10:
            return JsonResponse({
                "success": False,
                "error": "La descripción debe tener al menos 10 caracteres."
            })

        # Verificar que el grupo existe
        try:
            group = Group.objects.get(
                subject_code=subject_code, 
                number=group_number, 
                semester=semester
            )
        except Group.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "El grupo especificado no existe."
            })

        # Verificar si ya existe un plan
        group_filter = {
            "subject_code": subject_code,
            "group_number": group_number,
            "semester": semester
        }
        
        existing_plan = evaluation_plans_collection.find_one({"group": group_filter})
        if existing_plan:
            return JsonResponse({
                "success": False,
                "error": "Ya existe un plan de evaluación para este grupo."
            })

        # Obtener código del perfil del usuario autenticado
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        created_by = student_profile.codigo if student_profile else request.user.username

        # Construir el documento
        new_plan = {
            "group": group_filter,
            "description": description,
            "activities": activities,
            "created_by": created_by,
            "created_at": datetime.now()
        }

        # Insertar en MongoDB
        result = evaluation_plans_collection.insert_one(new_plan)
        
        if result.inserted_id:
            return JsonResponse({
                "success": True,
                "message": "Plan creado correctamente",
                "redirect_url": f"/evaluation-plan/{subject_code}/{group_number}/{semester}/"
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "Error al guardar en la base de datos"
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Error en el formato de las actividades"
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        })



@login_required
@require_http_methods(["GET", "PATCH", "POST"])
def edit_evaluation_plan(request, subject_code, group_number, semester):
    """
    Vista para editar un plan de evaluación existente (PATCH parcial).
    """
    # Verificar que el grupo existe
    try:
        group = Group.objects.get(
            subject_code=subject_code, 
            number=group_number, 
            semester=semester
        )
    except Group.DoesNotExist:
        messages.error(request, "El grupo especificado no existe.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    evaluation_plan = get_collection('evaluation_plans').find_one({...})

    # Buscar el plan de evaluación en MongoDB
    group_filter = {
        "subject_code": subject_code,
        "group_number": int(group_number),
        "semester": semester
    }
    
    
    if not evaluation_plan:
        messages.error(request, "No existe un plan de evaluación para este grupo.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    # Verificar permisos de edición
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    student_id = student_profile.codigo if student_profile else request.user.username
    
    can_edit = (
        request.user.is_staff or 
        group.professor_id == request.user.username or
        evaluation_plan.get('created_by') == student_id
    )
    
    if not can_edit:
        return JsonResponse({
            "success": False,
            "error": "No tienes permisos para editar este plan de evaluación."
        }, status=403)
    
    if request.method in ['PATCH', 'POST']:
        try:
            # Determinar si es PATCH (actualización parcial) o POST (completa)
            is_patch = request.method == 'PATCH' or request.headers.get('X-HTTP-Method-Override') == 'PATCH'
            
            # Obtener datos del request
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            update_data = {}
            
            # Actualización parcial - solo campos enviados
            if is_patch:
                if 'description' in data:
                    update_data['description'] = data['description'].strip()
                
                if 'activities' in data:
                    activities = data['activities']
                    if isinstance(activities, str):
                        activities = json.loads(activities)
                    
                    # Validar actividades si se envían
                    if activities:
                        total_percentage = sum(activity.get('percentage', 0) for activity in activities)
                        if total_percentage != 100:
                            return JsonResponse({
                                "success": False,
                                "error": f"La suma de porcentajes debe ser 100%. Actualmente es {total_percentage}%."
                            })
                        
                        for i, activity in enumerate(activities):
                            if not activity.get('name', '').strip():
                                return JsonResponse({
                                    "success": False,
                                    "error": f"La actividad {i+1} debe tener un nombre."
                                })
                            
                            if not activity.get('percentage') or activity.get('percentage') <= 0:
                                return JsonResponse({
                                    "success": False,
                                    "error": f"La actividad '{activity.get('name')}' debe tener un porcentaje válido."
                                })
                    
                    update_data['activities'] = activities
            
            # Actualización completa - todos los campos requeridos
            else:
                description = data.get('description', '').strip()
                activities_json = data.get('activities', '[]')
                activities = json.loads(activities_json) if isinstance(activities_json, str) else activities_json
                
                # Validaciones completas
                if not activities:
                    return JsonResponse({
                        "success": False,
                        "error": "Debe tener al menos una actividad."
                    })
                
                total_percentage = sum(activity.get('percentage', 0) for activity in activities)
                if total_percentage != 100:
                    return JsonResponse({
                        "success": False,
                        "error": f"La suma de porcentajes debe ser 100%. Actualmente es {total_percentage}%."
                    })
                
                for i, activity in enumerate(activities):
                    if not activity.get('name', '').strip():
                        return JsonResponse({
                            "success": False,
                            "error": f"La actividad {i+1} debe tener un nombre."
                        })
                    
                    if not activity.get('percentage') or activity.get('percentage') <= 0:
                        return JsonResponse({
                            "success": False,
                            "error": f"La actividad '{activity.get('name')}' debe tener un porcentaje válido."
                        })
                
                update_data = {
                    "description": description,
                    "activities": activities
                }
            
            # Agregar metadatos de actualización
            update_data.update({
                "updated_at": datetime.datetime.now(),
                "updated_by": student_id
            })
            
            # Actualizar en MongoDB
            result = evaluation_plans_collection.update_one(
                {"group": group_filter},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return JsonResponse({
                    "success": True,
                    "message": "Plan de evaluación actualizado exitosamente.",
                    "updated_fields": list(update_data.keys())
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "No se realizaron cambios en el plan."
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Error en el formato de los datos."
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Error inesperado: {str(e)}"
            })
    
    # GET request - mostrar formulario con datos existentes
    context = {
        'subject_code': subject_code,
        'group_number': group_number,
        'semester': semester,
        'group': group,
        'evaluation_plan': evaluation_plan,
    }
    
    return render(request, 'edit_evaluation_plan.html', context)

@login_required
@require_POST
def delete_evaluation_plan(request, subject_code, group_number, semester):
    """
    Vista para eliminar un plan de evaluación completo.
    """
    # Verificar que el grupo existe
    try:
        group = Group.objects.get(
            subject_code=subject_code, 
            number=group_number, 
            semester=semester
        )
    except Group.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "El grupo especificado no existe."
        }, status=404)
    
    # Buscar el plan de evaluación en MongoDB
    group_filter = {
        "subject_code": subject_code,
        "group_number": int(group_number),
        "semester": semester
    }
    evaluation_plans_collection = get_collection('evaluation_plans')

    evaluation_plan = evaluation_plans_collection.find_one({"group": group_filter})
    if not evaluation_plan:
        return JsonResponse({
            "success": False,
            "error": "No existe un plan de evaluación para este grupo."
        }, status=404)
    
    # Verificar permisos
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    student_id = student_profile.codigo if student_profile else request.user.username
    
    can_delete = (
        request.user.is_staff or 
        group.professor_id == request.user.username or
        evaluation_plan.get('created_by') == student_id
    )
    
    if not can_delete:
        return JsonResponse({
            "success": False,
            "error": "No tienes permisos para eliminar este plan de evaluación."
        }, status=403)
    
    try:
        # Eliminar el plan de evaluación
        result = evaluation_plans_collection.delete_one({"group": group_filter})
        
        if result.deleted_count > 0:
            # También eliminar comentarios relacionados
            comments_collection.delete_many({"group": group_filter})
            
            return JsonResponse({
                "success": True,
                "message": "Plan de evaluación eliminado exitosamente."
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "No se pudo eliminar el plan."
            })
            
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        })

@login_required
@require_POST
def add_comment(request, subject_code, group_number, semester):
    """
    Vista para agregar un comentario a un plan de evaluación.
    """
    # Verificar que el grupo existe
    try:
        group = Group.objects.get(
            subject_code=subject_code, 
            number=group_number, 
            semester=semester
        )
    except Group.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "El grupo especificado no existe."
        }, status=404)
    
    # Buscar el plan de evaluación
    group_filter = {
        "subject_code": subject_code,
        "group_number": int(group_number),
        "semester": semester
    }
    evaluation_plans_collection = get_collection("evaluation_plans")
    evaluation_plan = evaluation_plans_collection.find_one({"group": group_filter})
    if not evaluation_plan:
        return JsonResponse({
            "success": False,
            "error": "No existe un plan de evaluación para este grupo."
        }, status=404)
    
    try:
        # Obtener datos del comentario
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            comment_text = data.get('comment', '').strip()
        else:
            comment_text = request.POST.get('comment', '').strip()
        
        # Validaciones
        if not comment_text:
            return JsonResponse({
                "success": False,
                "error": "El comentario no puede estar vacío."
            })
        
        if len(comment_text) < 5:
            return JsonResponse({
                "success": False,
                "error": "El comentario debe tener al menos 5 caracteres."
            })
        
        if len(comment_text) > 1000:
            return JsonResponse({
                "success": False,
                "error": "El comentario no puede exceder 1000 caracteres."
            })
        
        # Obtener información del usuario
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        created_by = student_profile.codigo if student_profile else request.user.username
        
        # Crear el documento del comentario
        new_comment = {
            "group": group_filter,
            "comment": comment_text,
            "created_by": created_by,
            "created_at": datetime.datetime.now()
        }
        
        # Insertar en MongoDB
        result = comments_collection.insert_one(new_comment)
        
        if result.inserted_id:
            # Obtener información del autor para la respuesta
            author_name = f"{request.user.first_name} {request.user.last_name}".strip()
            if not author_name:
                author_name = request.user.username
            
            return JsonResponse({
                "success": True,
                "message": "Comentario agregado exitosamente.",
                "comment": {
                    "id": str(result.inserted_id),
                    "comment": comment_text,
                    "author_name": author_name,
                    "created_at": new_comment["created_at"].isoformat(),
                    "created_by": created_by
                }
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "Error al guardar el comentario."
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Error en el formato de los datos."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        })

@login_required
@require_POST
def delete_comment(request, subject_code, group_number, semester, comment_id):
    """
    Vista para eliminar un comentario específico.
    """
    try:
        # Buscar el comentario
        comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
        if not comment:
            return JsonResponse({
                "success": False,
                "error": "El comentario no existe."
            }, status=404)
        
        # Verificar permisos (solo el autor o admin puede eliminar)
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        user_id = student_profile.codigo if student_profile else request.user.username
        
        can_delete = (
            request.user.is_staff or 
            comment.get('created_by') == user_id
        )
        
        if not can_delete:
            return JsonResponse({
                "success": False,
                "error": "No tienes permisos para eliminar este comentario."
            }, status=403)
        
        # Eliminar el comentario
        result = comments_collection.delete_one({"_id": ObjectId(comment_id)})
        
        if result.deleted_count > 0:
            return JsonResponse({
                "success": True,
                "message": "Comentario eliminado exitosamente."
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "No se pudo eliminar el comentario."
            })
            
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        })

@login_required
@require_POST
def quick_create_plan(request):
    """
    Vista AJAX para crear rápidamente un plan desde la lista.
    """
    try:
        subject_code = request.POST.get('subject_code')
        group_number = int(request.POST.get('group_number'))
        semester = request.POST.get('semester')
        description = request.POST.get('description', '').strip()
        activities_json = request.POST.get('activities', '[]')
        activities = json.loads(activities_json)

        # Validaciones básicas
        if len(description) < 10:
            return JsonResponse({
                "success": False,
                "error": "La descripción debe tener al menos 10 caracteres."
            })

        # Verificar que el grupo existe
        try:
            group = Group.objects.get(
                subject_code=subject_code, 
                number=group_number, 
                semester=semester
            )
        except Group.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "El grupo especificado no existe."
            })

        # Verificar si ya existe un plan
        group_filter = {
            "subject_code": subject_code,
            "group_number": group_number,
            "semester": semester
        }
        
        existing_plan = evaluation_plans_collection.find_one({"group": group_filter})
        if existing_plan:
            return JsonResponse({
                "success": False,
                "error": "Ya existe un plan de evaluación para este grupo."
            })

        # Obtener código del perfil del usuario autenticado
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        created_by = student_profile.codigo if student_profile else request.user.username

        # Construir el documento
        new_plan = {
            "group": group_filter,
            "description": description,
            "activities": activities,
            "created_by": created_by,
            "created_at": datetime.datetime.now()
        }

        # Insertar en MongoDB
        result = evaluation_plans_collection.insert_one(new_plan)
        
        if result.inserted_id:
            return JsonResponse({
                "success": True,
                "message": "Plan creado correctamente",
                "redirect_url": f"/evaluation-plan/{subject_code}/{group_number}/{semester}/"
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "Error al guardar en la base de datos"
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Error en el formato de las actividades"
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        })

@login_required
def add_activity(request, subject_code, group_number, semester):
    """
    Vista para agregar una nueva actividad a un plan existente.
    """
    # Verificar que el grupo existe
    try:
        group = Group.objects.get(
            subject_code=subject_code, 
            number=group_number, 
            semester=semester
        )
    except Group.DoesNotExist:
        messages.error(request, "El grupo especificado no existe.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    # Buscar el plan de evaluación
    group_filter = {
        "subject_code": subject_code,
        "group_number": int(group_number),
        "semester": semester
    }
    evaluation_plans_collection = get_collection('evaluation_plans')
    evaluation_plan = evaluation_plans_collection.find_one({"group": group_filter})
    if not evaluation_plan:
        messages.error(request, "No existe un plan de evaluación para este grupo.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    # Verificar permisos
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    student_id = student_profile.codigo if student_profile else request.user.username
    
    can_edit = (
        request.user.is_staff or 
        group.professor_id == request.user.username or
        evaluation_plan.get('created_by') == student_id
    )
    
    if not can_edit:
        messages.error(request, "No tienes permisos para editar este plan.")
        return redirect('evaluation_plan_detail', 
                       subject_code=subject_code, 
                       group_number=group_number, 
                       semester=semester)
    
    if request.method == 'POST':
        try:
            # Obtener datos de la nueva actividad
            name = request.POST.get('name', '').strip()
            activity_type = request.POST.get('activity_type', '').strip()
            percentage = float(request.POST.get('percentage', 0))
            description = request.POST.get('description', '').strip()
            
            # Validaciones
            if not name:
                messages.error(request, "El nombre de la actividad es obligatorio.")
                return render(request, 'add_activity.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                    'group': group,
                    'evaluation_plan': evaluation_plan,
                })
            
            if not activity_type:
                messages.error(request, "El tipo de actividad es obligatorio.")
                return render(request, 'add_activity.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                    'group': group,
                    'evaluation_plan': evaluation_plan,
                })
            
            if percentage <= 0:
                messages.error(request, "El porcentaje debe ser mayor a 0.")
                return render(request, 'add_activity.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                    'group': group,
                    'evaluation_plan': evaluation_plan,
                })
            
            # Verificar que no exceda el 100%
            current_total = sum(activity.get('percentage', 0) for activity in evaluation_plan.get('activities', []))
            if current_total + percentage > 100:
                messages.error(request, f"El porcentaje excede el límite. Total actual: {current_total}%, disponible: {100 - current_total}%")
                return render(request, 'add_activity.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                    'group': group,
                    'evaluation_plan': evaluation_plan,
                })
            
            # Crear nueva actividad
            new_activity = {
                "name": name,
                "activity_type": activity_type,
                "percentage": percentage,
                "description": description
            }
            
            # Agregar actividad al plan
            result = evaluation_plans_collection.update_one(
                {"group": group_filter},
                {
                    "$push": {"activities": new_activity},
                    "$set": {
                        "updated_at": datetime.datetime.now(),
                        "updated_by": student_id
                    }
                }
            )
            
            if result.modified_count > 0:
                messages.success(request, f"Actividad '{name}' agregada exitosamente.")
                return redirect('evaluation_plan_detail', 
                               subject_code=subject_code, 
                               group_number=group_number, 
                               semester=semester)
            else:
                messages.error(request, "No se pudo agregar la actividad.")
                
        except ValueError:
            messages.error(request, "El porcentaje debe ser un número válido.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
    
    # Calcular porcentaje disponible
    current_total = sum(activity.get('percentage', 0) for activity in evaluation_plan.get('activities', []))
    available_percentage = 100 - current_total
    
    context = {
        'subject_code': subject_code,
        'group_number': group_number,
        'semester': semester,
        'group': group,
        'evaluation_plan': evaluation_plan,
        'current_total': current_total,
        'available_percentage': available_percentage,
    }
    
    return render(request, 'add_activity.html', context)

@login_required
def edit_activity(request, subject_code, group_number, semester, activity_id):
    """
    Vista para editar una actividad específica del plan.
    """
    try:
        group = Group.objects.get(
            subject_code=subject_code, 
            number=group_number, 
            semester=semester
        )
    except Group.DoesNotExist:
        messages.error(request, "El grupo especificado no existe.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    evaluation_plans_collection = get_collection('evaluation_plans')

    group_filter = {
        "subject_code": subject_code,
        "group_number": int(group_number),
        "semester": semester
    }
    # Cambio aquí: variable con otro nombre para evitar conflicto con función
    plan_doc = evaluation_plans_collection.find_one({"group": group_filter})

    if not plan_doc:
        messages.error(request, "No existe un plan de evaluación para este grupo.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    activities = plan_doc.get('activities', [])
    if activity_id < 0 or activity_id >= len(activities):
        messages.error(request, "La actividad especificada no existe.")
        return redirect('evaluation_plan_detail', 
                        subject_code=subject_code, 
                        group_number=group_number, 
                        semester=semester)
    
    activity = activities[activity_id]
    
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    student_id = student_profile.codigo if student_profile else request.user.username
    
    can_edit = (
        request.user.is_staff or 
        group.professor_id == request.user.username or
        plan_doc.get('created_by') == student_id  # Aquí uso plan_doc, no evaluation_plan
    )
    
    if not can_edit:
        messages.error(request, "No tienes permisos para editar este plan.")
        return redirect('evaluation_plan_detail', 
                        subject_code=subject_code, 
                        group_number=group_number, 
                        semester=semester)
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            activity_type = request.POST.get('activity_type', '').strip()
            percentage = float(request.POST.get('percentage', 0))
            description = request.POST.get('description', '').strip()
            
            if not name:
                messages.error(request, "El nombre de la actividad es obligatorio.")
                return render(request, 'edit_activity.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                    'group': group,
                    'evaluation_plan': plan_doc,  # cambio aquí también
                    'activity': activity,
                    'activity_index': activity_id,
                })
            
            if not activity_type:
                messages.error(request, "El tipo de actividad es obligatorio.")
                return render(request, 'edit_activity.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                    'group': group,
                    'evaluation_plan': plan_doc,
                    'activity': activity,
                    'activity_index': activity_id,
                })
            
            if percentage <= 0:
                messages.error(request, "El porcentaje debe ser mayor a 0.")
                return render(request, 'edit_activity.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                    'group': group,
                    'evaluation_plan': plan_doc,
                    'activity': activity,
                    'activity_index': activity_id,
                })
            
            current_total = sum(act.get('percentage', 0) for i, act in enumerate(activities) if i != activity_id)
            if current_total + percentage > 100:
                available = 100 - current_total
                messages.error(request, f"El porcentaje excede el límite. Disponible: {available}%")
                return render(request, 'edit_activity.html', {
                    'subject_code': subject_code,
                    'group_number': group_number,
                    'semester': semester,
                    'group': group,
                    'evaluation_plan': plan_doc,
                    'activity': activity,
                    'activity_index': activity_id,
                })
            
            updated_activity = {
                "name": name,
                "activity_type": activity_type,
                "percentage": percentage,
                "description": description
            }
            
            result = evaluation_plans_collection.update_one(
                {"group": group_filter},
                {
                    "$set": {
                        f"activities.{activity_id}": updated_activity,
                        "updated_at": datetime.datetime.now(),
                        "updated_by": student_id
                    }
                }
            )
            
            if result.modified_count > 0:
                messages.success(request, f"Actividad '{name}' actualizada exitosamente.")
                return redirect('evaluation_plan_detail', 
                                subject_code=subject_code, 
                                group_number=group_number, 
                                semester=semester)
            else:
                messages.error(request, "No se pudo actualizar la actividad.")
                
        except ValueError:
            messages.error(request, "El porcentaje debe ser un número válido.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
    
    current_total = sum(act.get('percentage', 0) for i, act in enumerate(activities) if i != activity_id)
    available_percentage = 100 - current_total
    
    context = {
        'subject_code': subject_code,
        'group_number': group_number,
        'semester': semester,
        'group': group,
        'evaluation_plan': plan_doc,
        'activity': activity,
        'activity_index': activity_id,
        'current_total': current_total,
        'available_percentage': available_percentage,
    }
    
    return render(request, 'edit_activity.html', context)

@require_POST
@login_required
def delete_activity(request, subject_code, group_number, semester, activity_index):
    """
    Vista para eliminar una actividad específica del plan.
    """
    # Verificar que el grupo existe
    try:
        group = Group.objects.get(
            subject_code=subject_code, 
            number=group_number, 
            semester=semester
        )
    except Group.DoesNotExist:
        messages.error(request, "El grupo especificado no existe.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    evaluation_plans_collection = get_collection('evaluation_plans')

    # Buscar el plan de evaluación
    group_filter = {
        "subject_code": subject_code,
        "group_number": int(group_number),
        "semester": semester
    }
    plan_doc = evaluation_plans_collection.find_one({"group": group_filter})
    
    if not plan_doc:
        messages.error(request, "No existe un plan de evaluación para este grupo.")
        return redirect('evaluation_plans_list', subject_code=subject_code)
    
    # Verificar que el índice de actividad es válido
    activities = plan_doc.get('activities', [])
    
    if activity_index < 0 or activity_index >= len(activities):
        messages.error(request, "La actividad especificada no existe.")
        return redirect('evaluation_plan_detail', 
                       subject_code=subject_code, 
                       group_number=group_number, 
                       semester=semester)
    
    activity = activities[activity_index]
    
    # Verificar permisos
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    student_id = student_profile.codigo if student_profile else request.user.username
    
    can_edit = (
        request.user.is_staff or 
        group.professor_id == request.user.username or
        plan_doc.get('created_by') == student_id
    )
    
    if not can_edit:
        messages.error(request, "No tienes permisos para editar este plan.")
        return redirect('evaluation_plan_detail', 
                       subject_code=subject_code, 
                       group_number=group_number, 
                       semester=semester)
    
    if request.method == 'POST':
        try:
            # Eliminar actividad del array
            result = evaluation_plans_collection.update_one(
                {"group": group_filter},
                {
                    "$unset": {f"activities.{activity_index}": 1},
                    "$set": {
                        "updated_at": datetime.datetime.now(),
                        "updated_by": student_id
                    }
                }
            )
            
            # Limpiar elementos null del array
            evaluation_plans_collection.update_one(
                {"group": group_filter},
                {"$pull": {"activities": None}}
            )
            
            if result.modified_count > 0:
                messages.success(request, f"Actividad '{activity.get('name')}' eliminada exitosamente.")
            else:
                messages.error(request, "No se pudo eliminar la actividad.")
                
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
        
        return redirect('evaluation_plan_detail', 
                       subject_code=subject_code, 
                       group_number=group_number, 
                       semester=semester)
    
    context = {
        'subject_code': subject_code,
        'group_number': group_number,
        'semester': semester,
        'group': group,
        'evaluation_plan': plan_doc,
        'activity': activity,
        'activity_index': activity_index,
    }
    
    return render(request, 'delete_activity.html', context)


@login_required
def evaluation_plan_detail(request, subject_code, group_number, semester):
    """
    Vista para mostrar el detalle de un plan de evaluación específico.
    """
    # Obtener el grupo desde PostgreSQL
    try:
        group = Group.objects.get(
            subject_code=subject_code, 
            number=group_number, 
            semester=semester
        )
    except Group.DoesNotExist:
        raise Http404("Grupo no encontrado")
    
    # Buscar el plan de evaluación en MongoDB
    group_filter = {
        "subject_code": subject_code,
        "group_number": int(group_number),
        "semester": semester
    }
    
    evaluation_plan = evaluation_plans_collection.find_one({"group": group_filter})
    
    if not evaluation_plan:
        # Si no existe plan, redirigir a crear uno
        messages.info(request, "Este grupo no tiene un plan de evaluación. ¿Te gustaría crear uno?")
        return redirect('create_evaluation_plan', 
                       subject_code=subject_code, 
                       group_number=group_number, 
                       semester=semester)
    
    # Obtener actividades del plan
    activities = evaluation_plan.get('activities', [])
    
    # Calcular el porcentaje total
    total_percentage = sum(activity.get('percentage', 0) for activity in activities)
    
    # Obtener comentarios relacionados con este plan
    comments = list(comments_collection.find({"group": group_filter}).sort("created_at", -1))
    
    # Enriquecer comentarios con información del usuario
    for comment in comments:
        # Intentar obtener información del estudiante
        try:
            student_profile = StudentProfile.objects.get(codigo=comment.get('created_by'))
            comment['author_name'] = f"{student_profile.user.first_name} {student_profile.user.last_name}".strip()
            if not comment['author_name']:
                comment['author_name'] = student_profile.user.username
        except StudentProfile.DoesNotExist:
            comment['author_name'] = comment.get('created_by', 'Usuario desconocido')
    
    # Verificar si el usuario puede editar el plan
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    student_id = student_profile.codigo if student_profile else request.user.username
    
    can_edit_plan = (
        request.user.is_staff or 
        group.professor_id == request.user.username or
        (evaluation_plan.get('created_by') == student_id)
    )
    
    # Obtener información del profesor
    professor = group.get_professor()
    
    # Obtener calificaciones si el usuario está inscrito
    user_grades = None
    if student_profile:
        user_grades = grades_collection.find_one({
            "student_id": student_profile.codigo,
            "group": group_filter
        })
    
    context = {
        'subject_code': subject_code,
        'group_number': group_number,
        'semester': semester,
        'group': group,
        'professor': professor,
        'evaluation_plan': evaluation_plan,
        'activities': activities,
        'comments': comments,
        'total_percentage': total_percentage,
        'can_edit_plan': can_edit_plan,
        'user_grades': user_grades,
        'is_complete': total_percentage == 100,
        'remaining_percentage': 100 - total_percentage,
    }
    
    return render(request, 'evaluation_plan_detail.html', context)
