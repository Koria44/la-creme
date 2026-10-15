from django.db import models


class ConfiguracionSitio(models.Model):
    nombre = models.CharField(max_length=120, default="LA CREME Pastelería", verbose_name="Nombre de la pastelería")
    eslogan = models.CharField(
        max_length=250,
        default="Pastelería artesanal hecha con amor, tradición y los mejores ingredientes.",
        verbose_name="Eslogan o frase principal"
    )
    direccion = models.CharField(
        max_length=255,
        default="Av. Providencia 1234, Local 5",
        verbose_name="Dirección física (Placeholder editable)"
    )
    comuna = models.CharField(max_length=100, default="Providencia", verbose_name="Comuna")
    ciudad = models.CharField(max_length=100, default="Santiago", verbose_name="Ciudad")
    telefono = models.CharField(max_length=30, default="+56 9 8765 4321", verbose_name="Teléfono fijo o móvil")
    whatsapp = models.CharField(
        max_length=30,
        default="+56987654321",
        verbose_name="Número de WhatsApp (con código de país, ej: +56987654321)"
    )
    correo = models.EmailField(default="contacto@pastelerialacreme.cl", verbose_name="Correo de contacto")
    horarios = models.TextField(
        default="Lunes a Sábado: 09:30 a 20:00 hrs.\nDomingos y festivos: 10:00 a 18:00 hrs.",
        verbose_name="Horarios de atención"
    )
    instagram = models.URLField(
        default="https://www.instagram.com/pasteleria_la_creme/",
        verbose_name="Enlace de Instagram"
    )
    facebook = models.URLField(
        blank=True,
        default="https://facebook.com/pasteleria_la_creme",
        verbose_name="Enlace de Facebook"
    )
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=-33.428500,
        verbose_name="Latitud (para Google Maps)"
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=-70.612300,
        verbose_name="Longitud (para Google Maps)"
    )
    costo_despacho_base = models.PositiveIntegerField(
        default=3990,
        verbose_name="Costo base de despacho (CLP)"
    )
    despacho_gratis_desde = models.PositiveIntegerField(
        default=45000,
        verbose_name="Monto para despacho gratis (CLP)"
    )

    class Meta:
        verbose_name = "Configuración del sitio"
        verbose_name_plural = "Configuración del sitio"

    def __str__(self):
        return f"Configuración: {self.nombre}"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=120, verbose_name="Nombre completo")
    correo = models.EmailField(verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=30, blank=True, verbose_name="Teléfono")
    asunto = models.CharField(max_length=150, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje o cotización")
    leido = models.BooleanField(default=False, verbose_name="¿Leído por administración?")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de envío")

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self):
        return f"{self.nombre} - {self.asunto} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"
