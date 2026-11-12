from django.urls import path
from . import views

urlpatterns = [
    # VM-271/274 — Órdenes de compra
    path('ordenes/', views.lista_ordenes, name='lista_ordenes'),
    path('ordenes/crear/', views.crear_orden, name='crear_orden'),
    path('ordenes/<int:pk>/', views.detalle_orden, name='detalle_orden'),
    path('ordenes/<int:pk>/recibir/', views.recibir_orden, name='recibir_orden'),
    path('ordenes/<int:pk>/cancelar/', views.cancelar_orden, name='cancelar_orden'),

    # VM-273 — Lotes
    path('lotes/', views.lista_lotes, name='lista_lotes'),

    # Proveedores
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
]
