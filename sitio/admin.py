from django.contrib import admin
from .models import ConfiguracionSitio, MensajeContacto


@admin.register(ConfiguracionSitio)
class ConfiguracionSitioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'whatsapp', 'correo', 'comuna', 'ciudad')

    def has_add_permission(self, request):
        # Permite crear sólo si no existe ninguna instancia (Singleton)
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'asunto', 'leido', 'fecha')
    list_filter = ('leido', 'fecha')
    search_fields = ('nombre', 'correo', 'asunto', 'mensaje')
    list_editable = ('leido',)
    readonly_fields = ('fecha',)
