from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Categoria, Producto


class ProductoListView(ListView):
    model = Producto
    template_name = 'catalogo/producto_lista.html'
    context_object_name = 'productos'
    paginate_by = 9

    def get_queryset(self):
        qs = Producto.objects.filter(activo=True).select_related('categoria')

        # Filtro de búsqueda
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(descripcion_corta__icontains=q) |
                Q(descripcion_larga__icontains=q) |
                Q(categoria__nombre__icontains=q)
            )

        # Filtro de categoría
        cat_slug = self.request.GET.get('categoria', '').strip()
        if cat_slug:
            qs = qs.filter(categoria__slug=cat_slug)

        # Filtro de precio
        precio_min = self.request.GET.get('precio_min')
        precio_max = self.request.GET.get('precio_max')
        if precio_min and precio_min.isdigit():
            qs = qs.filter(precio__gte=int(precio_min))
        if precio_max and precio_max.isdigit():
            qs = qs.filter(precio__lte=int(precio_max))

        # Ordenamiento
        orden = self.request.GET.get('orden', 'destacados')
        if orden == 'precio_asc':
            qs = qs.order_by('precio')
        elif orden == 'precio_desc':
            qs = qs.order_by('-precio')
        elif orden == 'nombre_asc':
            qs = qs.order_by('nombre')
        elif orden == 'novedades':
            qs = qs.order_by('-fecha_creacion')
        else: # 'destacados' por defecto
            qs = qs.order_by('-destacado', '-fecha_creacion')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.filter(activa=True)
        context['categoria_actual'] = self.request.GET.get('categoria', '')
        context['query_actual'] = self.request.GET.get('q', '')
        context['precio_min_actual'] = self.request.GET.get('precio_min', '')
        context['precio_max_actual'] = self.request.GET.get('precio_max', '')
        context['orden_actual'] = self.request.GET.get('orden', 'destacados')
        context['total_resultados'] = self.get_queryset().count()
        return context


class CategoriaDetailView(DetailView):
    model = Categoria
    template_name = 'catalogo/categoria_detalle.html'
    context_object_name = 'categoria'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categoria = self.object
        productos = categoria.productos.filter(activo=True)

        # Orden
        orden = self.request.GET.get('orden', 'destacados')
        if orden == 'precio_asc':
            productos = productos.order_by('precio')
        elif orden == 'precio_desc':
            productos = productos.order_by('-precio')
        elif orden == 'nombre_asc':
            productos = productos.order_by('nombre')
        elif orden == 'novedades':
            productos = productos.order_by('-fecha_creacion')
        else:
            productos = productos.order_by('-destacado', '-fecha_creacion')

        context['productos'] = productos
        context['orden_actual'] = orden
        context['otras_categorias'] = Categoria.objects.filter(activa=True).exclude(pk=categoria.pk)
        return context


class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'catalogo/producto_detalle.html'
    context_object_name = 'producto'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Producto.objects.filter(activo=True).select_related('categoria')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = self.object
        context['productos_relacionados'] = (
            Producto.objects.filter(categoria=producto.categoria, activo=True)
            .exclude(pk=producto.pk)[:4]
        )
        return context
