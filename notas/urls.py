from django.urls import path
from .views import GradesView


urlpatterns = [
    path('grades/', GradesView.as_view(), name='grades'),

]
