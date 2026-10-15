from sitio.models import ConfiguracionSitio
from catalogo.models import Categoria


def sitio_context(request):
    """
    Expone la configuración general del sitio y las categorías activas
    para el navbar, footer y SEO en todas las páginas.
    """
    try:
        configuracion = ConfiguracionSitio.get_solo()
    except Exception:
        configuracion = None

    try:
        categorias = Categoria.objects.filter(activa=True).order_by('orden', 'nombre')
    except Exception:
        categorias = []

    return {
        'configuracion_sitio': configuracion,
        'categorias_menu': categorias,
    }
