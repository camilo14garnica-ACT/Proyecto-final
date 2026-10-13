from django.urls import path
from . import views


urlpatterns = [
    path('', views.lista_mascotas, name='lista_mascotas'),
    path('nueva/', views.registrar_mascota, name='registrar_mascota'),
    path('razas_por_especie/<int:especie_id>/', views.razas_por_especie, name='razas_por_especie'),
    path('especies/nueva/', views.crear_especie, name='crear_especie'),
]
