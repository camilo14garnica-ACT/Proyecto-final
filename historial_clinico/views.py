from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from mascotas.models import Mascota
from mascotas.permisos import es_personal

from .forms import RegistroClinicoForm


def _mascota_permitida(request, mascota_id):
    """El personal ve cualquier mascota; el cliente solo las suyas."""
    mascotas = Mascota.objects.select_related('especie', 'raza', 'Cliente')
    if not es_personal(request.user):
        mascotas = mascotas.filter(Cliente=request.user)
    return get_object_or_404(mascotas, pk=mascota_id)


@login_required
def lista_historial(request):
    """Vista de entrada al historial clínico: lista de mascotas con buscador."""
    if not es_personal(request.user):
        raise PermissionDenied

    busqueda = request.GET.get('q', '').strip()
    mascotas = Mascota.objects.select_related('especie', 'raza', 'Cliente').filter(estado='ACTIVO')

    if busqueda:
        mascotas = mascotas.filter(nombre__icontains=busqueda) | \
                   Mascota.objects.select_related('especie', 'raza', 'Cliente').filter(
                       Cliente__first_name__icontains=busqueda, estado='ACTIVO') | \
                   Mascota.objects.select_related('especie', 'raza', 'Cliente').filter(
                       Cliente__last_name__icontains=busqueda, estado='ACTIVO')
        mascotas = mascotas.distinct()

    mascotas = mascotas.order_by('nombre')
    pagina = Paginator(mascotas, 15).get_page(request.GET.get('page'))

    return render(request, 'historial_clinico/lista_historial.html', {
        'pagina': pagina,
        'busqueda': busqueda,
    })


@login_required
def historial_mascota(request, mascota_id):
    mascota = _mascota_permitida(request, mascota_id)
    registros = (
        mascota.registros_clinicos
        .filter(estado='ACTIVO')
        .select_related('registrado_por')
    )
    pagina = Paginator(registros, 10).get_page(request.GET.get('page'))
    return render(request, 'historial_clinico/historial_mascota.html', {
        'mascota': mascota,
        'pagina': pagina,
        'es_personal': es_personal(request.user),
    })


@login_required
def agregar_registro(request, mascota_id):
    mascota = _mascota_permitida(request, mascota_id)
    if not es_personal(request.user):
        raise PermissionDenied

    form = RegistroClinicoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        registro = form.save(commit=False)
        registro.mascota = mascota
        registro.registrado_por = request.user
        registro.save()
        messages.success(request, 'Registro clínico guardado correctamente.')
        return redirect('historial_mascota', mascota_id=mascota.pk)

    return render(request, 'historial_clinico/registro_form.html', {
        'mascota': mascota,
        'form': form,
    })
