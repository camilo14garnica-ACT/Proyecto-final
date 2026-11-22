from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PromocionForm
from .models import Promocion

ORDENES = {
    "recientes": "-fecha_registro",
    "nombre": "nombre",
    "descuento": "-descuento",
    "inicio": "-fecha_inicio",
    "fin": "fecha_fin",
}


def solo_admin(request):
    return request.user.rol == "ADMIN"


def sin_permiso(request):
    messages.error(request, "No tienes permiso.")
    return redirect("mi_perfil")


# VM-704 — Crear promoción
@login_required
def crear_promocion(request):
    if not solo_admin(request):
        return sin_permiso(request)

    if request.method == "POST":
        form = PromocionForm(request.POST)
        if form.is_valid():
            promocion = form.save()
            messages.success(request, f'Promoción "{promocion.nombre}" creada correctamente.')
            return redirect("lista_promociones")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = PromocionForm()

    return render(request, "promociones/promocion_form.html", {"form": form, "titulo": "Nueva promoción"})


# VM-715 / VM-718 — Listar con orden
@login_required
def lista_promociones(request):
    if not solo_admin(request):
        return sin_permiso(request)

    orden = request.GET.get("orden", "recientes")
    if orden not in ORDENES:
        orden = "recientes"
    estado = request.GET.get("estado", "")

    promociones = Promocion.objects.annotate(total_productos=Count("productos"))
    if estado:
        promociones = promociones.filter(estado=estado)
    promociones = promociones.order_by(ORDENES[orden])

    return render(request, "promociones/lista_promociones.html", {
        "promociones": promociones,
        "orden": orden,
        "estado_sel": estado,
    })


# VM-707 — Editar promoción
@login_required
def editar_promocion(request, pk):
    if not solo_admin(request):
        return sin_permiso(request)

    promocion = get_object_or_404(Promocion, pk=pk)
    if request.method == "POST":
        form = PromocionForm(request.POST, instance=promocion)
        if form.is_valid():
            form.save()
            messages.success(request, f'Promoción "{promocion.nombre}" actualizada correctamente.')
            return redirect("lista_promociones")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = PromocionForm(instance=promocion)

    return render(request, "promociones/promocion_form.html", {"form": form, "titulo": "Editar promoción"})


# VM-707 — Eliminar promoción
@login_required
@require_POST
def eliminar_promocion(request, pk):
    if not solo_admin(request):
        return sin_permiso(request)

    promocion = get_object_or_404(Promocion, pk=pk)
    nombre = promocion.nombre
    promocion.delete()
    messages.success(request, f'Promoción "{nombre}" eliminada.')
    return redirect("lista_promociones")