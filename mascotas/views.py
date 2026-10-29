from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .models import Mascota, Especie, Raza
from .forms import EspecieForm, MascotaForm, RazaForm
from .permisos import es_personal

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def razas_por_especie(request, especie_id):
    razas = Raza.objects.filter(especie_id=especie_id, estado='ACTIVO').order_by('nombre')
    return JsonResponse({'razas': [{'id': r.id, 'nombre': r.nombre} for r in razas]})




# Permisos para gestionar especies y razas
class PersonalAutorizadoMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('login')

    def test_func(self):
        return es_personal(self.request.user)
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        
        messages.error(
            self.request,
            'No tienes permisos para gestionar este módulo.'
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
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Especie eliminada correctamente.'
        )
        return response

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                request,
                'No se puede eliminar esta especie porque tiene razas o mascotas asociadas.'
            )
            return redirect(self.success_url)


class PersonalMascotasMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('login')

    def test_func(self):
        usuario = self.request.user
        return es_personal(usuario) or usuario.rol == 'CLIENTE'

    def get_queryset(self):
        mascotas = Mascota.objects.select_related(
            'Cliente', 'especie', 'raza'
        )
        if es_personal(self.request.user):
            return mascotas
        return mascotas.filter(Cliente=self.request.user)


class ListaMascotasView(PersonalMascotasMixin, ListView):
    model = Mascota
    template_name = 'mascotas/lista_mascotas.html'
    context_object_name = 'mascotas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_personal'] = es_personal(self.request.user)
        context['titulo'] = (
            'Gestión de mascotas'
            if context['es_personal']
            else 'Mis mascotas'
        )
        return context


class FormularioMascotaMixin(PersonalMascotasMixin):
    model = Mascota
    form_class = MascotaForm
    template_name = 'mascotas/mascota_form.html'
    success_url = reverse_lazy('lista_mascotas')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not es_personal(self.request.user):
            form.instance.Cliente = self.request.user
        messages.success(self.request, self.mensaje_exito)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.titulo
        context['es_personal'] = es_personal(self.request.user)
        return context


class CrearMascotaView(FormularioMascotaMixin, CreateView):
    mensaje_exito = 'Mascota registrada correctamente.'
    titulo = 'Registrar mascota'


class EditarMascotaView(FormularioMascotaMixin, UpdateView):
    mensaje_exito = 'Mascota actualizada correctamente.'
    titulo = 'Editar mascota'


class EliminarMascotaView(PersonalMascotasMixin, DeleteView):
    model = Mascota
    template_name = 'mascotas/confirmar_eliminacion_mascota.html'
    context_object_name = 'mascota'
    success_url = reverse_lazy('lista_mascotas')

    def form_valid(self, form):
        messages.success(self.request, 'Mascota eliminada correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_personal'] = es_personal(self.request.user)
        return context


class ListaRazasView(PersonalAutorizadoMixin, ListView):
    model = Raza
    template_name = 'razas/lista_razas.html'
    context_object_name = 'razas'
    queryset = Raza.objects.select_related('especie').order_by(
        'especie__nombre', 'nombre'
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de razas'
        return context


class FormularioRazaMixin(PersonalAutorizadoMixin):
    model = Raza
    form_class = RazaForm
    template_name = 'razas/raza_form.html'
    success_url = reverse_lazy('lista_razas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.titulo
        return context

    def form_valid(self, form):
        messages.success(self.request, self.mensaje_exito)
        return super().form_valid(form)


class CrearRazaView(FormularioRazaMixin, CreateView):
    titulo = 'Registrar raza'
    mensaje_exito = 'Raza registrada correctamente.'


class EditarRazaView(FormularioRazaMixin, UpdateView):
    titulo = 'Editar raza'
    mensaje_exito = 'Raza actualizada correctamente.'


class EliminarRazaView(PersonalAutorizadoMixin, DeleteView):
    model = Raza
    template_name = 'razas/confirmar_eliminacion_raza.html'
    context_object_name = 'raza'
    success_url = reverse_lazy('lista_razas')

    def form_valid(self, form):
        messages.success(self.request, 'Raza eliminada correctamente.')
        return super().form_valid(form)
    

#VISTA PARA ESCOGER RAZA A LA HORA DE REGISTRAR MASCOTAS
