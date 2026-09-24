"""
URL configuration for app project.
"""
from django.contrib import admin
from django.urls import path, include
from usuarios import views as usuarios_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', usuarios_views.inicio, name='inicio'),
    path('usuarios/', include('usuarios.urls')),
]
