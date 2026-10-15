from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
import json

from catalogo.models import Producto, Categoria
from pedidos.models import Pedido, ItemPedido
from sitio.models import MensajeContacto, ConfiguracionSitio
from sitio.forms import ConfiguracionSitioForm
from .forms import ProductoForm, CategoriaForm, CambiarEstadoPedidoForm


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class DashboardView(View):
    template_name = 'panel/dashboard.html'

    def get(self, request):
        ahora = timezone.localtime()
        inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Ventas del día (pedidos no cancelados)
        ventas_hoy = Pedido.objects.filter(
            fecha_creacion__gte=inicio_hoy
        ).exclude(estado='cancelado').aggregate(total=Sum('total'))['total'] or 0

        # Ventas del mes
        ventas_mes = Pedido.objects.filter(
            fecha_creacion__gte=inicio_mes
        ).exclude(estado='cancelado').aggregate(total=Sum('total'))['total'] or 0

        # Pedidos pendientes
        pedidos_pendientes_cant = Pedido.objects.filter(estado='pendiente').count()

        # Productos con stock bajo (<= 4) o agotados
        productos_stock_bajo_cant = Producto.objects.filter(stock__lte=4, activo=True).count()

        # Nuevos clientes del mes
        nuevos_clientes_cant = User.objects.filter(
            date_joined__gte=inicio_mes,
            is_staff=False
        ).count()

        # Gráfico: Ventas de los últimos 30 días
        fechas_grafico = []
        ventas_grafico = []
        pedidos_grafico = []

        hace_30_dias = ahora.date() - timezone.timedelta(days=29)
        pedidos_ultimos_dias = Pedido.objects.filter(
            fecha_creacion__date__gte=hace_30_dias
        ).exclude(estado='cancelado')

        for i in range(30):
            dia = hace_30_dias + timezone.timedelta(days=i)
            pedidos_dia = [p for p in pedidos_ultimos_dias if p.fecha_creacion.date() == dia]
            fechas_grafico.append(dia.strftime('%d/%m'))
            ventas_grafico.append(sum(p.total for p in pedidos_dia))
            pedidos_grafico.append(len(pedidos_dia))

        # Productos más vendidos
        top_productos = (
            ItemPedido.objects.filter(pedido__estado__in=['confirmado', 'en_preparacion', 'listo', 'entregado'])
            .values('nombre_producto')
            .annotate(total_unidades=Sum('cantidad'), total_recaudado=Sum('subtotal'))
            .order_by('-total_unidades')[:5]
        )

        # Últimos 6 pedidos
        ultimos_pedidos = Pedido.objects.order_by('-fecha_creacion')[:6]

        # Mensajes sin leer
        mensajes_pendientes = MensajeContacto.objects.filter(leido=False).count()

        context = {
            'ventas_hoy': ventas_hoy,
            'ventas_mes': ventas_mes,
            'pedidos_pendientes_cant': pedidos_pendientes_cant,
            'productos_stock_bajo_cant': productos_stock_bajo_cant,
            'nuevos_clientes_cant': nuevos_clientes_cant,
            'fechas_grafico_json': json.dumps(fechas_grafico),
            'ventas_grafico_json': json.dumps(ventas_grafico),
            'pedidos_grafico_json': json.dumps(pedidos_grafico),
            'top_productos': top_productos,
            'ultimos_pedidos': ultimos_pedidos,
            'mensajes_pendientes': mensajes_pendientes,
        }
        return render(request, self.template_name, context)


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class ProductoListView(ListView):
    model = Producto
    template_name = 'panel/producto_lista.html'
    context_object_name = 'productos'
    paginate_by = 15

    def get_queryset(self):
        qs = Producto.objects.select_related('categoria').order_by('-fecha_creacion')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(categoria__nombre__icontains=q))

        cat = self.request.GET.get('categoria')
        if cat and cat.isdigit():
            qs = qs.filter(categoria_id=int(cat))

        estado = self.request.GET.get('estado')
        if estado == 'activos':
            qs = qs.filter(activo=True)
        elif estado == 'inactivos':
            qs = qs.filter(activo=False)

        filtro_stock = self.request.GET.get('stock')
        if filtro_stock == 'bajo':
            qs = qs.filter(stock__lte=4, stock__gt=0)
        elif filtro_stock == 'agotado':
            qs = qs.filter(stock=0)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['q'] = self.request.GET.get('q', '')
        context['cat_seleccionada'] = self.request.GET.get('categoria', '')
        context['estado_seleccionado'] = self.request.GET.get('estado', '')
        context['stock_seleccionado'] = self.request.GET.get('stock', '')
        return context


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'panel/producto_form.html'
    success_url = reverse_lazy('panel:productos')

    def form_valid(self, form):
        messages.success(self.request, f'Producto "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'panel/producto_form.html'
    success_url = reverse_lazy('panel:productos')

    def form_valid(self, form):
        messages.success(self.request, f'Producto "{form.instance.nombre}" actualizado correctamente.')
        return super().form_valid(form)


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'panel/producto_confirmar_eliminar.html'
    success_url = reverse_lazy('panel:productos')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        nombre = obj.nombre
        messages.success(request, f'Producto "{nombre}" eliminado con éxito.')
        return super().delete(request, *args, **kwargs)


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class StockListView(ListView):
    model = Producto
    template_name = 'panel/stock_lista.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Producto.objects.select_related('categoria').order_by('stock', 'nombre')


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class AjusteStockRapidoView(View):
    def post(self, request):
        producto_id = request.POST.get('producto_id')
        nuevo_stock = request.POST.get('stock')

        try:
            producto = get_object_or_404(Producto, id=producto_id)
            stock_int = max(0, int(nuevo_stock))
            producto.stock = stock_int
            producto.save()

            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'nuevo_stock': producto.stock,
                    'mensaje': f'Stock de "{producto.nombre}" actualizado a {producto.stock} unidades.',
                    'esta_agotado': producto.esta_agotado,
                    'stock_bajo': producto.stock_bajo,
                })

            messages.success(request, f'Stock de "{producto.nombre}" actualizado a {producto.stock}.')
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'mensaje': str(e)}, status=400)
            messages.error(request, f'Error al actualizar stock: {e}')

        return redirect('panel:stock')


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class CategoriaListView(ListView):
    model = Categoria
    template_name = 'panel/categoria_lista.html'
    context_object_name = 'categorias'


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'panel/categoria_form.html'
    success_url = reverse_lazy('panel:categorias')

    def form_valid(self, form):
        messages.success(self.request, f'Categoría "{form.instance.nombre}" creada correctamente.')
        return super().form_valid(form)


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'panel/categoria_form.html'
    success_url = reverse_lazy('panel:categorias')

    def form_valid(self, form):
        messages.success(self.request, f'Categoría "{form.instance.nombre}" actualizada correctamente.')
        return super().form_valid(form)


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = 'panel/categoria_confirmar_eliminar.html'
    success_url = reverse_lazy('panel:categorias')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        nombre = obj.nombre
        messages.success(request, f'Categoría "{nombre}" eliminada.')
        return super().delete(request, *args, **kwargs)


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class PedidoListView(ListView):
    model = Pedido
    template_name = 'panel/pedido_lista.html'
    context_object_name = 'pedidos'
    paginate_by = 15

    def get_queryset(self):
        qs = Pedido.objects.prefetch_related('items').order_by('-fecha_creacion')
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(correo__icontains=q) |
                Q(telefono__icontains=q) |
                Q(id__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_actual'] = self.request.GET.get('estado', '')
        context['q'] = self.request.GET.get('q', '')
        context['estados_choices'] = Pedido.ESTADO_CHOICES
        return context


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class PedidoDetailView(DetailView):
    model = Pedido
    template_name = 'panel/pedido_detalle.html'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_estado'] = CambiarEstadoPedidoForm(instance=self.object)
        return context


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class PedidoCambiarEstadoView(View):
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido #{pedido.id:05d} cambiado a "{pedido.get_estado_display()}".')
        else:
            messages.error(request, 'Estado no válido.')
        return redirect('panel:pedido_detalle', pk=pk)


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class ClienteListView(ListView):
    model = User
    template_name = 'panel/cliente_lista.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        return (
            User.objects.filter(is_staff=False)
            .select_related('perfil')
            .annotate(
                total_pedidos=Count('pedidos'),
                total_gastado=Sum('pedidos__total', filter=~Q(pedidos__estado='cancelado'))
            )
            .order_by('-date_joined')
        )


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class MensajeListView(ListView):
    model = MensajeContacto
    template_name = 'panel/mensaje_lista.html'
    context_object_name = 'mensajes_contacto'
    paginate_by = 15


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class MensajeMarcarLeidoView(View):
    def post(self, request, pk):
        mensaje = get_object_or_404(MensajeContacto, pk=pk)
        mensaje.leido = not mensaje.leido
        mensaje.save()
        estado = "leído" if mensaje.leido else "no leído"
        messages.info(request, f'Mensaje marcado como {estado}.')
        return redirect('panel:mensajes')


@method_decorator(staff_member_required(login_url='cuentas:ingresar'), name='dispatch')
class ConfiguracionSitioUpdateView(View):
    template_name = 'panel/configuracion_form.html'

    def get(self, request):
        config = ConfiguracionSitio.get_solo()
        form = ConfiguracionSitioForm(instance=config)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        config = ConfiguracionSitio.get_solo()
        form = ConfiguracionSitioForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'La configuración de la pastelería ha sido actualizada correctamente.')
            return redirect('panel:configuracion')
        messages.error(request, 'Por favor corrige los errores indicados en el formulario.')
        return render(request, self.template_name, {'form': form})
