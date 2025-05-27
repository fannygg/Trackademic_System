from django.contrib.auth.models import User
from django import forms

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    codigo = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            user.profile.codigo = self.cleaned_data['codigo']
            user.profile.save()

        return user