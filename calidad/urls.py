from django.urls import path
from . import views

urlpatterns = [
    # Clientes / Frontend
    path('pqrs/nueva/', views.radicar_pqrs, name='radicar_pqrs'),
    path('mis-pqrs/', views.mis_pqrs, name='mis_pqrs'),
    path('encuestas/nueva/', views.crear_encuesta, name='crear_encuesta'),

    # Panel de administración interno
    path('admin/pqrs/', views.admin_pqrs_list, name='admin_pqrs_list'),
    path('admin/pqrs/<int:pk>/', views.admin_pqrs_detalle, name='admin_pqrs_detalle'),

    path('admin/lotes/', views.admin_lotes_list, name='admin_lotes_list'),
    path('admin/lotes/nuevo/', views.admin_lote_crear, name='admin_lote_crear'),
    path('admin/lotes/editar/<int:pk>/', views.admin_lote_editar, name='admin_lote_editar'),

    path('admin/no-conformidades/', views.admin_no_conformidades_list, name='admin_no_conformidades_list'),
    path('admin/no-conformidades/nueva/', views.admin_no_conformidad_crear, name='admin_no_conformidad_crear'),
    path('admin/no-conformidades/editar/<int:pk>/', views.admin_no_conformidad_editar, name='admin_no_conformidad_editar'),

    path('admin/encuestas/', views.admin_encuestas_list, name='admin_encuestas_list'),
]

