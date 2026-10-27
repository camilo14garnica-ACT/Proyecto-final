from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Mascota, Especie, Raza
from .forms import EspecieForm, MascotaForm
from .permisos import es_personal, solo_admin
from django.views.decorators.http import require_http_methods

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView


def mascotas_visible(usuario):
    mascotas = Mascota.objects.select_related('Cliente', 'especie', 'raza')
    if es_personal(usuario):
        return mascotas
    return mascotas.filter(Cliente=usuario)


@login_required
def lista_mascotas(request):
    mascotas = mascotas_visible(request.user)
    return render(request, 'mascotas/lista_mascotas.html', {'mascotas': mascotas})

@login_required
def registrar_mascota(request):

    form = MascotaForm(request.POST or None, usuario=request.user)

    if request.method == 'POST' and form.is_valid():

        mascota = form.save(commit=False)

        # Si es cliente, se asigna como propietario automáticamente.
        if request.user.rol == 'CLIENTE':
            mascota.Cliente = request.user

        mascota.save()

        messages.success(
            request,
            'Mascota registrada correctamente.'
        )

        return redirect('lista_mascotas')

    return render(
        request,
        'mascotas/mascota_form.html',
        {'form': form}
    )
@login_required
def editar_mascota(request, pk):
    mascota = get_object_or_404(
        mascotas_visible(request.user),
        pk=pk
    )
    
    form = MascotaForm(
        request.POST or None,
        instance=mascota,
        usuario=request.user
    )
    
    if request.method == 'POST' and form.is_valid():
        mascota = form.save(commit=False)
        
        #El cliente conserva la propiedad de su mascota
        if not es_personal(request.user):
            mascota.Cliente = request.user
        
        mascota.save()
        
        messages.success(
            request,
            'Mascota actualizada correctamente.'
        )
        
        return redirect('lista_mascotas')
    return render(
        request,
        'mascotas/mascota_form.html',
        {
            'form': form,
            'titulo': 'Editar mascota'
        }
    )

@login_required
@require_http_methods(["GET", "POST"])
def eliminar_mascota(request, pk):
    mascota = get_object_or_404(
        mascotas_visible(request.user),
        pk=pk
    )
    if request.method == 'POST':
        nombre = mascota.nombre
        mascota.delete()
        
        messages.success(
            request,
            f'la mascota {nombre} fue eliminada correctamente.'
        )
        
        return redirect('lista_mascotas')
    return render(
        request,
        'mascotas/confirmar_eliminacion_mascota.html',
        {'mascota': mascota}
    )

@login_required
def razas_por_especie(request, especie_id):
    razas = Raza.objects.filter(especie_id=especie_id, estado='ACTIVO').order_by('nombre')
    return JsonResponse({'razas': [{'id': r.id, 'nombre': r.nombre} for r in razas]})




#PERMISOS PARA EL CRUD DE ESPECIES
class PersonalAutorizadoMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.rol in ['ADMIN', 'VETERINARIO']
    
    def handle_no_permission(self):
        if not self.request.user.is_aunthenticated:
            return super().handle_no_permission()
        
        messages.error(
            self.request,
            'No tienes permisos para gestionar especies'
        )
        return redirect('inicio')
    

# VISTA PARA LISTAR ESPECIES
class ListarEspecieView(PersonalAutorizadoMixin, ListView):
    model = Especie
    template_name = 'especies/lista_especies.html'
    context_object_name = 'especies'
    ordering = ['nombre']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de especies'
        return context


# VISTA PARA CREAR ESPECIES
class CrearEspecieView(PersonalAutorizadoMixin, CreateView):
    model = Especie
    form_class = EspecieForm
    template_name = 'especies/especie_form.html'
    success_url = reverse_lazy('lista_especies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar especie'
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            'Especie registrada correctamente.'
        )
        return super().form_valid(form)


# VISTA PARA EDITAR ESPECIES
class EditarEspecieView(PersonalAutorizadoMixin, UpdateView):
    model = Especie
    form_class = EspecieForm
    template_name = 'especies/especie_form.html'
    success_url = reverse_lazy('lista_especies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar especie'
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            'Especie actualizada correctamente.'
        )
        return super().form_valid(form)


# VISTA PARA ELIMINAR ESPECIES
class EliminarEspeciesView(PersonalAutorizadoMixin, DeleteView):
    model = Especie
    template_name = 'especies/confirmar_eliminacion_especie.html'
    context_object_name = 'especie'
    success_url = reverse_lazy('lista_especies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar especie'
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            'Especie eliminada correctamente.'
        )
        return super().form_valid(form)
    
# Create your views here.


# ============================================================
# CARRITO DE COMPRAS
# ============================================================
from .models import Producto, Carrito, ItemCarrito

@login_required
def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito del usuario"""
    producto = get_object_or_404(Producto, pk=producto_id, estado='ACTIVO')
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    if not creado:
        item.cantidad += 1
        item.save()

    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'mi_perfil'))


@login_required
def quitar_del_carrito(request, item_id):
    """Elimina un ítem del carrito"""
    item = get_object_or_404(ItemCarrito, pk=item_id, carrito__usuario=request.user)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')


@login_required
def ver_carrito(request):
    """Muestra el carrito del usuario"""
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    productos  = Producto.objects.filter(estado='ACTIVO')
    return render(request, 'mascotas/carrito.html', {
        'carrito': carrito,
        'productos': productos,
    })


@login_required
def pagar_carrito(request):
    """Procesa el pago del carrito (simulado)"""
    carrito = get_object_or_404(Carrito, usuario=request.user)
    if carrito.cantidad_items() == 0:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('ver_carrito')

    # Simulación de pago exitoso — aquí iría la pasarela real
    carrito.items.all().delete()
    messages.success(request, '¡Compra realizada con éxito! Pronto recibirás tu pedido.')
    return redirect('mi_perfil')
