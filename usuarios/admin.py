from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Mascota, Cita, HistorialMedico

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'Document_Type', 'Number_Document', 'Date_of_birth')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'Document_Type', 'Number_Document', 'Date_of_birth')
        }),
    )

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

<<<<<<< HEAD
=======



@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active')
    list_filter = ('rol', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Rol y datos personales', {
            'fields' :( 'rol', 'Document_Type', 'Number_Document', 'Date_of_birth'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rol y datos', {
            'fields': ('rol', 'email', 'first_name', 'last_name',)
        }),
    )
    
    
>>>>>>> 4877cb84795950d378de70a9c5694b3ce7374643
