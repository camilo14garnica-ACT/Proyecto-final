from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path(
        'iniciar-sesion/',
        LoginView.as_view(
            template_name='usuarios/iniciar_sesion.html',
            next_page='crear_usuario',
        ),
        name='iniciar_sesion',
    ),
]
