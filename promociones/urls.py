from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_promociones, name="lista_promociones"),
    path("crear/", views.crear_promocion, name="crear_promocion"),
]