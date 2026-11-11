from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from usuarios.decorators import solo_admin
from .models import EncuestaSatisfaccion, PQRS, LoteProducto, NoConformidad
from .forms import (
    PQRSForm,
    AtenderPQRSForm,
    EncuestaSatisfaccionForm,
    LoteProductoForm,
    NoConformidadForm,
)


# ============================================================
# VISTAS PARA CLIENTES (FRONTEND PÚBLICO / USUARIO)
# ============================================================

@login_required
def radicar_pqrs(request):
    """Permite a un cliente radicar una nueva PQRS."""
    if request.method == 'POST':
        form = PQRSForm(request.POST)
        if form.is_valid():
            pqrs = form.save(commit=False)
            pqrs.cliente = request.user
            pqrs.save()
            messages.success(
                request,
                f'Tu {pqrs.get_tipo_display().lower()} ha sido radicada exitosamente con el número #{pqrs.pk}.'
            )
            return redirect('mis_pqrs')
    else:
        form = PQRSForm()

    return render(request, 'calidad/radicar_pqrs.html', {'form': form})


@login_required
def mis_pqrs(request):
    """Muestra el historial y estado de las PQRS del usuario autenticado."""
    lista = PQRS.objects.filter(cliente=request.user).order_by('-fecha')
    return render(request, 'calidad/mis_pqrs.html', {'pqrs_list': lista})


@login_required
def crear_encuesta(request):
    """Permite al cliente calificar un servicio recibido."""
    if request.method == 'POST':
        form = EncuestaSatisfaccionForm(request.POST, cliente=request.user)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.cliente = request.user
            encuesta.save()
            messages.success(request, '¡Muchas gracias por tus comentarios! Nos ayudan a mejorar cada día.')
            return redirect('inicio')
    else:
        form = EncuestaSatisfaccionForm(cliente=request.user)

    return render(request, 'calidad/crear_encuesta.html', {'form': form})


# ============================================================
# VISTAS DE ADMINISTRACIÓN (PANEL INTERNO MASCOTT)
# ============================================================

@solo_admin
def admin_pqrs_list(request):
    """Listado de todas las PQRS recibidas en la clínica."""
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')

    queryset = PQRS.objects.select_related('cliente').all().order_by('-fecha')
    if tipo_filtro:
        queryset = queryset.filter(tipo=tipo_filtro)
    if estado_filtro:
        queryset = queryset.filter(estado=estado_filtro)

    conteo = {
        'total': PQRS.objects.count(),
        'abiertas': PQRS.objects.filter(estado=PQRS.Estado.ABIERTA).count(),
        'en_proceso': PQRS.objects.filter(estado=PQRS.Estado.EN_PROCESO).count(),
        'cerradas': PQRS.objects.filter(estado=PQRS.Estado.CERRADA).count(),
    }

    return render(request, 'calidad/admin_pqrs_list.html', {
        'pqrs_list': queryset,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
        'conteo': conteo,
        'tipos': PQRS.Tipo.choices,
        'estados': PQRS.Estado.choices,
    })


@solo_admin
def admin_pqrs_detalle(request, pk):
    """Detalle de una PQRS y cambio de estado."""
    pqrs = get_object_or_404(PQRS.objects.select_related('cliente'), pk=pk)

    if request.method == 'POST':
        form = AtenderPQRSForm(request.POST, instance=pqrs)
        if form.is_valid():
            form.save()
            messages.success(request, f'Estado de la PQRS #{pqrs.pk} actualizado correctamente.')
            return redirect('admin_pqrs_detalle', pk=pk)
    else:
        form = AtenderPQRSForm(instance=pqrs)

    no_conformidades = pqrs.no_conformidades.all()

    return render(request, 'calidad/admin_pqrs_detalle.html', {
        'pqrs': pqrs,
        'form': form,
        'no_conformidades': no_conformidades,
    })


@solo_admin
def admin_lotes_list(request):
    """Control de lotes de productos con alertas de vencimiento."""
    hoy = timezone.now().date()
    en_30_dias = hoy + timedelta(days=30)

    lotes = LoteProducto.objects.select_related('producto').all().order_by('fecha_vencimiento')

    # Clasificación de alertas
    total_lotes = lotes.count()
    vencidos_count = lotes.filter(fecha_vencimiento__lt=hoy).count()
    por_vencer_count = lotes.filter(fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=en_30_dias).count()
    vigentes_count = lotes.filter(fecha_vencimiento__gt=en_30_dias).count()

    filtro_alerta = request.GET.get('alerta', '')
    if filtro_alerta == 'vencidos':
        lotes = lotes.filter(fecha_vencimiento__lt=hoy)
    elif filtro_alerta == 'por_vencer':
        lotes = lotes.filter(fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=en_30_dias)
    elif filtro_alerta == 'vigentes':
        lotes = lotes.filter(fecha_vencimiento__gt=en_30_dias)

    return render(request, 'calidad/admin_lotes_list.html', {
        'lotes': lotes,
        'hoy': hoy,
        'en_30_dias': en_30_dias,
        'filtro_alerta': filtro_alerta,
        'total_lotes': total_lotes,
        'vencidos_count': vencidos_count,
        'por_vencer_count': por_vencer_count,
        'vigentes_count': vigentes_count,
    })


@solo_admin
def admin_lote_crear(request):
    """Registrar un nuevo lote de producto."""
    if request.method == 'POST':
        form = LoteProductoForm(request.POST)
        if form.is_valid():
            lote = form.save()
            messages.success(request, f'Lote {lote.numero_lote} registrado exitosamente.')
            return redirect('admin_lotes_list')
    else:
        form = LoteProductoForm()

    return render(request, 'calidad/admin_lote_form.html', {'form': form, 'titulo': 'Registrar Lote de Producto'})


@solo_admin
def admin_lote_editar(request, pk):
    """Editar un lote de producto existente."""
    lote = get_object_or_404(LoteProducto, pk=pk)
    if request.method == 'POST':
        form = LoteProductoForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lote {lote.numero_lote} actualizado correctamente.')
            return redirect('admin_lotes_list')
    else:
        form = LoteProductoForm(instance=lote)

    return render(request, 'calidad/admin_lote_form.html', {'form': form, 'titulo': f'Editar Lote {lote.numero_lote}'})


@solo_admin
def admin_no_conformidades_list(request):
    """Listado y seguimiento de no conformidades."""
    estado_filtro = request.GET.get('estado', '')
    queryset = NoConformidad.objects.select_related('pqrs', 'encuesta').all().order_by('-fecha')

    if estado_filtro:
        queryset = queryset.filter(estado=estado_filtro)

    conteo = {
        'total': NoConformidad.objects.count(),
        'abiertas': NoConformidad.objects.filter(estado=NoConformidad.Estado.ABIERTA).count(),
        'en_proceso': NoConformidad.objects.filter(estado=NoConformidad.Estado.EN_PROCESO).count(),
        'resueltas': NoConformidad.objects.filter(estado=NoConformidad.Estado.RESUELTA).count(),
    }

    return render(request, 'calidad/admin_no_conformidades_list.html', {
        'no_conformidades': queryset,
        'conteo': conteo,
        'estado_filtro': estado_filtro,
        'estados': NoConformidad.Estado.choices,
    })


@solo_admin
def admin_no_conformidad_crear(request):
    """Registrar una no conformidad."""
    pqrs_id = request.GET.get('pqrs_id')
    encuesta_id = request.GET.get('encuesta_id')

    initial_data = {}
    if pqrs_id:
        initial_data['pqrs'] = pqrs_id
    if encuesta_id:
        initial_data['encuesta'] = encuesta_id

    if request.method == 'POST':
        form = NoConformidadForm(request.POST)
        if form.is_valid():
            nc = form.save()
            messages.success(request, f'No conformidad #{nc.pk} registrada correctamente.')
            return redirect('admin_no_conformidades_list')
    else:
        form = NoConformidadForm(initial=initial_data)

    return render(request, 'calidad/admin_no_conformidad_form.html', {
        'form': form,
        'titulo': 'Registrar No Conformidad / Acción Correctiva'
    })


@solo_admin
def admin_no_conformidad_editar(request, pk):
    """Editar estado o acción correctiva de una no conformidad."""
    nc = get_object_or_404(NoConformidad, pk=pk)
    if request.method == 'POST':
        form = NoConformidadForm(request.POST, instance=nc)
        if form.is_valid():
            form.save()
            messages.success(request, f'No conformidad #{nc.pk} actualizada correctamente.')
            return redirect('admin_no_conformidades_list')
    else:
        form = NoConformidadForm(instance=nc)

    return render(request, 'calidad/admin_no_conformidad_form.html', {
        'form': form,
        'titulo': f'Gestionar No Conformidad #{nc.pk}'
    })


@solo_admin
def admin_encuestas_list(request):
    """Métricas y listado de encuestas de satisfacción."""
    encuestas = EncuestaSatisfaccion.objects.select_related('cliente', 'cita').all().order_by('-fecha')

    # Métricas generales
    total = encuestas.count()
    promedio = encuestas.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0.0

    distribucion = {
        '5': encuestas.filter(puntuacion=5).count(),
        '4': encuestas.filter(puntuacion=4).count(),
        '3': encuestas.filter(puntuacion=3).count(),
        '2': encuestas.filter(puntuacion=2).count(),
        '1': encuestas.filter(puntuacion=1).count(),
    }

    return render(request, 'calidad/admin_encuestas_list.html', {
        'encuestas': encuestas,
        'total': total,
        'promedio': round(promedio, 2),
        'distribucion': distribucion,
    })
