import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from usuarios.decorators import solo_admin
from .models import EncuestaSatisfaccion, PQRS, LoteProducto, NoConformidad, Notificacion
from .forms import (
    PQRSForm,
    AtenderPQRSForm,
    EncuestaSatisfaccionForm,
    LoteProductoForm,
    NoConformidadForm,
)
from .exports import (
    exportar_pqrs_excel,
    exportar_lotes_excel,
    exportar_encuestas_excel,
    exportar_no_conformidades_excel,
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
    cita_id = request.GET.get('cita_id')
    initial_data = {}
    if cita_id:
        initial_data['cita'] = cita_id

    if request.method == 'POST':
        form = EncuestaSatisfaccionForm(request.POST, cliente=request.user)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.cliente = request.user
            encuesta.save()
            messages.success(request, '¡Muchas gracias por tus comentarios! Nos ayudan a mejorar cada día.')
            return redirect('inicio')
    else:
        form = EncuestaSatisfaccionForm(cliente=request.user, initial=initial_data)

    return render(request, 'calidad/crear_encuesta.html', {'form': form, 'cita_id': cita_id})


# ============================================================
# CENTRO DE NOTIFICACIONES
# ============================================================

@login_required
def mis_notificaciones(request):
    """Bandeja de notificaciones del usuario autenticado."""
    filtro_estado = request.GET.get('estado', '')
    queryset = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')

    total_count = queryset.count()
    no_leidas_count = queryset.filter(leida=False).count()

    if filtro_estado == 'no_leidas':
        queryset = queryset.filter(leida=False)
    elif filtro_estado == 'leidas':
        queryset = queryset.filter(leida=True)

    return render(request, 'calidad/notificaciones.html', {
        'notificaciones_list': queryset,
        'filtro_estado': filtro_estado,
        'total_count': total_count,
        'no_leidas_count': no_leidas_count,
    })


@login_required
def marcar_notificacion_leida(request, pk):
    """Marca una notificación específica como leída y redirige a su enlace si existe."""
    notif = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notif.leida = True
    notif.save()

    next_url = request.GET.get('next') or request.POST.get('next') or notif.enlace
    if next_url:
        return redirect(next_url)
    return redirect('mis_notificaciones')


@login_required
def marcar_todas_notificaciones_leidas(request):
    """Marca todas las notificaciones pendientes del usuario como leídas."""
    if request.method == 'POST':
        Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    return redirect('mis_notificaciones')


# ============================================================
# REPORTES Y EXPORTACIÓN EN EXCEL
# ============================================================

@solo_admin
def exportar_pqrs_view(request):
    """Descarga reporte en Excel de las PQRS."""
    queryset = PQRS.objects.all().order_by('-fecha')
    tipo_filtro = request.GET.get('tipo', '')
    estado_filtro = request.GET.get('estado', '')
    if tipo_filtro:
        queryset = queryset.filter(tipo=tipo_filtro)
    if estado_filtro:
        queryset = queryset.filter(estado=estado_filtro)
    return exportar_pqrs_excel(queryset)


@solo_admin
def exportar_lotes_view(request):
    """Descarga reporte en Excel de los lotes de productos."""
    queryset = LoteProducto.objects.all().order_by('fecha_vencimiento')
    alerta = request.GET.get('alerta', '')
    hoy = timezone.now().date()
    if alerta == 'vencidos':
        queryset = queryset.filter(fecha_vencimiento__lt=hoy)
    elif alerta == 'por_vencer':
        queryset = queryset.filter(fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=hoy + timedelta(days=30))
    elif alerta == 'vigentes':
        queryset = queryset.filter(fecha_vencimiento__gt=hoy + timedelta(days=30))
    return exportar_lotes_excel(queryset)


@solo_admin
def exportar_encuestas_view(request):
    """Descarga reporte en Excel de las encuestas de satisfacción."""
    queryset = EncuestaSatisfaccion.objects.all().order_by('-fecha')
    puntuacion = request.GET.get('puntuacion')
    if puntuacion:
        queryset = queryset.filter(puntuacion=puntuacion)
    return exportar_encuestas_excel(queryset)


@solo_admin
def exportar_no_conformidades_view(request):
    """Descarga reporte en Excel de no conformidades."""
    queryset = NoConformidad.objects.all().order_by('-fecha')
    estado = request.GET.get('estado')
    if estado:
        queryset = queryset.filter(estado=estado)
    return exportar_no_conformidades_excel(queryset)


# ============================================================
# DASHBOARD DE INDICADORES Y GRÁFICOS (CHART.JS)
# ============================================================

@solo_admin
def admin_dashboard(request):
    """Tablero interactivo con indicadores de gestión, métricas y gráficos estadísticos."""
    hoy = timezone.now().date()
    en_30_dias = hoy + timedelta(days=30)

    # 1. Indicadores generales de PQRS
    total_pqrs = PQRS.objects.count()
    pqrs_abiertas = PQRS.objects.filter(estado=PQRS.Estado.ABIERTA).count()
    pqrs_en_proceso = PQRS.objects.filter(estado=PQRS.Estado.EN_PROCESO).count()
    pqrs_cerradas = PQRS.objects.filter(estado=PQRS.Estado.CERRADA).count()
    tasa_resolucion = round((pqrs_cerradas / total_pqrs * 100), 1) if total_pqrs > 0 else 0.0

    # 2. Indicadores de satisfacción
    total_encuestas = EncuestaSatisfaccion.objects.count()
    promedio_satisfaccion = EncuestaSatisfaccion.objects.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0.0
    distribucion_estrellas = [
        EncuestaSatisfaccion.objects.filter(puntuacion=i).count()
        for i in range(1, 6)
    ]

    # 3. Indicadores de lotes
    total_lotes = LoteProducto.objects.count()
    lotes_vencidos = LoteProducto.objects.filter(fecha_vencimiento__lt=hoy).count()
    lotes_por_vencer = LoteProducto.objects.filter(fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=en_30_dias).count()
    lotes_vigentes = LoteProducto.objects.filter(fecha_vencimiento__gt=en_30_dias).count()

    # 4. Indicadores de No Conformidades
    total_nc = NoConformidad.objects.count()
    nc_abiertas = NoConformidad.objects.filter(estado=NoConformidad.Estado.ABIERTA).count()
    nc_en_proceso = NoConformidad.objects.filter(estado=NoConformidad.Estado.EN_PROCESO).count()
    nc_resueltas = NoConformidad.objects.filter(estado=NoConformidad.Estado.RESUELTA).count()

    # 5. Distribución de PQRS por tipo (para gráfico circular)
    pqrs_tipos_labels = ['Peticiones', 'Quejas', 'Reclamos', 'Sugerencias']
    pqrs_tipos_valores = [
        PQRS.objects.filter(tipo=PQRS.Tipo.PETICION).count(),
        PQRS.objects.filter(tipo=PQRS.Tipo.QUEJA).count(),
        PQRS.objects.filter(tipo=PQRS.Tipo.RECLAMO).count(),
        PQRS.objects.filter(tipo=PQRS.Tipo.SUGERENCIA).count(),
    ]

    # 6. Tendencia de los últimos 6 meses
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    meses_labels = []
    tendencia_radicadas = []
    tendencia_cerradas = []

    ahora = timezone.now()
    for i in range(5, -1, -1):
        # Calcular fecha del mes
        mes_target = (ahora.month - i - 1) % 12 + 1
        ano_target = ahora.year if (ahora.month - i) > 0 else ahora.year - 1
        label = f"{meses_nombres[mes_target - 1]} {ano_target}"
        meses_labels.append(label)

        radicadas = PQRS.objects.filter(fecha__year=ano_target, fecha__month=mes_target).count()
        cerradas = PQRS.objects.filter(
            fecha__year=ano_target,
            fecha__month=mes_target,
            estado=PQRS.Estado.CERRADA
        ).count()
        tendencia_radicadas.append(radicadas)
        tendencia_cerradas.append(cerradas)

    context = {
        'total_pqrs': total_pqrs,
        'pqrs_abiertas': pqrs_abiertas,
        'pqrs_en_proceso': pqrs_en_proceso,
        'pqrs_cerradas': pqrs_cerradas,
        'tasa_resolucion': tasa_resolucion,
        'total_encuestas': total_encuestas,
        'promedio_satisfaccion': round(promedio_satisfaccion, 2),
        'total_lotes': total_lotes,
        'lotes_vencidos': lotes_vencidos,
        'lotes_por_vencer': lotes_por_vencer,
        'lotes_vigentes': lotes_vigentes,
        'total_nc': total_nc,
        'nc_abiertas': nc_abiertas,
        'nc_en_proceso': nc_en_proceso,
        'nc_resueltas': nc_resueltas,
        # JSON para Chart.js
        'chart_meses_labels': json.dumps(meses_labels),
        'chart_tendencia_radicadas': json.dumps(tendencia_radicadas),
        'chart_tendencia_cerradas': json.dumps(tendencia_cerradas),
        'chart_pqrs_tipos_labels': json.dumps(pqrs_tipos_labels),
        'chart_pqrs_tipos_valores': json.dumps(pqrs_tipos_valores),
        'chart_estrellas_distribucion': json.dumps(distribucion_estrellas),
        'chart_lotes_valores': json.dumps([lotes_vigentes, lotes_por_vencer, lotes_vencidos]),
        'chart_nc_valores': json.dumps([nc_abiertas, nc_en_proceso, nc_resueltas]),
    }

    return render(request, 'calidad/admin_dashboard.html', context)


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
