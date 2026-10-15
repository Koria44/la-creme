from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.http import HttpResponse

from catalogo.models import Categoria, Producto
from .forms import MensajeContactoForm
from .models import ConfiguracionSitio


class InicioView(TemplateView):
    template_name = 'sitio/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias_destacadas'] = Categoria.objects.filter(activa=True)[:6]
        context['productos_destacados'] = (
            Producto.objects.filter(activo=True, destacado=True)
            .select_related('categoria')[:8]
        )
        context['ultimas_novedades'] = (
            Producto.objects.filter(activo=True)
            .select_related('categoria')
            .order_by('-fecha_creacion')[:4]
        )
        return context


class NosotrosView(TemplateView):
    template_name = 'sitio/nosotros.html'


class ContactoView(View):
    template_name = 'sitio/contacto.html'

    def get(self, request):
        form = MensajeContactoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = MensajeContactoForm(request.POST)
        if form.is_valid():
            mensaje = form.save()
            messages.success(
                request,
                f"¡Gracias, {mensaje.nombre}! Hemos recibido tu mensaje correctamente. "
                "Te responderemos a la brevedad."
            )
            return redirect('sitio:contacto')
        messages.error(request, "Por favor corrige los campos indicados en el formulario.")
        return render(request, self.template_name, {'form': form})


class UbicacionView(TemplateView):
    template_name = 'sitio/ubicacion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MensajeContactoForm()
        return context


class PreguntasFrecuentesView(TemplateView):
    template_name = 'sitio/preguntas_frecuentes.html'


class TerminosCondicionesView(TemplateView):
    template_name = 'sitio/terminos.html'


class PoliticaPrivacidadView(TemplateView):
    template_name = 'sitio/privacidad.html'


def robots_txt(request):
    """
    Genera el archivo robots.txt dinámicamente bloqueando panel, admin, carrito y cuentas.
    """
    lineas = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /panel/",
        "Disallow: /carrito/",
        "Disallow: /cuentas/",
        "Disallow: /finalizar-compra/",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lineas), content_type="text/plain; charset=utf-8")


def error_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def error_500_view(request):
    return render(request, '500.html', status=500)
