from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Productos
    path('productos/', views.ProductoListView.as_view(), name='productos'),
    path('productos/crear/', views.ProductoCreateView.as_view(), name='producto_crear'),
    path('productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_eliminar'),

    # Stock
    path('stock/', views.StockListView.as_view(), name='stock'),
    path('stock/ajuste-rapido/', views.AjusteStockRapidoView.as_view(), name='stock_ajuste_rapido'),

    # Categorías
    path('categorias/', views.CategoriaListView.as_view(), name='categorias'),
    path('categorias/crear/', views.CategoriaCreateView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_eliminar'),

    # Pedidos
    path('pedidos/', views.PedidoListView.as_view(), name='pedidos'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detalle'),
    path('pedidos/<int:pk>/cambiar-estado/', views.PedidoCambiarEstadoView.as_view(), name='pedido_cambiar_estado'),

    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='clientes'),

    # Mensajes de contacto
    path('mensajes/', views.MensajeListView.as_view(), name='mensajes'),
    path('mensajes/<int:pk>/marcar-leido/', views.MensajeMarcarLeidoView.as_view(), name='mensaje_marcar_leido'),

    # Configuración del sitio
    path('configuracion/', views.ConfiguracionSitioUpdateView.as_view(), name='configuracion'),
]
