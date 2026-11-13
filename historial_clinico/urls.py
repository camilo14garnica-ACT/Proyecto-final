from django.urls import path

from . import views

urlpatterns = [
    path('mascota/<int:mascota_id>/', views.historial_mascota, name='historial_mascota'),
    path('mascota/<int:mascota_id>/nuevo/', views.agregar_registro, name='agregar_registro',)
]
