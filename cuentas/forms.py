from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Perfil


class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="Nombre")
    last_name = forms.CharField(max_length=50, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo electrónico")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono / WhatsApp")
    direccion = forms.CharField(max_length=255, required=False, label="Dirección (calle y número)")
    comuna = forms.CharField(max_length=100, required=False, label="Comuna")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = "Letras, números y @/./+/-/_ únicamente."

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con este correo electrónico.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            perfil, _ = Perfil.objects.get_or_create(usuario=user)
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.direccion = self.cleaned_data.get('direccion', '')
            perfil.comuna = self.cleaned_data.get('comuna', '')
            perfil.save()
        return user


class IniciarSesionForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tu nombre de usuario',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tu contraseña',
        })


class EditarPerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, label="Nombre")
    last_name = forms.CharField(max_length=50, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo electrónico")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono / WhatsApp")
    direccion = forms.CharField(max_length=255, required=False, label="Dirección")
    comuna = forms.CharField(max_length=100, required=False, label="Comuna")
    region = forms.CharField(max_length=100, required=False, label="Región")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'perfil'):
            self.fields['telefono'].initial = self.instance.perfil.telefono
            self.fields['direccion'].initial = self.instance.perfil.direccion
            self.fields['comuna'].initial = self.instance.perfil.comuna
            self.fields['region'].initial = self.instance.perfil.region
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit and hasattr(user, 'perfil'):
            perfil = user.perfil
            perfil.telefono = self.cleaned_data['telefono']
            perfil.direccion = self.cleaned_data['direccion']
            perfil.comuna = self.cleaned_data['comuna']
            perfil.region = self.cleaned_data['region']
            perfil.save()
        return user
