from django.contrib import admin

from .models import Cita, CategoriaServicio, DiaNoDisponible, HorarioVeterinario, Servicio

@admin.register(CategoriaServicio)
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado")
    list_filter = ("estado",)
    search_fields =("nombre",)
    
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "bloques", "estado")
    list_filter = ("categoria", "estado")
    search_fields = ("nombre",)
    
    
@admin.register(HorarioVeterinario)
class HorarioVeterinarioAdmin(admin.ModelAdmin):
    list_display = ("veterinario", "dia_semana", "hora_inicio", "hora_fin", "activo")
    list_filter = ("veterinario", "dia_semana", "activo")
 
 
@admin.register(DiaNoDisponible)
class DiaNoDisponibleAdmin(admin.ModelAdmin):
    list_display = ("veterinario", "fecha_inicio", "fecha_fin", "motivo")
    list_filter = ("veterinario",)   

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora_inicio", "mascota", "servicio", "veterinario", "estado")
    list_filter = ("estado", "veterinario", "servicio", "fecha")
    search_fields = ("mascota__nombre", "cliente__username", "cliente__first__name", "cliente_last_name")
    date_hierarchy = "fecha"
    
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado")
    list_filter = ("estado",)
    search_fields = ("nombre",)