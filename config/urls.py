"""
URL configuration for the LA CREME project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from sitio.sitemaps import EstaticasSitemap, CategoriaSitemap, ProductoSitemap

sitemaps = {
    'estaticas': EstaticasSitemap,
    'categorias': CategoriaSitemap,
    'productos': ProductoSitemap,
}

urlpatterns = [
    # Panel Django Admin estándar
    path('admin/', admin.site.urls),

    # Panel de administración propio para staff
    path('panel/', include('panel.urls')),

    # Cuentas de usuario
    path('cuentas/', include('cuentas.urls')),

    # Carrito de compras
    path('carrito/', include('carrito.urls')),

    # Pedidos y checkout
    path('', include('pedidos.urls')),

    # Catálogo de productos
    path('productos/', include('catalogo.urls')),

    # Sitio institucional, páginas legales y portada
    path('', include('sitio.urls')),

    # Mapa del sitio para SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Servir archivos estáticos y subidas en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Vistas personalizadas de error en español
handler404 = 'sitio.views.error_404_view'
handler500 = 'sitio.views.error_500_view'
