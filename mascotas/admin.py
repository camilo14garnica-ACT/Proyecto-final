from django.contrib import admin
from .models import Especie, Raza, Mascota


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


