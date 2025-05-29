from django.urls import path
from .views import GradesView
from . import views



urlpatterns = [
    path('grades/', GradesView.as_view(), name='grades'),
    path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/',
     views.evaluation_plan,
     name='evaluation_plan_detail'
    ),
    path('evaluation-plans-list/<str:subject_code>/', 
     views.evaluation_plans_list, 
     name='evaluation_plans_list'),
    

    path('edit-evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/',
     views.edit_evaluation_plan,
     name='edit_evaluation_plan'
    ),
    #Comentarios
    path('add-comment/<str:subject_code>/<int:group_number>/<str:semester>/',
     views.add_comment,
     name='add_comment'
    ),

    # Crear nuevo plan
    path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/create/', 
     views.create_evaluation_plan, name='create_evaluation_plan'),
    # quick
    path('quick-create-plan/', views.quick_create_plan, name='quick_create_plan'),
    
    ## # Editar plan existente (PATCH parcial)
    path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/edit/', 
         views.edit_evaluation_plan, name='edit_evaluation_plan'),
    
    # Eliminar plan
    path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/delete/', 
         views.delete_evaluation_plan, name='delete_evaluation_plan'),
    
    # Comentarios
    path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/add-comment/', 
         views.add_comment, name='add_comment'),
    
    path('comment/<str:comment_id>/delete/', 
         views.delete_comment, name='delete_comment'),

    path('add-activity/<str:subject_code>/<int:group_number>/<str:semester>/',
         views.add_activity, name='add_activity'),
    
    path('edit-activity/<str:subject_code>/<int:group_number>/<str:semester>/<int:activity_id>/',
            views.edit_activity, name='edit_activity'
         ),
    path('delete-activity/<str:subject_code>/<int:group_number>/<str:semester>/<int:activity_index>/',
         views.delete_activity, name='delete_activity'),
    
    path('evaluation-plan/<str:subject_code>/<int:group_number>/<str:semester>/', 
         views.evaluation_plan_detail, 
         name='evaluation_plan_detail')
]
