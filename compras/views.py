from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from .models import OrdenCompra, ItemOrdenCompra, Proveedor, RecepcionCompra, ItemRecepcion, Lote
from productos.models import Producto


def solo_admin_o_vet(request):
    return request.user.rol in ['ADMIN', 'VETERINARIO']


# VM-271 — Crear orden de compra
@login_required
def crear_orden(request):
    if not solo_admin_o_vet(request):
        messages.error(request, 'No tienes permiso.')
        return redirect('mi_perfil')

    proveedores = Proveedor.objects.filter(activo=True)
    productos   = Producto.objects.filter(estado='ACTIVO')

    if request.method == 'POST':
        proveedor_id    = request.POST.get('proveedor')
        fecha_esperada  = request.POST.get('fecha_esperada') or None
        notas           = request.POST.get('notas', '')
        productos_ids   = request.POST.getlist('producto[]')
        cantidades      = request.POST.getlist('cantidad[]')
        precios         = request.POST.getlist('precio_unit[]')

        if not productos_ids:
            messages.error(request, 'Debes agregar al menos un producto.')
        else:
            proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
            orden = OrdenCompra.objects.create(
                proveedor=proveedor,
                creada_por=request.user,
                fecha_esperada=fecha_esperada,
                notas=notas,
            )
            for pid, cant, precio in zip(productos_ids, cantidades, precios):
                if pid and cant and precio:
                    ItemOrdenCompra.objects.create(
                        orden=orden,
                        producto_id=pid,
                        cantidad=int(cant),
                        precio_unit=precio,
                    )
            messages.success(request, f'Orden OC-{orden.pk} creada correctamente.')
            return redirect('lista_ordenes')

    return render(request, 'compras/crear_orden.html', {
        'proveedores': proveedores,
        'productos': productos,
    })


# VM-274 — Consultar y filtrar órdenes de compra
@login_required
def lista_ordenes(request):
    if not solo_admin_o_vet(request):
        messages.error(request, 'No tienes permiso.')
        return redirect('mi_perfil')

    ordenes = OrdenCompra.objects.select_related('proveedor', 'creada_por').all()

    # Filtros
    estado      = request.GET.get('estado')
    proveedor   = request.GET.get('proveedor')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if estado:
        ordenes = ordenes.filter(estado=estado)
    if proveedor:
        ordenes = ordenes.filter(proveedor_id=proveedor)
    if fecha_desde:
        ordenes = ordenes.filter(fecha_orden__gte=fecha_desde)
    if fecha_hasta:
        ordenes = ordenes.filter(fecha_orden__lte=fecha_hasta)

    return render(request, 'compras/lista_ordenes.html', {
        'ordenes': ordenes,
        'proveedores': Proveedor.objects.filter(activo=True),
        'estados': OrdenCompra.Estado.choices,
        'filtros': {'estado': estado, 'proveedor': proveedor, 'fecha_desde': fecha_desde, 'fecha_hasta': fecha_hasta},
    })


# Detalle de una orden
@login_required
def detalle_orden(request, pk):
    if not solo_admin_o_vet(request):
        return redirect('mi_perfil')
    orden = get_object_or_404(OrdenCompra, pk=pk)
    return render(request, 'compras/detalle_orden.html', {'orden': orden})


# VM-272 — Recepción e ingreso al inventario
@login_required
@transaction.atomic
def recibir_orden(request, pk):
    if not solo_admin_o_vet(request):
        messages.error(request, 'No tienes permiso.')
        return redirect('mi_perfil')

    orden = get_object_or_404(OrdenCompra, pk=pk)

    if orden.estado == OrdenCompra.Estado.CANCELADA:
        messages.error(request, 'No se puede recepcionar una orden cancelada.')
        return redirect('detalle_orden', pk=pk)

    if request.method == 'POST':
        productos_ids   = request.POST.getlist('producto[]')
        cantidades      = request.POST.getlist('cantidad[]')
        lotes           = request.POST.getlist('lote[]')
        vencimientos    = request.POST.getlist('vence[]')
        notas           = request.POST.get('notas', '')

        recepcion = RecepcionCompra.objects.create(
            orden=orden,
            recibido_por=request.user,
            notas=notas,
        )

        for pid, cant, lote, vence in zip(productos_ids, cantidades, lotes, vencimientos):
            if pid and cant:
                cantidad = int(cant)
                producto = get_object_or_404(Producto, pk=pid)

                # Registrar ítem de recepción
                ItemRecepcion.objects.create(
                    recepcion=recepcion,
                    producto=producto,
                    cantidad=cantidad,
                    numero_lote=lote,
                    fecha_vence=vence or None,
                )

                # VM-273 — Crear lote
                Lote.objects.create(
                    producto=producto,
                    orden=orden,
                    numero_lote=lote,
                    cantidad=cantidad,
                    fecha_vence=vence or None,
                )

                # Actualizar stock del producto
                producto.stock += cantidad
                producto.save()

        # Actualizar estado de la orden
        orden.estado = OrdenCompra.Estado.COMPLETADA
        orden.save()

        messages.success(request, 'Recepción registrada e inventario actualizado.')
        return redirect('lista_ordenes')

    return render(request, 'compras/recibir_orden.html', {'orden': orden})


# VM-273 — Gestión de lotes
@login_required
def lista_lotes(request):
    if not solo_admin_o_vet(request):
        return redirect('mi_perfil')

    lotes = Lote.objects.select_related('producto', 'orden').all()

    # Filtros
    producto    = request.GET.get('producto')
    vencidos    = request.GET.get('vencidos')
    por_vencer  = request.GET.get('por_vencer')  # próximos 30 días

    if producto:
        lotes = lotes.filter(producto_id=producto)
    if vencidos:
        lotes = lotes.filter(fecha_vence__lt=timezone.now().date())
    if por_vencer:
        limite = timezone.now().date() + timezone.timedelta(days=30)
        lotes = lotes.filter(fecha_vence__lte=limite, fecha_vence__gte=timezone.now().date())

    return render(request, 'compras/lista_lotes.html', {
        'lotes': lotes,
        'productos': Producto.objects.filter(estado='ACTIVO'),
        'hoy': timezone.now().date(),
    })


# Cancelar orden
@login_required
def cancelar_orden(request, pk):
    if not solo_admin_o_vet(request):
        return redirect('mi_perfil')

    orden = get_object_or_404(OrdenCompra, pk=pk)
    if request.method == 'POST':
        orden.estado = OrdenCompra.Estado.CANCELADA
        orden.save()
        messages.success(request, f'Orden OC-{orden.pk} cancelada.')
        return redirect('lista_ordenes')

    return render(request, 'compras/cancelar_orden.html', {'orden': orden})


# CRUD Proveedores
@login_required
def lista_proveedores(request):
    if not solo_admin_o_vet(request):
        return redirect('mi_perfil')
    proveedores = Proveedor.objects.all()
    return render(request, 'compras/lista_proveedores.html', {'proveedores': proveedores})


@login_required
def crear_proveedor(request):
    if not solo_admin_o_vet(request):
        return redirect('mi_perfil')

    if request.method == 'POST':
        Proveedor.objects.create(
            nombre=request.POST.get('nombre'),
            contacto=request.POST.get('contacto', ''),
            telefono=request.POST.get('telefono', ''),
            email=request.POST.get('email', ''),
            direccion=request.POST.get('direccion', ''),
        )
        messages.success(request, 'Proveedor creado correctamente.')
        return redirect('lista_proveedores')

    return render(request, 'compras/proveedor_form.html', {'titulo': 'Nuevo proveedor'})
