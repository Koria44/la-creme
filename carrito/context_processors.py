from .cart import Carrito


def carrito_context(request):
    """
    Expone el objeto Carrito en todas las plantillas.
    """
    return {
        'carrito': Carrito(request)
    }
