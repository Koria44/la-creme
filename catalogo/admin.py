from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'activa', 'orden')
    list_filter = ('activa',)
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('activa', 'orden')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'categoria',
        'precio',
        'precio_oferta',
        'stock',
        'activo',
        'destacado',
        'fecha_creacion'
    )
    list_filter = ('activo', 'destacado', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion_corta', 'descripcion_larga')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('precio', 'precio_oferta', 'stock', 'activo', 'destacado')
