from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil de Cliente'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_telefono', 'get_comuna')

    def get_telefono(self, instance):
        return getattr(instance.perfil, 'telefono', '')
    get_telefono.short_description = 'Teléfono'

    def get_comuna(self, instance):
        return getattr(instance.perfil, 'comuna', '')
    get_comuna.short_description = 'Comuna'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'comuna', 'region')
    search_fields = ('usuario__username', 'usuario__email', 'telefono', 'comuna')
    list_filter = ('comuna', 'region')
