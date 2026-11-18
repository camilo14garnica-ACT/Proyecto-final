from rest_framework import serializers
from django.utils import timezone
from .models import PQRS, EncuestaSatisfaccion, LoteProducto, NoConformidad, Notificacion


class PQRSSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = PQRS
        fields = [
            'id',
            'tipo',
            'tipo_display',
            'estado',
            'estado_display',
            'cliente',
            'cliente_nombre',
            'descripcion',
            'fecha',
        ]
        read_only_fields = ['id', 'estado', 'cliente', 'fecha']

    def get_cliente_nombre(self, obj):
        return obj.cliente.get_full_name() or obj.cliente.username


class PQRSCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PQRS
        fields = ['tipo', 'descripcion']


class EncuestaSatisfaccionSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()
    servicio_info = serializers.SerializerMethodField()

    class Meta:
        model = EncuestaSatisfaccion
        fields = [
            'id',
            'cliente',
            'cliente_nombre',
            'cita',
            'servicio_info',
            'puntuacion',
            'comentarios',
            'fecha',
        ]
        read_only_fields = ['id', 'cliente', 'fecha']

    def get_cliente_nombre(self, obj):
        return obj.cliente.get_full_name() or obj.cliente.username

    def get_servicio_info(self, obj):
        if obj.cita:
            return f"Cita #{obj.cita.pk} ({obj.cita.servicio.nombre if hasattr(obj.cita, 'servicio') and obj.cita.servicio else 'Atención médica'})"
        return "Atención General"


class LoteProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    estado_calidad_display = serializers.CharField(source='get_estado_calidad_display', read_only=True)
    esta_vencido = serializers.SerializerMethodField()
    dias_para_vencer = serializers.SerializerMethodField()

    class Meta:
        model = LoteProducto
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'numero_lote',
            'fecha_vencimiento',
            'estado_calidad',
            'estado_calidad_display',
            'esta_vencido',
            'dias_para_vencer',
        ]

    def get_esta_vencido(self, obj):
        return obj.fecha_vencimiento < timezone.now().date()

    def get_dias_para_vencer(self, obj):
        return (obj.fecha_vencimiento - timezone.now().date()).days


class NoConformidadSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    origen_detalle = serializers.SerializerMethodField()

    class Meta:
        model = NoConformidad
        fields = [
            'id',
            'pqrs',
            'encuesta',
            'origen_detalle',
            'descripcion_problema',
            'accion_correctiva',
            'estado',
            'estado_display',
            'fecha',
        ]

    def get_origen_detalle(self, obj):
        if obj.pqrs:
            return f"PQRS #{obj.pqrs.pk} ({obj.pqrs.get_tipo_display()})"
        if obj.encuesta:
            return f"Encuesta #{obj.encuesta.pk} ({obj.encuesta.puntuacion}★)"
        return "Auditoría Interna"


class NotificacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Notificacion
        fields = [
            'id',
            'usuario',
            'titulo',
            'mensaje',
            'tipo',
            'tipo_display',
            'leida',
            'enlace',
            'fecha',
        ]
        read_only_fields = ['id', 'usuario', 'fecha']

