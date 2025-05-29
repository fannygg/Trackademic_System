from django.urls import path
from .views import GradesView
from . import views



urlpatterns = [
    path('grades/', GradesView.as_view(), name='grades'),
    path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/',
     views.evaluation_plan,
     name='evaluation_plan_detail'
    ),
    path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/',
     views.evaluation_plan,
     name='edit_evaluation_plan'
    ),
    path('edit-evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/',
     views.edit_evaluation_plan,
     name='edit_evaluation_plan'
    ),
    #Comentarios
    path('add-comment/<str:subject_code>/<int:group_number>/<str:semester>/',
     views.add_comment,
     name='add_comment'
    ),
    # Gestión de actividades
    
    #path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/add-activity/', 
    #     views.add_activity, name='add_activity'),
    #path('activity/<int:activity_id>/edit/', 
     #    views.edit_activity, name='edit_activity'),
    #path('activity/<int:activity_id>/delete/', 
     #    views.delete_activity, name='delete_activity'),
    # Crear plan de evaluación
    # Crear nuevo plan
    #path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/create/', 
     #    views.create_evaluation_plan, name='create_evaluation_plan'),
    

]
