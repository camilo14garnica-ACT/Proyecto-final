from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario




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
    
    