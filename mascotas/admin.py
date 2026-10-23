from django.contrib import admin
from .models import Especie, Raza, Mascota, Servicio, Cita


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'estado')
    search_fields = ('nombre',)
    list_filter = ('estado',)


@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'estado')
    search_fields = ('nombre',)
    list_filter = ('especie', 'estado')


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'Cliente', 'estado')
    search_fields = ('nombre', 'Cliente__first_name', 'Cliente__last_name')
    list_filter = ('especie', 'estado')


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion_minutos', 'precio', 'estado')
    search_fields = ('nombre',)
    list_filter = ('estado',)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'servicio', 'veterinario', 'fecha_hora', 'estado')
    list_filter = ('estado', 'servicio', 'fecha_hora')
    search_fields = ('mascota__nombre', 'veterinario__first_name', 'veterinario__last_name')
    date_hierarchy = 'fecha_hora'
    ordering = ('-fecha_hora',)
