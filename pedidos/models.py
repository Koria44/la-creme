from django.db import models
from django.contrib.auth.models import User
from catalogo.models import Producto


class Pedido(models.Model):
    TIPO_ENTREGA_CHOICES = [
        ('retiro', 'Retiro en tienda (Providencia)'),
        ('despacho', 'Despacho a domicilio'),
    ]

    METODO_PAGO_CHOICES = [
        ('transferencia', 'Transferencia bancaria previa'),
        ('efectivo', 'Efectivo o tarjeta al retirar en tienda'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de pago / confirmación'),
        ('confirmado', 'Confirmado'),
        ('en_preparacion', 'En preparación'),
        ('listo', 'Listo para retiro / despacho'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
        verbose_name="Usuario registrado"
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre completo")
    correo = models.EmailField(verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=25, verbose_name="Teléfono de contacto")
    tipo_entrega = models.CharField(
        max_length=20,
        choices=TIPO_ENTREGA_CHOICES,
        default='retiro',
        verbose_name="Tipo de entrega"
    )
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección de entrega")
    comuna = models.CharField(max_length=100, blank=True, verbose_name="Comuna de entrega")
    fecha_entrega = models.DateField(verbose_name="Fecha deseada de entrega / retiro")
    hora_entrega = models.CharField(
        max_length=80,
        blank=True,
        default="Tarde (14:00 - 18:00 hrs)",
        verbose_name="Rango horario preferido"
    )
    notas = models.TextField(blank=True, verbose_name="Dedicatoria o instrucciones especiales")
    metodo_pago = models.CharField(
        max_length=25,
        choices=METODO_PAGO_CHOICES,
        default='transferencia',
        verbose_name="Método de pago"
    )
    estado = models.CharField(
        max_length=25,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado del pedido"
    )
    total = models.PositiveIntegerField(default=0, verbose_name="Total en CLP")
    costo_envio = models.PositiveIntegerField(default=0, verbose_name="Costo de envío en CLP")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id:05d} - {self.nombre} (${self.total:,} CLP)"

    @property
    def total_con_envio(self):
        return self.total + self.costo_envio

    @property
    def badge_class(self):
        mapping = {
            'pendiente': 'warning text-dark',
            'confirmado': 'info text-dark',
            'en_preparacion': 'primary',
            'listo': 'secondary',
            'entregado': 'success',
            'cancelado': 'danger',
        }
        return mapping.get(self.estado, 'light text-dark')


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items', verbose_name="Pedido")
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_pedido',
        verbose_name="Producto"
    )
    nombre_producto = models.CharField(max_length=200, verbose_name="Nombre del producto")
    precio_unitario = models.PositiveIntegerField(verbose_name="Precio unitario (CLP)")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    subtotal = models.PositiveIntegerField(verbose_name="Subtotal (CLP)")

    class Meta:
        verbose_name = "Ítem de pedido"
        verbose_name_plural = "Ítems de pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto} (${self.subtotal:,} CLP)"
