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
    path('especies/eliminar/<int:pk>/', views.EliminarEspeciesView.as_view(), name='eliminar_especie'),

    # Carrito de compras
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/quitar/<int:item_id>/', views.quitar_del_carrito, name='quitar_carrito'),
    path('carrito/pagar/', views.pagar_carrito, name='pagar_carrito'),

    # VM-71/485 — Horarios
    path('horarios/', views.ver_horarios, name='ver_horarios'),
    path('horarios/gestionar/', views.gestionar_horario, name='gestionar_horario'),

    # VM-502 — Mis citas (cliente)
    path('citas/', views.mis_citas, name='mis_citas'),

    # VM-502 — Agendar cita (cliente)
    path('citas/agendar/', views.agendar_cita, name='agendar_cita'),

    # VM-523 — Agendar cita para cliente (admin/vet)
    path('citas/agendar-admin/', views.agendar_cita_admin, name='agendar_cita_admin'),

    # VM-577 — Consultar y filtrar citas
    path('citas/consultar/', views.consultar_citas, name='consultar_citas'),

    # VM-581 — Reprogramar cita
    path('citas/reprogramar/<int:pk>/', views.reprogramar_cita, name='reprogramar_cita'),

    # VM-585 — Cancelar cita
    path('citas/cancelar/<int:pk>/', views.cancelar_cita, name='cancelar_cita'),

    # VM-589 — Cambiar estado
    path('citas/estado/<int:pk>/', views.cambiar_estado_cita, name='cambiar_estado_cita'),

    # VM-593 — Enviar recordatorio por correo
    path('citas/recordatorio/<int:pk>/', views.enviar_recordatorio, name='enviar_recordatorio'),

    # VM-599 — Historial por mascota
    path('mascotas/<int:pk>/historial/', views.historial_mascota, name='historial_mascota'),
]
