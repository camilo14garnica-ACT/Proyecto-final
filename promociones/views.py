from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PromocionForm


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
            return redirect("crear_promocion")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = PromocionForm()

    return render(request, "promociones/promocion_form.html", {
        "form": form,
        "titulo": "Nueva promoción",
    })