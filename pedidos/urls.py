from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('finalizar-compra/', views.CheckoutView.as_view(), name='checkout'),
    path('pedido-confirmado/<int:pedido_id>/', views.PedidoConfirmadoView.as_view(), name='confirmado'),
]
