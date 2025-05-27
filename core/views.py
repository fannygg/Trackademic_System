from django.shortcuts import render, redirect
from .forms import RegisterForm
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import RegisterSerializer


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # o tu dashboard
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