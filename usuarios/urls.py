from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('iniciar-sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('login/', views.iniciar_sesion, name='login'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('cambiar-password/', auth_views.PasswordChangeView.as_view(
        template_name='usuarios/iniciar_sesion.html',
        success_url='/usuarios/perfil/'
    ), name='cambiar_password'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-veterinario/', views.panel_veterinario, name='panel_veterinario'),
]
