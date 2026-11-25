from django.contrib import admin
from .models import Proveedor, OrdenCompra, ItemOrdenCompra, Lote, RecepcionCompra, ItemRecepcion


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'email', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


class ItemOrdenInline(admin.TabularInline):
    model = ItemOrdenCompra
    extra = 1


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('pk', 'proveedor', 'estado', 'fecha_orden', 'fecha_esperada', 'creada_por')
    list_filter = ('estado', 'proveedor')
    search_fields = ('proveedor__nombre',)
    inlines = [ItemOrdenInline]


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('producto', 'numero_lote', 'cantidad', 'fecha_ingreso', 'fecha_vence', 'vencido')
    list_filter = ('producto', 'fecha_vence')
    search_fields = ('producto__nombre', 'numero_lote')


@admin.register(RecepcionCompra)
class RecepcionAdmin(admin.ModelAdmin):
    list_display = ('orden', 'recibido_por', 'fecha_recepcion')
