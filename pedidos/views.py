from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from carrito.cart import Carrito
from sitio.models import ConfiguracionSitio
from .models import Pedido, ItemPedido
from .forms import CheckoutForm


class CheckoutView(View):
    template_name = 'pedidos/checkout.html'

    def get(self, request):
        carrito = Carrito(request)
        if len(carrito) == 0:
            messages.warning(request, "Tu carrito está vacío. Agrega productos para iniciar la compra.")
            return redirect('catalogo:lista')

        initial_data = {}
        if request.user.is_authenticated:
            initial_data['nombre'] = request.user.get_full_name() or request.user.username
            initial_data['correo'] = request.user.email
            if hasattr(request.user, 'perfil'):
                initial_data['telefono'] = request.user.perfil.telefono
                initial_data['direccion'] = request.user.perfil.direccion
                initial_data['comuna'] = request.user.perfil.comuna

        # Por defecto fecha mínima mañana
        manana = timezone.localdate() + timezone.timedelta(days=1)
        initial_data['fecha_entrega'] = manana

        form = CheckoutForm(initial=initial_data)
        configuracion = ConfiguracionSitio.get_solo()

        context = {
            'form': form,
            'carrito': carrito,
            'configuracion': configuracion,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        carrito = Carrito(request)
        if len(carrito) == 0:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('catalogo:lista')

        form = CheckoutForm(request.POST)
        configuracion = ConfiguracionSitio.get_solo()

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Verificar stock antes de confirmar
                    for item in carrito:
                        prod = item['producto']
                        if prod.stock < item['cantidad']:
                            messages.error(
                                request,
                                f"Lo sentimos, no hay stock suficiente para '{prod.nombre}'. "
                                f"Stock disponible: {prod.stock}."
                            )
                            return render(request, self.template_name, {
                                'form': form,
                                'carrito': carrito,
                                'configuracion': configuracion,
                            })

                    # Calcular costo de envío si aplica despacho
                    tipo_entrega = form.cleaned_data['tipo_entrega']
                    subtotal_productos = carrito.get_total_precio()
                    costo_envio = 0
                    if tipo_entrega == 'despacho':
                        if subtotal_productos < configuracion.despacho_gratis_desde:
                            costo_envio = configuracion.costo_despacho_base

                    pedido = form.save(commit=False)
                    if request.user.is_authenticated:
                        pedido.usuario = request.user
                        # Guardar datos en perfil si estaban vacíos
                        if hasattr(request.user, 'perfil'):
                            perfil = request.user.perfil
                            if not perfil.telefono:
                                perfil.telefono = form.cleaned_data['telefono']
                            if not perfil.direccion and form.cleaned_data.get('direccion'):
                                perfil.direccion = form.cleaned_data['direccion']
                            if not perfil.comuna and form.cleaned_data.get('comuna'):
                                perfil.comuna = form.cleaned_data['comuna']
                            perfil.save()

                    pedido.total = subtotal_productos
                    pedido.costo_envio = costo_envio
                    pedido.save()

                    # Crear items y descontar stock
                    for item in carrito:
                        prod = item['producto']
                        ItemPedido.objects.create(
                            pedido=pedido,
                            producto=prod,
                            nombre_producto=prod.nombre,
                            precio_unitario=item['precio'],
                            cantidad=item['cantidad'],
                            subtotal=item['subtotal']
                        )
                        prod.stock -= item['cantidad']
                        prod.save()

                    # Vaciar carrito de sesión
                    carrito.vaciar()

                    # Enviar correo de confirmación (consola en demo)
                    asunto = f"Confirmación de Pedido #{pedido.id:05d} - LA CREME Pastelería"
                    cuerpo = (
                        f"¡Hola {pedido.nombre}!\n\n"
                        f"Hemos recibido tu pedido #{pedido.id:05d} con éxito.\n"
                        f"Tipo de entrega: {pedido.get_tipo_entrega_display()}\n"
                        f"Fecha deseada: {pedido.fecha_entrega} ({pedido.hora_entrega})\n"
                        f"Total a pagar: ${pedido.total_con_envio:,} CLP\n"
                        f"Método de pago: {pedido.get_metodo_pago_display()}\n\n"
                        f"Nos pondremos en contacto contigo vía WhatsApp o correo para coordinar los detalles.\n\n"
                        f"¡Gracias por preferir LA CREME!"
                    )
                    try:
                        send_mail(
                            asunto,
                            cuerpo,
                            settings.DEFAULT_FROM_EMAIL,
                            [pedido.correo],
                            fail_silently=True,
                        )
                    except Exception:
                        pass

                    messages.success(request, f"¡Tu pedido #{pedido.id:05d} ha sido generado exitosamente!")
                    return redirect('pedidos:confirmado', pedido_id=pedido.id)

            except Exception as e:
                messages.error(request, f"Ocurrió un error al procesar tu pedido: {e}")
        else:
            messages.error(request, "Por favor revisa los errores en el formulario de compra.")

        return render(request, self.template_name, {
            'form': form,
            'carrito': carrito,
            'configuracion': configuracion,
        })


class PedidoConfirmadoView(View):
    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedido.objects.prefetch_related('items'), id=pedido_id)
        configuracion = ConfiguracionSitio.get_solo()
        return render(request, 'pedidos/pedido_confirmado.html', {
            'pedido': pedido,
            'configuracion': configuracion,
        })
