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


# ============================================================
# GESTIÓN DE CITAS
# ============================================================
from .models import Cita, Servicio, HorarioDisponible
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings as django_settings


def citas_visibles(usuario):
    """Retorna las citas según el rol del usuario — VM-604 restricción de acceso"""
    if usuario.rol == 'ADMIN':
        return Cita.objects.select_related('mascota', 'veterinario', 'servicio', 'mascota__Cliente').all()
    elif usuario.rol == 'VETERINARIO':
        return Cita.objects.select_related('mascota', 'veterinario', 'servicio').filter(veterinario=usuario)
    else:
        # Cliente solo ve sus propias citas
        return Cita.objects.select_related('mascota', 'veterinario', 'servicio').filter(mascota__Cliente=usuario)


# VM-71 / VM-485 — Ver horarios disponibles
@login_required
def ver_horarios(request):
    """Muestra los horarios de disponibilidad de los veterinarios"""
    from usuarios.models import Usuario
    veterinarios = Usuario.objects.filter(rol='VETERINARIO', is_active=True)
    horarios = HorarioDisponible.objects.filter(activo=True).select_related('veterinario')
    return render(request, 'mascotas/horarios.html', {
        'veterinarios': veterinarios,
        'horarios': horarios,
    })


# VM-71 — Gestionar horario (solo admin/vet)
@login_required
def gestionar_horario(request):
    """Admin/vet crea o edita sus propios horarios"""
    if request.user.rol not in ['ADMIN', 'VETERINARIO']:
        messages.error(request, 'No tienes permiso para gestionar horarios.')
        return redirect('mi_perfil')

    if request.method == 'POST':
        dia       = request.POST.get('dia_semana')
        h_inicio  = request.POST.get('hora_inicio')
        h_fin     = request.POST.get('hora_fin')
        vet_id    = request.POST.get('veterinario_id') if request.user.rol == 'ADMIN' else request.user.pk

        from usuarios.models import Usuario
        vet = get_object_or_404(Usuario, pk=vet_id, rol='VETERINARIO')

        HorarioDisponible.objects.update_or_create(
            veterinario=vet, dia_semana=dia, hora_inicio=h_inicio,
            defaults={'hora_fin': h_fin, 'activo': True}
        )
        messages.success(request, 'Horario guardado correctamente.')
        return redirect('ver_horarios')

    return redirect('ver_horarios')


# VM-502 — Agendar cita (cliente)
@login_required
def agendar_cita(request):
    """El cliente agenda su propia cita"""
    mascotas  = Mascota.objects.filter(Cliente=request.user, estado='ACTIVO')
    servicios = Servicio.objects.filter(estado='ACTIVO')
    from usuarios.models import Usuario
    veterinarios = Usuario.objects.filter(rol='VETERINARIO', is_active=True)
    error = None

    if request.method == 'POST':
        mascota_id   = request.POST.get('mascota')
        servicio_id  = request.POST.get('servicio')
        vet_id       = request.POST.get('veterinario') or None
        fecha_hora   = request.POST.get('fecha_hora')
        motivo       = request.POST.get('motivo', '')

        try:
            mascota  = get_object_or_404(Mascota, pk=mascota_id, Cliente=request.user)
            servicio = get_object_or_404(Servicio, pk=servicio_id)

            cita = Cita.objects.create(
                mascota=mascota,
                servicio=servicio,
                veterinario_id=vet_id if vet_id else None,
                fecha_hora=fecha_hora,
                motivo=motivo,
                estado=Cita.Estado.PROGRAMADA,
            )
            messages.success(request, f'Cita agendada para {cita.fecha_hora.strftime("%d/%m/%Y %H:%M")}.')
            return redirect('mis_citas')
        except Exception as e:
            error = f'Error al agendar la cita: {e}'

    return render(request, 'mascotas/agendar_cita.html', {
        'mascotas': mascotas,
        'servicios': servicios,
        'veterinarios': veterinarios,
        'error': error,
    })


# VM-523 — Agendar cita para un cliente (admin/vet)
@login_required
def agendar_cita_admin(request):
    """Admin o veterinario agenda una cita para cualquier cliente"""
    if request.user.rol not in ['ADMIN', 'VETERINARIO']:
        messages.error(request, 'No tienes permiso.')
        return redirect('mi_perfil')

    from usuarios.models import Usuario
    clientes     = Usuario.objects.filter(rol='CLIENTE', is_active=True)
    servicios    = Servicio.objects.filter(estado='ACTIVO')
    veterinarios = Usuario.objects.filter(rol='VETERINARIO', is_active=True)
    mascotas     = Mascota.objects.filter(estado='ACTIVO').select_related('Cliente')

    if request.method == 'POST':
        mascota_id  = request.POST.get('mascota')
        servicio_id = request.POST.get('servicio')
        vet_id      = request.POST.get('veterinario') or None
        fecha_hora  = request.POST.get('fecha_hora')
        motivo      = request.POST.get('motivo', '')

        mascota  = get_object_or_404(Mascota, pk=mascota_id)
        servicio = get_object_or_404(Servicio, pk=servicio_id)

        Cita.objects.create(
            mascota=mascota, servicio=servicio,
            veterinario_id=vet_id, fecha_hora=fecha_hora,
            motivo=motivo, estado=Cita.Estado.PROGRAMADA,
        )
        messages.success(request, 'Cita agendada correctamente.')
        return redirect('consultar_citas')

    return render(request, 'mascotas/agendar_cita_admin.html', {
        'clientes': clientes, 'servicios': servicios,
        'veterinarios': veterinarios, 'mascotas': mascotas,
    })


# VM-577 — Consultar y filtrar citas
@login_required
def consultar_citas(request):
    """Lista y filtra citas según rol y parámetros de búsqueda"""
    citas = citas_visibles(request.user)

    # Filtros opcionales
    estado    = request.GET.get('estado')
    servicio  = request.GET.get('servicio')
    fecha     = request.GET.get('fecha')

    if estado:
        citas = citas.filter(estado=estado)
    if servicio:
        citas = citas.filter(servicio_id=servicio)
    if fecha:
        citas = citas.filter(fecha_hora__date=fecha)

    servicios = Servicio.objects.filter(estado='ACTIVO')
    return render(request, 'mascotas/consultar_citas.html', {
        'citas': citas.order_by('-fecha_hora'),
        'servicios': servicios,
        'estados': Cita.Estado.choices,
        'filtros': {'estado': estado, 'servicio': servicio, 'fecha': fecha},
    })


# VM-581 — Reprogramar cita
@login_required
def reprogramar_cita(request, pk):
    """Cambia la fecha/hora de una cita existente"""
    cita = get_object_or_404(citas_visibles(request.user), pk=pk)

    if cita.estado in [Cita.Estado.COMPLETADA, Cita.Estado.CANCELADA]:
        messages.error(request, 'No se puede reprogramar una cita completada o cancelada.')
        return redirect('consultar_citas')

    if request.method == 'POST':
        nueva_fecha = request.POST.get('fecha_hora')
        motivo      = request.POST.get('motivo', cita.motivo)
        cita.fecha_hora = nueva_fecha
        cita.motivo     = motivo
        cita.estado     = Cita.Estado.PROGRAMADA
        cita.save()
        messages.success(request, f'Cita reprogramada para {cita.fecha_hora.strftime("%d/%m/%Y %H:%M")}.')
        return redirect('consultar_citas')

    return render(request, 'mascotas/reprogramar_cita.html', {'cita': cita})


# VM-585 — Cancelar cita
@login_required
def cancelar_cita(request, pk):
    """Cancela una cita — el cliente cancela la suya, admin/vet cualquiera"""
    cita = get_object_or_404(citas_visibles(request.user), pk=pk)

    if cita.estado == Cita.Estado.COMPLETADA:
        messages.error(request, 'No se puede cancelar una cita ya completada.')
        return redirect('consultar_citas')

    if request.method == 'POST':
        cita.estado = Cita.Estado.CANCELADA
        cita.save()
        messages.success(request, 'Cita cancelada correctamente.')
        return redirect('consultar_citas')

    return render(request, 'mascotas/cancelar_cita.html', {'cita': cita})


# VM-589 — Cambiar estado de la cita (solo admin/vet)
@login_required
def cambiar_estado_cita(request, pk):
    """Admin o veterinario cambia el estado de cualquier cita"""
    if request.user.rol not in ['ADMIN', 'VETERINARIO']:
        messages.error(request, 'No tienes permiso para cambiar el estado.')
        return redirect('consultar_citas')

    cita = get_object_or_404(Cita, pk=pk)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        notas        = request.POST.get('notas_veterinario', '')
        if nuevo_estado in dict(Cita.Estado.choices):
            cita.estado = nuevo_estado
            if notas:
                cita.notas_veterinario = notas
            cita.save()
            messages.success(request, f'Estado actualizado a "{cita.get_estado_display()}".')
        return redirect('consultar_citas')

    return render(request, 'mascotas/cambiar_estado_cita.html', {
        'cita': cita,
        'estados': Cita.Estado.choices,
    })


# VM-593 — Enviar recordatorio por correo
@login_required
def enviar_recordatorio(request, pk):
    """Envía recordatorio de cita al correo del dueño de la mascota"""
    if request.user.rol not in ['ADMIN', 'VETERINARIO']:
        messages.error(request, 'No tienes permiso.')
        return redirect('consultar_citas')

    cita = get_object_or_404(Cita, pk=pk)
    cliente = cita.mascota.Cliente

    try:
        send_mail(
            subject=f'🐾 Recordatorio de cita - Veterinaria Mascott',
            message=(
                f'Hola {cliente.first_name},\n\n'
                f'Te recordamos que tienes una cita programada:\n'
                f'• Mascota: {cita.mascota.nombre}\n'
                f'• Servicio: {cita.servicio.nombre}\n'
                f'• Fecha y hora: {cita.fecha_hora.strftime("%d/%m/%Y %H:%M")}\n'
                f'• Veterinario: {cita.veterinario or "Por asignar"}\n\n'
                f'Clínica Veterinaria Mascott\nCalle 15 #9-54, Sogamoso'
            ),
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.email],
            fail_silently=False,
        )
        messages.success(request, f'Recordatorio enviado a {cliente.email}.')
    except Exception as e:
        messages.error(request, f'Error al enviar correo: {e}')

    return redirect('consultar_citas')


# VM-599 — Historial de servicios por mascota
@login_required
def historial_mascota(request, pk):
    """Muestra el historial completo de citas de una mascota"""
    mascota = get_object_or_404(Mascota, pk=pk)

    # VM-604: solo el dueño, admin o vet asignado puede ver el historial
    if request.user.rol == 'CLIENTE' and mascota.Cliente != request.user:
        messages.error(request, 'No tienes acceso a este historial.')
        return redirect('mis_citas')

    citas = Cita.objects.filter(mascota=mascota).order_by('-fecha_hora')
    return render(request, 'mascotas/historial_mascota.html', {
        'mascota': mascota,
        'citas': citas,
    })


# VM-502 — Mis citas (vista del cliente)
@login_required
def mis_citas(request):
    """Panel de citas del cliente"""
    proximas = citas_visibles(request.user).filter(
        estado__in=['PROGRAMADA', 'CONFIRMADA']
    ).order_by('fecha_hora')

    pasadas = citas_visibles(request.user).filter(
        estado__in=['COMPLETADA', 'CANCELADA', 'NO_ASISTIO']
    ).order_by('-fecha_hora')[:10]

    return render(request, 'mascotas/mis_citas.html', {
        'proximas': proximas,
        'pasadas': pasadas,
    })
