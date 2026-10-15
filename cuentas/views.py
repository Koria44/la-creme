from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from pedidos.models import Pedido
from .forms import RegistroUsuarioForm, IniciarSesionForm, EditarPerfilForm


class RegistroView(View):
    template_name = 'cuentas/registro.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('sitio:inicio')
        form = RegistroUsuarioForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('sitio:inicio')
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"¡Bienvenido(a) a LA CREME, {user.first_name}! Tu cuenta ha sido creada exitosamente."
            )
            return redirect('sitio:inicio')
        messages.error(request, "Por favor corrige los errores indicados en el formulario de registro.")
        return render(request, self.template_name, {'form': form})


class IngresarView(LoginView):
    template_name = 'cuentas/ingresar.html'
    authentication_form = IniciarSesionForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"¡Hola de nuevo, {form.get_user().first_name or form.get_user().username}! Has iniciado sesión.")
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return next_url
        if self.request.user.is_staff:
            return reverse_lazy('panel:dashboard')
        return reverse_lazy('sitio:inicio')


class SalirView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente. ¡Esperamos verte pronto en LA CREME!")
        return redirect('sitio:inicio')

    def get(self, request):
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente. ¡Esperamos verte pronto en LA CREME!")
        return redirect('sitio:inicio')


class MiPerfilView(LoginRequiredMixin, View):
    template_name = 'cuentas/mi_perfil.html'

    def get(self, request):
        form = EditarPerfilForm(instance=request.user)
        ultimos_pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:3]
        return render(request, self.template_name, {
            'form': form,
            'ultimos_pedidos': ultimos_pedidos,
        })

    def post(self, request):
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos de perfil han sido actualizados con éxito.")
            return redirect('cuentas:mi_perfil')
        messages.error(request, "Por favor revisa los errores en tus datos.")
        ultimos_pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:3]
        return render(request, self.template_name, {
            'form': form,
            'ultimos_pedidos': ultimos_pedidos,
        })


class MisPedidosView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'cuentas/mis_pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).order_by('-fecha_creacion')


class DetallePedidoView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'cuentas/pedido_detalle.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).prefetch_related('items__producto')
