from django.urls import path
from . import views

app_name = 'sitio'

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path('nosotros/', views.NosotrosView.as_view(), name='nosotros'),
    path('contacto/', views.ContactoView.as_view(), name='contacto'),
    path('ubicacion/', views.UbicacionView.as_view(), name='ubicacion'),
    path('preguntas-frecuentes/', views.PreguntasFrecuentesView.as_view(), name='preguntas_frecuentes'),
    path('terminos-y-condiciones/', views.TerminosCondicionesView.as_view(), name='terminos'),
    path('politica-de-privacidad/', views.PoliticaPrivacidadView.as_view(), name='privacidad'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
