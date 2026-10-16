from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from .views import iniciar_sesion


class InicioSesionTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_admin_se_redirige_a_su_panel_al_iniciar_sesion(self):
        request = self.factory.post(reverse('login'))
        request.user = AnonymousUser()
        usuario = SimpleNamespace(rol='ADMIN')
        form = Mock()
        form.is_valid.return_value = True
        form.get_user.return_value = usuario

        with patch('usuarios.views.AuthenticationForm', return_value=form):
            with patch('usuarios.views.login') as login:
                response = iniciar_sesion(request)

        login.assert_called_once_with(request, usuario)
        self.assertRedirects(response, reverse('panel_admin'), fetch_redirect_response=False)

    def test_admin_ya_autenticado_se_redirige_a_su_panel(self):
        request = self.factory.get(reverse('login'))
        request.user = SimpleNamespace(is_authenticated=True, rol='ADMIN')

        response = iniciar_sesion(request)

        self.assertRedirects(response, reverse('panel_admin'), fetch_redirect_response=False)
