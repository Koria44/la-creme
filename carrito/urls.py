from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.CarritoDetalleView.as_view(), name='detalle'),
    path('agregar/<int:producto_id>/', views.CarritoAgregarView.as_view(), name='agregar'),
    path('actualizar/<int:producto_id>/', views.CarritoActualizarView.as_view(), name='actualizar'),
    path('eliminar/<int:producto_id>/', views.CarritoEliminarView.as_view(), name='eliminar'),
    path('vaciar/', views.CarritoVaciarView.as_view(), name='vaciar'),
]
