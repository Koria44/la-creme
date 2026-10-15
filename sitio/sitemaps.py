from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from catalogo.models import Categoria, Producto


class EstaticasSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            'sitio:inicio',
            'catalogo:lista',
            'sitio:nosotros',
            'sitio:ubicacion',
            'sitio:contacto',
            'sitio:preguntas_frecuentes',
            'sitio:terminos',
            'sitio:privacidad',
        ]

    def location(self, item):
        return reverse(item)


class CategoriaSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Categoria.objects.filter(activa=True)


class ProductoSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return Producto.objects.filter(activo=True)

    def lastmod(self, obj):
        return obj.fecha_creacion
