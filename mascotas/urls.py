from django.urls import path
from . import views


urlpatterns = [
    #Crud de mascotas
    path('', views.lista_mascotas, name='lista_mascotas'),
    path('nueva/', views.registrar_mascota, name='registrar_mascota'),
    path('editar/<int:pk>', views.eliminar_mascota, name='eliminar_mascota'),
    path('eliminar/<int:pk>', views.eliminar_mascota, name='eliminar_mascota'),
    
    #Consulta de razas por especie
    path('razas_por_especie/<int:especie_id>/', views.razas_por_especie, name='razas_por_especie'),
    path('especies/nueva/', views.crear_especie, name='crear_especie'),
]
