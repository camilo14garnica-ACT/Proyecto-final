from django.urls import path

from . import views

urlpatterns = [
    # VM-720 — Crear nuevos productos
    path("crear/", views.crear_producto, name="crear_producto"),
]