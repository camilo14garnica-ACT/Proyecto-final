from django.contrib import admin
from .models import Especie, Raza, Mascota

@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'estado')

@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'estado')

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'Cliente', 'estado')

# Register your models here.
