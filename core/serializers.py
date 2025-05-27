from django.contrib.auth.models import User
from rest_framework import serializers
from .models import StudentProfile

class RegisterSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'codigo')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        print("Validated data:", validated_data)
        codigo = validated_data.pop('codigo')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # Asegurarse de no duplicar el perfil si ya existe
        if not hasattr(user, 'profile'):
            StudentProfile.objects.create(user=user, codigo=codigo)
        return user


