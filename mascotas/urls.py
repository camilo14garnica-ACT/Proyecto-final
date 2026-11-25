from django.urls import path
from . import views


urlpatterns = [
    #Crud de mascotas
    path('', views.ListaMascotasView.as_view(), name='lista_mascotas'),
    path('nueva/', views.CrearMascotaView.as_view(), name='registrar_mascota'),
    path('editar/<int:pk>/', views.EditarMascotaView.as_view(), name='editar_mascota'),
    path('eliminar/<int:pk>/', views.EliminarMascotaView.as_view(), name='eliminar_mascota'),
    
    #Consulta de razas por especie
    path('razas_por_especie/<int:especie_id>/', views.razas_por_especie, name='razas_por_especie'),
    
    #Crud de especies
    path('especies/', views.ListarEspecieView.as_view(), name='lista_especies'),
    path('especies/crear/', views.CrearEspecieView.as_view(), name='especie_form'),
    path('especies/editar/<int:pk>/', views.EditarEspecieView.as_view(), name='editar_especie'),
    path('especies/eliminar/<int:pk>/', views.EliminarEspeciesView.as_view(), name='eliminar_especie'),

    # CRUD de razas
    path('razas/', views.ListaRazasView.as_view(), name='lista_razas'),
    path('razas/crear/', views.CrearRazaView.as_view(), name='registrar_raza'),
    path('razas/editar/<int:pk>/', views.EditarRazaView.as_view(), name='editar_raza'),
    path('razas/eliminar/<int:pk>/', views.EliminarRazaView.as_view(), name='eliminar_raza'),

]
