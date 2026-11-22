from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_promociones, name="lista_promociones"),
    path("crear/", views.crear_promocion, name="crear_promocion"),
    path("<int:pk>/editar/", views.editar_promocion, name="editar_promocion"),
    path("<int:pk>/eliminar/", views.eliminar_promocion, name="eliminar_promocion"),
]