from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_historial, name='lista_historial'),
    path('mascota/<int:mascota_id>/', views.historial_mascota, name='historial_mascota'),
    path('mascota/<int:mascota_id>/nuevo/', views.agregar_registro, name='agregar_registro'),
]
