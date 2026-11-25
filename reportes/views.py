import csv
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from productos.models import Categoria
from .models import Venta, DetalleVenta, ReporteGuardado, RegistroAuditoria

# Solo administradores (is_staff) pueden entrar (VM-687)
solo_admin = user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')


def aplicar_filtros(request):
    """VM-660: filtros por fechas, categoría y método de pago"""
    inicio = parse_date(request.GET.get('inicio') or '')
    fin = parse_date(request.GET.get('fin') or '')
    categoria = request.GET.get('categoria') or ''
    metodo = request.GET.get('metodo') or ''

    ventas = Venta.objects.all()
    detalles = DetalleVenta.objects.all()

    if inicio:
        ventas = ventas.filter(fecha__date__gte=inicio)
        detalles = detalles.filter(venta__fecha__date__gte=inicio)
    if fin:
        ventas = ventas.filter(fecha__date__lte=fin)
        detalles = detalles.filter(venta__fecha__date__lte=fin)
    if metodo:
        ventas = ventas.filter(metodo_pago=metodo)
        detalles = detalles.filter(venta__metodo_pago=metodo)
    if categoria:
        detalles = detalles.filter(producto__categoria_id=categoria)
        ventas = ventas.filter(id__in=detalles.values('venta_id'))

    return ventas, detalles, {'inicio': inicio, 'fin': fin, 'categoria': categoria, 'metodo': metodo}


def registrar(request, accion):
    """VM-687: auditoría básica"""
    RegistroAuditoria.objects.create(usuario=request.user, accion=accion)


@solo_admin
def dashboard(request):
    """VM-649 y VM-673: consultas, agregaciones y dashboard"""
    ventas, detalles, filtros = aplicar_filtros(request)

    total = ventas.aggregate(t=Sum('total'))['t'] or 0
    cantidad = ventas.count()
    promedio = (total / cantidad) if cantidad else 0

    por_mes = (ventas.annotate(mes=TruncMonth('fecha'))
               .values('mes').annotate(total=Sum('total'), n=Count('id')).order_by('mes'))

    por_metodo = (ventas.values('metodo_pago')
                  .annotate(total=Sum('total'), n=Count('id')).order_by('-total'))

    ingreso = ExpressionWrapper(F('cantidad') * F('precio_unitario'),
                                output_field=DecimalField(max_digits=14, decimal_places=2))
    top_productos = (detalles.values('producto__nombre')
                     .annotate(unidades=Sum('cantidad'), ingresos=Sum(ingreso))
                     .order_by('-unidades')[:5])

    registrar(request, 'Consultó el dashboard de ventas')

    contexto = {
        'total': total, 'cantidad': cantidad, 'promedio': promedio,
        'por_mes': por_mes, 'por_metodo': por_metodo, 'top_productos': top_productos,
        'categorias': Categoria.objects.all(),
        'metodos': Venta.METODOS_PAGO,
        'filtros': filtros,
        'guardados': ReporteGuardado.objects.order_by('-creado_en')[:10],
    }
    return render(request, 'reportes/dashboard.html', contexto)


@solo_admin
def exportar_csv(request):
    """VM-666: exportar el reporte filtrado a CSV (abre en Excel)"""
    ventas, _, _ = aplicar_filtros(request)
    registrar(request, 'Exportó reporte de ventas a CSV')

    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    respuesta.write('\ufeff')
    escritor = csv.writer(respuesta)
    escritor.writerow(['ID', 'Fecha', 'Cliente', 'Método de pago', 'Total'])
    for v in ventas:
        escritor.writerow([v.pk, v.fecha.strftime('%Y-%m-%d %H:%M'), v.cliente, v.get_metodo_pago_display(), v.total])
    return respuesta


@solo_admin
def guardar_reporte(request):
    """VM-681: guardar los filtros actuales como reporte"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre') or 'Reporte sin nombre'
        _, _, f = aplicar_filtros(request)
        ReporteGuardado.objects.create(
            nombre=nombre, fecha_inicio=f['inicio'], fecha_fin=f['fin'],
            categoria_id=f['categoria'] or None, creado_por=request.user,
        )
        registrar(request, f'Guardó el reporte "{nombre}"')
    return redirect('reportes:dashboard')