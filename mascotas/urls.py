from django.urls import path
from . import views


urlpatterns = [
    #Crud de mascotas
    path('', views.lista_mascotas, name='lista_mascotas'),
    path('nueva/', views.registrar_mascota, name='registrar_mascota'),
    path('editar/<int:pk>', views.eliminar_mascota, name='eliminar_mascota'),
    path('eliminar/<int:pk>', views.editar_mascota, name='editar_mascota'),
    
    #Consulta de razas por especie
    path('razas_por_especie/<int:especie_id>/', views.razas_por_especie, name='razas_por_especie'),
    
    #Crud de especies
    path('especies/', views.ListarEspecieView.as_view(), name='lista_especies'),
    path('especies/crear/', views.CrearEspecieView.as_view(), name='especie_form'),
    path('especies/editar/<int:pk>/', views.EditarEspecieView.as_view(), name='editar_especie'),
    path('especies/eliminar/<int:pk>/', views.EliminarEspeciesView.as_view(), name='eliminar_especie')
]
