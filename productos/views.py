from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AjusteStockForm, CategoriaForm, ProductoForm
from .models import Categoria, Producto


def solo_admin(request):
    return request.user.rol == "ADMIN"


def sin_permiso(request):
    messages.error(request, "No tienes permiso.")
    return redirect("mi_perfil")


# ---------- PRODUCTOS (VM-720, VM-728, VM-751) ----------

@login_required
def lista_productos(request):
    if not solo_admin(request):
        return sin_permiso(request)

    productos = Producto.objects.select_related("categoria")
    q = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "")
    estado = request.GET.get("estado", "")

    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if categoria:
        productos = productos.filter(categoria_id=categoria)
    if estado:
        productos = productos.filter(estado=estado)

    return render(request, "productos/lista_productos.html", {
        "productos": productos,
        "categorias": Categoria.objects.all(),
        "q": q,
        "categoria_sel": categoria,
        "estado_sel": estado,
    })


@login_required
def crear_producto(request):
    if not solo_admin(request):
        return sin_permiso(request)

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado correctamente.')
            return redirect("lista_productos")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = ProductoForm()

    return render(request, "productos/producto_form.html", {"form": form, "titulo": "Nuevo producto"})


@login_required
def editar_producto(request, pk):
    if not solo_admin(request):
        return sin_permiso(request)

    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect("lista_productos")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "productos/producto_form.html", {"form": form, "titulo": "Editar producto"})


@login_required
@require_POST
def eliminar_producto(request, pk):
    if not solo_admin(request):
        return sin_permiso(request)

    producto = get_object_or_404(Producto, pk=pk)
    try:
        producto.delete()
        messages.success(request, f'Producto "{producto.nombre}" eliminado.')
    except ProtectedError:
        messages.error(request, "No se puede eliminar: el producto está en órdenes de compra. Márcalo como Inactivo.")
    return redirect("lista_productos")


# ---------- CATEGORÍAS (VM-758) ----------

@login_required
def lista_categorias(request):
    if not solo_admin(request):
        return sin_permiso(request)

    categorias = Categoria.objects.annotate(total=Count("productos"))
    return render(request, "productos/lista_categorias.html", {"categorias": categorias})


@login_required
def crear_categoria(request):
    if not solo_admin(request):
        return sin_permiso(request)

    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada correctamente.')
            return redirect("lista_categorias")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = CategoriaForm()

    return render(request, "productos/producto_form.html", {"form": form, "titulo": "Nueva categoría"})


@login_required
def editar_categoria(request, pk):
    if not solo_admin(request):
        return sin_permiso(request)

    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente.')
            return redirect("lista_categorias")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, "productos/producto_form.html", {"form": form, "titulo": "Editar categoría"})


@login_required
@require_POST
def eliminar_categoria(request, pk):
    if not solo_admin(request):
        return sin_permiso(request)

    categoria = get_object_or_404(Categoria, pk=pk)
    try:
        categoria.delete()
        messages.success(request, f'Categoría "{categoria.nombre}" eliminada.')
    except ProtectedError:
        messages.error(request, "No se puede eliminar: tiene productos asociados. Márcala como Inactiva.")
    return redirect("lista_categorias")


# ---------- STOCK (VM-766) ----------

@login_required
def ajustar_stock(request, pk):
    if not solo_admin(request):
        return sin_permiso(request)

    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = AjusteStockForm(request.POST, producto=producto)
        if form.is_valid():
            cantidad = form.cleaned_data["cantidad"]
            if form.cleaned_data["tipo"] == "ENTRADA":
                producto.stock += cantidad
            else:
                producto.stock -= cantidad
            producto.save(update_fields=["stock"])
            messages.success(request, f'Stock de "{producto.nombre}" actualizado: {producto.stock} unidades.')
            return redirect("lista_productos")
        messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = AjusteStockForm(producto=producto)

    return render(request, "productos/stock_form.html", {"form": form, "producto": producto})


# ---------- CATÁLOGO (VM-773) ----------

@login_required
def catalogo(request):
    productos = Producto.objects.filter(
        estado="ACTIVO", categoria__estado="ACTIVO", stock__gt=0
    ).select_related("categoria")

    q = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "")
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if categoria:
        productos = productos.filter(categoria_id=categoria)

    return render(request, "productos/catalogo.html", {
        "productos": productos,
        "categorias": Categoria.objects.filter(estado="ACTIVO"),
        "q": q,
        "categoria_sel": categoria,
    })