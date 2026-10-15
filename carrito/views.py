from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from catalogo.models import Producto
from sitio.models import ConfiguracionSitio
from .cart import Carrito


class CarritoDetalleView(View):
    def get(self, request):
        carrito = Carrito(request)
        configuracion = ConfiguracionSitio.get_solo()
        whatsapp_mensaje = carrito.obtener_mensaje_whatsapp(configuracion)
        telefono_limpio = configuracion.whatsapp.replace('+', '').replace(' ', '').replace('-', '')
        whatsapp_url = f"https://wa.me/{telefono_limpio}?text={whatsapp_mensaje}"

        context = {
            'carrito': carrito,
            'whatsapp_url': whatsapp_url,
            'configuracion': configuracion,
        }
        return render(request, 'carrito/detalle.html', context)


class CarritoAgregarView(View):
    def post(self, request, producto_id):
        carrito = Carrito(request)
        producto = get_object_or_404(Producto, id=producto_id, activo=True)

        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (ValueError, TypeError):
            cantidad = 1

        if cantidad < 1:
            cantidad = 1

        resultado = carrito.agregar(producto=producto, cantidad=cantidad)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')

        if is_ajax:
            return JsonResponse({
                'success': resultado['success'],
                'mensaje': resultado['mensaje'],
                'cantidad': resultado['cantidad'],
                'total_items': len(carrito),
                'total_precio': carrito.get_total_precio(),
                'producto_nombre': producto.nombre,
            })

        if resultado['success']:
            messages.success(request, resultado['mensaje'])
        else:
            messages.warning(request, resultado['mensaje'])

        siguiente = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'carrito:detalle'
        return redirect(siguiente)


class CarritoActualizarView(View):
    def post(self, request, producto_id):
        carrito = Carrito(request)
        producto = get_object_or_404(Producto, id=producto_id, activo=True)

        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (ValueError, TypeError):
            cantidad = 1

        if cantidad <= 0:
            carrito.eliminar(producto)
            resultado = {
                'success': True,
                'mensaje': f'Se eliminó "{producto.nombre}" del carrito.',
                'cantidad': 0,
            }
        else:
            resultado = carrito.agregar(producto=producto, cantidad=cantidad, override_cantidad=True)

        subtotal = producto.precio_final * resultado['cantidad']
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')

        if is_ajax:
            return JsonResponse({
                'success': resultado['success'],
                'mensaje': resultado['mensaje'],
                'cantidad': resultado['cantidad'],
                'subtotal': subtotal,
                'total_items': len(carrito),
                'total_precio': carrito.get_total_precio(),
                'producto_id': producto.id,
            })

        messages.info(request, resultado['mensaje'])
        return redirect('carrito:detalle')


class CarritoEliminarView(View):
    def post(self, request, producto_id):
        carrito = Carrito(request)
        producto = get_object_or_404(Producto, id=producto_id)
        carrito.eliminar(producto)

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
        if is_ajax:
            return JsonResponse({
                'success': True,
                'mensaje': f'"{producto.nombre}" fue eliminado del carrito.',
                'total_items': len(carrito),
                'total_precio': carrito.get_total_precio(),
                'producto_id': producto.id,
            })

        messages.info(request, f'"{producto.nombre}" fue eliminado de tu carrito.')
        return redirect('carrito:detalle')


class CarritoVaciarView(View):
    def post(self, request):
        carrito = Carrito(request)
        carrito.vaciar()
        messages.info(request, 'Tu carrito de compras ha sido vaciado.')
        return redirect('carrito:detalle')
