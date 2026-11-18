from django.urls import path
from . import api_views

urlpatterns = [
    # PQRS API
    path('pqrs/', api_views.PQRSListCreateAPIView.as_view(), name='api_pqrs_list_create'),
    path('pqrs/<int:pk>/', api_views.PQRSDetailAPIView.as_view(), name='api_pqrs_detail'),

    # Encuestas de Satisfacción API
    path('encuestas/', api_views.EncuestaListCreateAPIView.as_view(), name='api_encuestas_list_create'),

    # Lotes de Productos API (Admin)
    path('lotes/', api_views.LoteProductoListCreateAPIView.as_view(), name='api_lotes_list_create'),
    path('lotes/<int:pk>/', api_views.LoteProductoDetailAPIView.as_view(), name='api_lotes_detail'),

    # No Conformidades API (Admin)
    path('no-conformidades/', api_views.NoConformidadListCreateAPIView.as_view(), name='api_no_conformidades_list_create'),
    path('no-conformidades/<int:pk>/', api_views.NoConformidadDetailAPIView.as_view(), name='api_no_conformidades_detail'),

    # Notificaciones API
    path('notificaciones/', api_views.NotificacionesListAPIView.as_view(), name='api_notificaciones'),

    # Indicadores & KPIs de Calidad API (Admin)
    path('indicadores/', api_views.IndicadoresAPIView.as_view(), name='api_indicadores'),
]

