from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name="Usuario")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono / WhatsApp")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    comuna = models.CharField(max_length=100, blank=True, verbose_name="Comuna")
    region = models.CharField(max_length=100, default='Región Metropolitana', blank=True, verbose_name="Región")

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"

    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name() or self.usuario.username}"


@receiver(post_save, sender=User)
def crear_o_guardar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
    else:
        if hasattr(instance, 'perfil'):
            instance.perfil.save()
