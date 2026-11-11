from datetime import timedelta
from django.contrib import admin
from django.utils import timezone
from .models import EncuestaSatisfaccion, PQRS, LoteProducto, NoConformidad


class EstadoVencimientoFilter(admin.SimpleListFilter):
    """Filtro amigable para identificar rápidamente productos vencidos o próximos a vencer."""
    title = 'Alerta de vencimiento'
    parameter_name = 'alerta_vencimiento'

    def lookups(self, request, model_admin):
        return (
            ('vencidos', '⚠️ Ya vencidos'),
            ('por_vencer_30', '⏳ Por vencer (próximos 30 días)'),
            ('vigentes', '✅ Vigentes'),
        )

    def queryset(self, request, queryset):
        hoy = timezone.now().date()
        if self.value() == 'vencidos':
            return queryset.filter(fecha_vencimiento__lt=hoy)
        if self.value() == 'por_vencer_30':
            return queryset.filter(
                fecha_vencimiento__gte=hoy,
                fecha_vencimiento__lte=hoy + timedelta(days=30)
            )
        if self.value() == 'vigentes':
            return queryset.filter(fecha_vencimiento__gt=hoy + timedelta(days=30))
        return queryset


@admin.register(EncuestaSatisfaccion)
class EncuestaSatisfaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'cita', 'puntuacion', 'fecha')
    list_filter = ('puntuacion', 'fecha')
    search_fields = (
        'cliente__first_name',
        'cliente__last_name',
        'cliente__username',
        'cliente__Number_Document',
        'comentarios',
    )
    autocomplete_fields = ('cliente', 'cita')
    readonly_fields = ('fecha',)
    date_hierarchy = 'fecha'
    list_per_page = 25


@admin.register(PQRS)
class PQRSAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'estado', 'cliente', 'fecha')
    list_filter = ('tipo', 'estado', 'fecha')
    search_fields = (
        'cliente__first_name',
        'cliente__last_name',
        'cliente__username',
        'cliente__Number_Document',
        'descripcion',
    )
    autocomplete_fields = ('cliente',)
    readonly_fields = ('fecha',)
    date_hierarchy = 'fecha'
    list_per_page = 25


@admin.register(LoteProducto)
class LoteProductoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_lote',
        'producto',
        'fecha_vencimiento',
        'estado_calidad',
        'esta_vencido',
    )
    list_filter = (
        EstadoVencimientoFilter,
        'estado_calidad',
        'fecha_vencimiento',
    )
    search_fields = (
        'numero_lote',
        'producto__nombre',
    )
    autocomplete_fields = ('producto',)
    date_hierarchy = 'fecha_vencimiento'
    list_per_page = 25

    @admin.display(description='¿Vencido?', boolean=True)
    def esta_vencido(self, obj):
        return obj.fecha_vencimiento < timezone.now().date()


@admin.register(NoConformidad)
class NoConformidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'origen_display', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = (
        'descripcion_problema',
        'accion_correctiva',
        'pqrs__descripcion',
        'encuesta__comentarios',
        'pqrs__cliente__first_name',
        'pqrs__cliente__last_name',
        'encuesta__cliente__first_name',
        'encuesta__cliente__last_name',
    )
    autocomplete_fields = ('pqrs', 'encuesta')
    readonly_fields = ('fecha',)
    date_hierarchy = 'fecha'
    list_per_page = 25

    @admin.display(description='Origen')
    def origen_display(self, obj):
        if obj.pqrs:
            return f'PQRS #{obj.pqrs.pk}'
        if obj.encuesta:
            return f'Encuesta #{obj.encuesta.pk}'
        return '—'
