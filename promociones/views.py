from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from .forms import PromocionForm
from .models import Promocion

# Opciones de orden permitidas (lista cerrada, así nadie ordena por campos raros)
ORDENES = {
    "recientes": "-fecha_registro",
    "nombre": "nombre",
    "descuento": "-descuento",
    "inicio": "-fecha_inicio",
    "fin": "fecha_fin",
}


def solo_admin(request):
    return request.user.rol == "ADMIN"


# VM-704 — Formulario para crear una promoción
@login_required
def crear_promocion(request):
    if not solo_admin(request):
        messages.error(request, "No tienes permiso.")
        return redirect("mi_perfil")

    if request.method == "POST":
        form = PromocionForm(request.POST)
        if form.is_valid():
            promocion = form.save()
            messages.success(request, f'Promoción "{promocion.nombre}" creada correctamente.')
            return redirect("lista_promociones")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = PromocionForm()

    return render(request, "promociones/promocion_form.html", {
        "form": form,
        "titulo": "Nueva promoción",
    })


# VM-715 — Listar promociones (VM-718: con orden)
@login_required
def lista_promociones(request):
    if not solo_admin(request):
        messages.error(request, "No tienes permiso.")
        return redirect("mi_perfil")

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