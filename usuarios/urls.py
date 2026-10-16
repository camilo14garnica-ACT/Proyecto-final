from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('iniciar-sesion/', views.iniciar_sesion, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),

    # panel administrativo.
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-veterinario/', views.panel_veterinario, name='panel_veterinario'),

    # cambiar contraseña estando logueado
    path('perfil/cambiar-password/', auth_views.PasswordChangeView.as_view(template_name='usuarios/cambiar_password.html', success_url='/usuarios/perfil/password-cambiado/'),name='cambiar_password'),
    path('perfil/password-cambiado/', auth_views.PasswordChangeDoneView.as_view(template_name='usuarios/password_cambiado.html'), name='password_change_done'),

    # recuperar contraseña olvidada
    path('recuperar-password/', auth_views.PasswordResetView.as_view(template_name='usuarios/recuperar_password.html', email_template_name='usuarios/recuperar_password_email.html', success_url='/usuarios/recuperar-password/enviado/'),name='password_reset'),
    path('recuperar-password/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='usuarios/recuperar_password_enviado.html'), name='password_reset_done'),
    path('recuperar-password/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/recuperar_password_confirmar.html', success_url='/usuarios/recuperar-password/completo/'), name='password_reset_confirm'),
    path('recuperar-password/completo/', auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/recuperar_password_completo.html'),name='password_reset_complete'),
    
    # CRUD administrativo de usuarios
    
    path('administracion/usuarios/', views.listar_usuarios, name='lista_usuarios'),
    path('administracion/usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('administracion/usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    #Solicitar Eliminar cuenta propia
    path('perfil/confirmar-eliminacion/', views.confirmar_eliminacion_cuenta, name='confirmar_eliminacion_cuenta')
]

