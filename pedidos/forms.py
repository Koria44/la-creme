from django import forms
from django.utils import timezone
from .models import Pedido


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'nombre',
            'correo',
            'telefono',
            'tipo_entrega',
            'direccion',
            'comuna',
            'fecha_entrega',
            'hora_entrega',
            'metodo_pago',
            'notas',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre y apellido', 'required': True}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.cl', 'required': True}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678', 'required': True}),
            'tipo_entrega': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle, número, depto / casa'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Providencia, Las Condes, Ñuñoa...'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'hora_entrega': forms.Select(
                choices=[
                    ('Mañana (10:00 - 13:00 hrs)', 'Mañana (10:00 a 13:00 hrs)'),
                    ('Tarde (14:00 - 18:00 hrs)', 'Tarde (14:00 a 18:00 hrs)'),
                    ('Vespertino (18:00 - 20:00 hrs)', 'Vespertino (18:00 a 20:00 hrs)'),
                ],
                attrs={'class': 'form-select'}
            ),
            'metodo_pago': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '¿Deseas una dedicatoria o indicaciones para la entrega? Escríbela aquí.'
            }),
        }
        labels = {
            'nombre': 'Nombre completo',
            'correo': 'Correo electrónico',
            'telefono': 'Teléfono o WhatsApp',
            'tipo_entrega': 'Modalidad de entrega',
            'direccion': 'Dirección (obligatorio para despacho)',
            'comuna': 'Comuna',
            'fecha_entrega': 'Fecha requerida',
            'hora_entrega': 'Horario preferente',
            'metodo_pago': 'Forma de pago',
            'notas': 'Notas adicionales / Mensaje en tarjeta',
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_entrega = cleaned_data.get('tipo_entrega')
        direccion = cleaned_data.get('direccion')
        comuna = cleaned_data.get('comuna')
        fecha_entrega = cleaned_data.get('fecha_entrega')

        if tipo_entrega == 'despacho':
            if not direccion:
                self.add_error('direccion', 'Para despacho a domicilio debes ingresar una dirección válida.')
            if not comuna:
                self.add_error('comuna', 'Debes indicar la comuna para coordinar el despacho.')

        if fecha_entrega:
            hoy = timezone.localdate()
            if fecha_entrega < hoy:
                self.add_error('fecha_entrega', 'La fecha de entrega no puede ser anterior a hoy.')

        return cleaned_data
