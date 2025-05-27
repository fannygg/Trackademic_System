from django.urls import path
from .views import RegisterView, CustomAuthToken, login_view, register_view, home, profile

from django.contrib.auth import views as auth_views


urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('api/login/', CustomAuthToken.as_view(), name='custom_login'),
    # Frontend HTML views
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', login_view, name='profile'),  
    path('home/', home, name='home'),
    ## Dashboard-related paths
    path('grades/', profile, name='grades'),  
    path('subjects/', profile, name='subjects'),
    path('settings/', profile, name='settings'),
    path('calendar/', profile, name='calendar'),
    path('calculator/', profile, name='calculator'),
    path('reports/', profile, name='reports'),
    path('plans/', profile, name='plans'),
    path('collaboration/', profile, name='collaboration'),
    ## Profile-related paths
    path('edit_profile/', profile, name='edit_profile'),
    path('academic_history/', profile, name='academic_history'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='change_password.html'), name='change_password'),
    path('export_data/', profile, name='export_data'),
    path('privacy_settings/', profile, name='privacy_settings'),
]
