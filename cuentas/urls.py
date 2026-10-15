from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('ingresar/', views.IngresarView.as_view(), name='ingresar'),
    path('salir/', views.SalirView.as_view(), name='salir'),
    path('mi-perfil/', views.MiPerfilView.as_view(), name='mi_perfil'),
    path('mis-pedidos/', views.MisPedidosView.as_view(), name='mis_pedidos'),
    path('mis-pedidos/<int:pk>/', views.DetallePedidoView.as_view(), name='pedido_detalle'),

    # Flujo de recuperación de contraseña con correo por consola
    path(
        'recuperar-contrasena/',
        auth_views.PasswordResetView.as_view(
            template_name='cuentas/recuperar_contrasena.html',
            email_template_name='cuentas/emails/recuperar_contrasena_email.html',
            subject_template_name='cuentas/emails/recuperar_contrasena_asunto.txt',
            success_url=reverse_lazy('cuentas:password_reset_done'),
        ),
        name='recuperar_contrasena'
    ),
    path(
        'recuperar-contrasena/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='cuentas/recuperar_contrasena_enviado.html'
        ),
        name='password_reset_done'
    ),
    path(
        'recuperar-contrasena/confirmar/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='cuentas/recuperar_contrasena_confirmar.html',
            success_url=reverse_lazy('cuentas:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'recuperar-contrasena/completado/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='cuentas/recuperar_contrasena_completo.html'
        ),
        name='password_reset_complete'
    ),
]
