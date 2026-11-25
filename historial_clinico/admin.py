from django.contrib import admin

from .models import RegistroClinico


@admin.register(RegistroClinico)
class RegistroClinicoAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'fecha', 'motivo', 'registrado_por', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('mascota__nombre', 'motivo', 'diagnostico')