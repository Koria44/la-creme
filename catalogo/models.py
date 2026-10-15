from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True, verbose_name="Imagen")
    activa = models.BooleanField(default=True, verbose_name="¿Activa?")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('catalogo:categoria_detalle', kwargs={'slug': self.slug})


class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='productos',
        verbose_name="Categoría"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre del producto")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="Slug")
    descripcion_corta = models.CharField(
        max_length=300,
        verbose_name="Descripción corta",
        help_text="Resumen llamativo para tarjetas de producto (máx 300 caracteres)"
    )
    descripcion_larga = models.TextField(
        verbose_name="Descripción detallada",
        help_text="Ingredientes, elaboración, conservación y recomendaciones de servicio"
    )
    precio = models.PositiveIntegerField(verbose_name="Precio normal (CLP)")
    precio_oferta = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Precio oferta (CLP)",
        help_text="Opcional. Si se define y es menor al precio normal, se mostrará tachado el normal."
    )
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name="Imagen del producto"
    )
    stock = models.PositiveIntegerField(default=10, verbose_name="Stock disponible")
    activo = models.BooleanField(default=True, verbose_name="¿Activo para la venta?")
    destacado = models.BooleanField(default=False, verbose_name="¿Producto destacado?")
    tamano_porciones = models.CharField(
        max_length=120,
        default="12 a 16 porciones (22 cm)",
        verbose_name="Tamaño / Porciones",
        help_text="Ej: 15-20 porciones / 24 cm de diámetro / Formato individual"
    )
    tiempo_preparacion = models.CharField(
        max_length=120,
        default="24 a 48 horas de anticipación",
        verbose_name="Tiempo de preparación",
        help_text="Anticipación recomendada para realizar el pedido"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        ordering = ['-destacado', '-fecha_creacion']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            counter = 1
            while Producto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('catalogo:producto_detalle', kwargs={'slug': self.slug})

    @property
    def precio_final(self):
        if self.precio_oferta and self.precio_oferta < self.precio:
            return self.precio_oferta
        return self.precio

    @property
    def tiene_descuento(self):
        return bool(self.precio_oferta and self.precio_oferta < self.precio)

    @property
    def porcentaje_descuento(self):
        if self.tiene_descuento:
            descuento = (self.precio - self.precio_oferta) / self.precio * 100
            return round(descuento)
        return 0

    @property
    def disponible(self):
        return self.activo and self.stock > 0

    @property
    def esta_agotado(self):
        return self.stock <= 0

    @property
    def stock_bajo(self):
        return 0 < self.stock <= 4
