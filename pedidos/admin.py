from django.contrib import admin
from .models import Pedido, ItemPedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('nombre_producto', 'precio_unitario', 'cantidad', 'subtotal')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'telefono',
        'tipo_entrega',
        'fecha_entrega',
        'metodo_pago',
        'estado',
        'total',
        'fecha_creacion'
    )
    list_filter = ('estado', 'tipo_entrega', 'metodo_pago', 'fecha_creacion', 'fecha_entrega')
    search_fields = ('id', 'nombre', 'correo', 'telefono', 'direccion')
    list_editable = ('estado',)
    inlines = [ItemPedidoInline]
    date_hierarchy = 'fecha_creacion'


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'nombre_producto', 'precio_unitario', 'cantidad', 'subtotal')
    list_filter = ('pedido__estado',)
    search_fields = ('nombre_producto', 'pedido__id', 'pedido__nombre')
