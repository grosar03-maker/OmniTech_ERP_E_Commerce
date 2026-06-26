"""
OmniTech Forms
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import UserProfile


class UserRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre de usuario'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Correo electrónico'})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirmar contraseña'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password2'):
            raise ValidationError('Las contraseñas no coinciden.')


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Contraseña'}))


class CheckoutForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Correo electrónico'}), required=False
    )

    REGIONES = [
        ('', 'Selecciona tu región'),
        ('La Araucanía', 'La Araucanía (Subsidio disponible)'),
        ('Metropolitana', 'Región Metropolitana'),
        ('Valparaíso', 'Valparaíso'),
        ('Biobío', 'Biobío'),
        ('Maule', 'Maule'),
        ('Ñuble', 'Ñuble'),
        ('Los Ríos', 'Los Ríos'),
        ('Los Lagos', 'Los Lagos'),
        ('Aysén', 'Aysén'),
        ('Magallanes', 'Magallanes'),
        ('Antofagasta', 'Antofagasta'),
        ('Atacama', 'Atacama'),
        ('Coquimbo', 'Coquimbo'),
        ('O Higgins', "O'Higgins"),
        ('Arica y Parinacota', 'Arica y Parinacota'),
        ('Tarapacá', 'Tarapacá'),
    ]

    region = forms.ChoiceField(choices=REGIONES, widget=forms.Select(attrs={'class': 'form-input'}))
    direccion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Dirección de envío', 'rows': 3}),
        required=False,
    )
    observaciones = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-input', 'placeholder': 'Observaciones adicionales (opcional)', 'rows': 2}
        ),
        required=False,
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['rut', 'telefono', 'region', 'ciudad', 'direccion', 'newsletter']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '12.345.678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+56 9 1234 5678'}),
            'region': forms.TextInput(attrs={'class': 'form-input'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ciudad'}),
            'direccion': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'newsletter': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
