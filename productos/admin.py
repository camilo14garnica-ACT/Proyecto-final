from django.contrib import admin

from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'estado')
	list_filter = ('estado',)
	search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'categoria', 'precio', 'stock', 'estado', 'fecha_registro')
	list_filter = ('categoria', 'estado')
	search_fields = ('nombre', 'descripcion', 'categoria__nombre')
	autocomplete_fields = ('categoria',)
	readonly_fields = ('fecha_registro',)