from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('iniciar-sesion/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),

    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-veterinario/', views.panel_veterinario, name='panel_veterinario'),

    # cambiar contraseña estando logueado
    path(
        'perfil/cambiar-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='usuarios/cambiar_password.html',
            success_url='/usuarios/perfil/password-cambiado/'
        ),
        name='cambiar_password',
    ),
    path(
        'perfil/password-cambiado/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='usuarios/password_cambiado.html'
        ),
        name='password_change_done',
    ),

    # recuperar contraseña olvidada
    path(
        'recuperar-password/',
        auth_views.PasswordResetView.as_view(
            template_name='usuarios/recuperar_password.html',
            email_template_name='usuarios/recuperar_password_email.html',
            success_url='/usuarios/recuperar-password/enviado/'
        ),
        name='password_reset',
    ),
    path(
        'recuperar-password/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/recuperar_password_enviado.html'
        ),
        name='password_reset_done',
    ),
    path(
        'recuperar-password/confirmar/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/recuperar_password_confirmar.html',
            success_url='/usuarios/recuperar-password/completo/'
        ),
        name='password_reset_confirm',
    ),
    path(
        'recuperar-password/completo/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/recuperar_password_completo.html'
        ),
        name='password_reset_complete',
    ),
]