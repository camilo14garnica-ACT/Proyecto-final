from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('exportar/', views.exportar_csv, name='exportar'),
    path('guardar/', views.guardar_reporte, name='guardar'),
]