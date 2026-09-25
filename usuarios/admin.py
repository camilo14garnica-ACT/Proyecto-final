from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Mascota, Cita, HistorialMedico

admin.site.register(Usuario, UserAdmin)

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'propietario', 'peso', 'fecha_nacimiento')
    search_fields = ('nombre', 'propietario__username', 'propietario__first_name', 'propietario__last_name')
    list_filter = ('especie',)

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'veterinario', 'fecha_hora', 'estado')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('mascota__nombre', 'veterinario__username', 'motivo')

@admin.register(HistorialMedico)
class HistorialMedicoAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'veterinario', 'fecha')
    search_fields = ('mascota__nombre', 'diagnostico')
    list_filter = ('fecha',)

