from django import forms
from .models import MensajeContacto, ConfiguracionSitio


class MensajeContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'correo', 'telefono', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Andrea Muñoz',
                'required': True,
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'nombre@ejemplo.cl',
                'required': True,
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678',
            }),
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Cotización torta matrimonio / Consulta stock',
                'required': True,
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos qué necesitas (fechas, porciones, detalles especiales)...',
                'required': True,
            }),
        }
        labels = {
            'nombre': 'Nombre completo',
            'correo': 'Correo electrónico',
            'telefono': 'Teléfono o WhatsApp (opcional)',
            'asunto': 'Asunto',
            'mensaje': 'Mensaje o detalle de tu pedido',
        }


class ConfiguracionSitioForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSitio
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'eslogan': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'horarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'costo_despacho_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'despacho_gratis_desde': forms.NumberInput(attrs={'class': 'form-control'}),
        }
