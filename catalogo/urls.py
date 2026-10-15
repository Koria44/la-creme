from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='lista'),
    path('categoria/<slug:slug>/', views.CategoriaDetailView.as_view(), name='categoria_detalle'),
    path('<slug:slug>/', views.ProductoDetailView.as_view(), name='producto_detalle'),
]
