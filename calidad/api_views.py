from datetime import timedelta
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PQRS, EncuestaSatisfaccion, LoteProducto, NoConformidad, Notificacion
from .serializers import (
    PQRSSerializer,
    PQRSCreateSerializer,
    EncuestaSatisfaccionSerializer,
    LoteProductoSerializer,
    NoConformidadSerializer,
    NotificacionSerializer,
)


class EsAdministradorOStaff(permissions.BasePermission):
    """Permiso personalizado para verificar si el usuario tiene rol ADMIN o is_staff."""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (
                getattr(request.user, 'rol', '') == 'ADMIN' or request.user.is_staff
            )
        )


class PQRSListCreateAPIView(generics.ListCreateAPIView):
    """
    Listar y crear PQRS vía API REST.
    - Clientes: ven únicamente sus propias PQRS.
    - Administradores: ven todas las PQRS registradas y pueden filtrar por tipo o estado.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PQRSCreateSerializer
        return PQRSSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PQRS.objects.select_related('cliente').all().order_by('-fecha')

        if getattr(user, 'rol', '') != 'ADMIN' and not user.is_staff:
            queryset = queryset.filter(cliente=user)

        tipo = self.request.query_params.get('tipo')
        estado = self.request.query_params.get('estado')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

    def create(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        self.perform_create(create_serializer)
        instance = create_serializer.instance
        output_serializer = PQRSSerializer(instance, context=self.get_serializer_context())
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PQRSDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y cierre de una PQRS."""
    serializer_class = PQRSSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'rol', '') == 'ADMIN' or user.is_staff:
            return PQRS.objects.select_related('cliente').all()
        return PQRS.objects.filter(cliente=user)


class EncuestaListCreateAPIView(generics.ListCreateAPIView):
    """Listar encuestas recibidas y radicar nuevas calificaciones."""
    serializer_class = EncuestaSatisfaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'rol', '') == 'ADMIN' or user.is_staff:
            return EncuestaSatisfaccion.objects.select_related('cliente', 'cita').all().order_by('-fecha')
        return EncuestaSatisfaccion.objects.filter(cliente=user).order_by('-fecha')

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)


class LoteProductoListCreateAPIView(generics.ListCreateAPIView):
    """Listado y registro de lotes de productos veterinarios (solo admin)."""
    serializer_class = LoteProductoSerializer
    permission_classes = [EsAdministradorOStaff]

    def get_queryset(self):
        queryset = LoteProducto.objects.select_related('producto').all().order_by('fecha_vencimiento')
        alerta = self.request.query_params.get('alerta')
        hoy = timezone.now().date()
        if alerta == 'vencidos':
            queryset = queryset.filter(fecha_vencimiento__lt=hoy)
        elif alerta == 'por_vencer':
            queryset = queryset.filter(fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=hoy + timedelta(days=30))
        elif alerta == 'vigentes':
            queryset = queryset.filter(fecha_vencimiento__gt=hoy + timedelta(days=30))
        return queryset


class LoteProductoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, edición y retiro de lotes de productos."""
    serializer_class = LoteProductoSerializer
    permission_classes = [EsAdministradorOStaff]
    queryset = LoteProducto.objects.select_related('producto').all()


class NoConformidadListCreateAPIView(generics.ListCreateAPIView):
    """Listado y registro de no conformidades internas (solo admin)."""
    serializer_class = NoConformidadSerializer
    permission_classes = [EsAdministradorOStaff]

    def get_queryset(self):
        queryset = NoConformidad.objects.select_related('pqrs', 'encuesta').all().order_by('-fecha')
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset


class NoConformidadDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle y seguimiento correctivo de una no conformidad."""
    serializer_class = NoConformidadSerializer
    permission_classes = [EsAdministradorOStaff]
    queryset = NoConformidad.objects.select_related('pqrs', 'encuesta').all()


class NotificacionesListAPIView(APIView):
    """Listado de notificaciones del usuario autenticado y acción de marcar como leídas."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Notificacion.objects.filter(usuario=request.user)
        no_leidas = qs.filter(leida=False).count()
        notificaciones = qs.order_by('-fecha')[:30]
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response({
            'conteo_no_leidas': no_leidas,
            'notificaciones': serializer.data,
        })

    def post(self, request):
        """Marca una o todas las notificaciones como leídas."""
        notificacion_id = request.data.get('notificacion_id')
        if notificacion_id:
            actualizados = Notificacion.objects.filter(
                id=notificacion_id, usuario=request.user
            ).update(leida=True)
            return Response({'mensaje': 'Notificación marcada como leída.', 'afectadas': actualizados})
        else:
            actualizados = Notificacion.objects.filter(
                usuario=request.user, leida=False
            ).update(leida=True)
            return Response({'mensaje': 'Todas las notificaciones marcadas como leídas.', 'afectadas': actualizados})


class IndicadoresAPIView(APIView):
    """
    Retorna métricas cuantitativas e indicadores clave (KPIs) en tiempo real
    del Sistema de Gestión de Calidad Mascott.
    """
    permission_classes = [EsAdministradorOStaff]

    def get(self, request):
        hoy = timezone.now().date()
        en_30_dias = hoy + timedelta(days=30)

        # 1. Indicadores de PQRS
        total_pqrs = PQRS.objects.count()
        pqrs_abiertas = PQRS.objects.filter(estado=PQRS.Estado.ABIERTA).count()
        pqrs_en_proceso = PQRS.objects.filter(estado=PQRS.Estado.EN_PROCESO).count()
        pqrs_cerradas = PQRS.objects.filter(estado=PQRS.Estado.CERRADA).count()
        tasa_resolucion_pqrs = round((pqrs_cerradas / total_pqrs * 100), 1) if total_pqrs > 0 else 0.0

        pqrs_por_tipo = {
            'peticiones': PQRS.objects.filter(tipo=PQRS.Tipo.PETICION).count(),
            'quejas': PQRS.objects.filter(tipo=PQRS.Tipo.QUEJA).count(),
            'reclamos': PQRS.objects.filter(tipo=PQRS.Tipo.RECLAMO).count(),
            'sugerencias': PQRS.objects.filter(tipo=PQRS.Tipo.SUGERENCIA).count(),
        }

        # 2. Indicadores de Satisfacción
        total_encuestas = EncuestaSatisfaccion.objects.count()
        promedio_satisfaccion = EncuestaSatisfaccion.objects.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0.0
        distribucion_estrellas = {
            f'{i}_estrellas': EncuestaSatisfaccion.objects.filter(puntuacion=i).count()
            for i in range(1, 6)
        }

        # 3. Control de Lotes
        total_lotes = LoteProducto.objects.count()
        lotes_vencidos = LoteProducto.objects.filter(fecha_vencimiento__lt=hoy).count()
        lotes_por_vencer = LoteProducto.objects.filter(
            fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=en_30_dias
        ).count()
        lotes_vigentes = LoteProducto.objects.filter(fecha_vencimiento__gt=en_30_dias).count()

        # 4. No Conformidades
        total_nc = NoConformidad.objects.count()
        nc_abiertas = NoConformidad.objects.filter(estado=NoConformidad.Estado.ABIERTA).count()
        nc_en_proceso = NoConformidad.objects.filter(estado=NoConformidad.Estado.EN_PROCESO).count()
        nc_resueltas = NoConformidad.objects.filter(estado=NoConformidad.Estado.RESUELTA).count()

        return Response({
            'kpis_generales': {
                'total_pqrs': total_pqrs,
                'tasa_resolucion_pqrs': f"{tasa_resolucion_pqrs}%",
                'satisfaccion_promedio': round(promedio_satisfaccion, 2),
                'total_evaluaciones': total_encuestas,
                'lotes_en_riesgo': lotes_vencidos + lotes_por_vencer,
                'no_conformidades_pendientes': nc_abiertas + nc_en_proceso,
            },
            'pqrs': {
                'total': total_pqrs,
                'abiertas': pqrs_abiertas,
                'en_proceso': pqrs_en_proceso,
                'cerradas': pqrs_cerradas,
                'distribucion_tipo': pqrs_por_tipo,
            },
            'satisfaccion': {
                'promedio': round(promedio_satisfaccion, 2),
                'total_encuestas': total_encuestas,
                'distribucion_estrellas': distribucion_estrellas,
            },
            'lotes': {
                'total': total_lotes,
                'vigentes': lotes_vigentes,
                'por_vencer_30d': lotes_por_vencer,
                'vencidos': lotes_vencidos,
            },
            'no_conformidades': {
                'total': total_nc,
                'abiertas': nc_abiertas,
                'en_proceso': nc_en_proceso,
                'resueltas': nc_resueltas,
            },
            'fecha_generacion': timezone.now().isoformat(),
        })
