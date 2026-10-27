from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Páginas principales
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('iniciar-sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('login/', views.iniciar_sesion, name='login'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/eliminar-cuenta/', views.solicitar_eliminacion_cuenta, name='solicitar_eliminacion_cuenta'),

    # Paneles por rol
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-veterinario/', views.panel_veterinario, name='panel_veterinario'),

    # Cambiar contraseña estando logueado
    path('perfil/cambiar-password/', auth_views.PasswordChangeView.as_view(template_name='usuarios/cambiar_password.html', success_url='/usuarios/perfil/password-cambiado/'), name='cambiar_password'),
    path('perfil/password-cambiado/', auth_views.PasswordChangeDoneView.as_view(template_name='usuarios/password_cambiado.html'), name='password_change_done'),

    # Recuperar contraseña con código de 6 dígitos
    path('recuperar-password/', views.recuperar_password_solicitar, name='recuperar_password_solicitar'),
    path('recuperar-password/codigo/', views.recuperar_password_codigo, name='recuperar_password_codigo'),
    path('recuperar-password/nueva/', views.recuperar_password_nueva, name='recuperar_password_nueva'),
    path('recuperar-password/completo/', views.recuperar_password_completo, name='recuperar_password_completo'),

    # Alias para compatibilidad con el link de "olvidé contraseña" del login
    path('recuperar-password/enviado/', views.recuperar_password_codigo, name='password_reset_done'),
    path('recuperar-password/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/recuperar_password_confirmar.html', success_url='/usuarios/recuperar-password/completo/'), name='password_reset_confirm'),

    # CRUD administrativo de usuarios
    path('administracion/usuarios/', views.listar_usuarios, name='lista_usuarios'),
    path('administracion/usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('administracion/usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('perfil/confirmar-eliminacion/<int:pk>/', views.confirmar_eliminacion_cuenta, name='confirmar_eliminacion_cuenta'),
    
    #Perfil de admin y veterinaria para editar perfil
    path('editar_perfil_admin/', views.panel_perfil, name='editar_perfil_admin')
]
