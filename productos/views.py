from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProductoForm


def solo_admin(request):
    return request.user.rol == "ADMIN"


# VM-723 — Registrar un producto
@login_required
def crear_producto(request):
    if not solo_admin(request):
        messages.error(request, "No tienes permiso.")
        return redirect("mi_perfil")

    if request.method == "POST":
        # request.FILES lleva la imagen (VM-725)
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado correctamente.')
            return redirect("crear_producto")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = ProductoForm()

    return render(request, "productos/producto_form.html", {
        "form": form,
        "titulo": "Nuevo producto",
    })