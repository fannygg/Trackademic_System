from django.urls import path
from .views import RegisterView, CustomAuthToken, login_view, register_view


urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('api/login/', CustomAuthToken.as_view(), name='custom_login'),
    # Frontend HTML views
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),

]
