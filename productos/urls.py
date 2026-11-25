from django.urls import path

from . import views

urlpatterns = [
    # Productos
    path("", views.lista_productos, name="lista_productos"),
    path("crear/", views.crear_producto, name="crear_producto"),
    path("<int:pk>/editar/", views.editar_producto, name="editar_producto"),
    path("<int:pk>/eliminar/", views.eliminar_producto, name="eliminar_producto"),
    # Stock
    path("<int:pk>/stock/", views.ajustar_stock, name="ajustar_stock"),
    # Categorías
    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categorias/crear/", views.crear_categoria, name="crear_categoria"),
    path("categorias/<int:pk>/editar/", views.editar_categoria, name="editar_categoria"),
    path("categorias/<int:pk>/eliminar/", views.eliminar_categoria, name="eliminar_categoria"),
    # Catálogo
    path("catalogo/", views.catalogo, name="catalogo"),
]