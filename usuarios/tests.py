from unittest.mock import Mock, patch
from types import SimpleNamespace

from django.db import OperationalError
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse
from django.contrib.auth.hashers import identify_hasher
from usuarios.models import Usuario, UsuarioSyncPendiente
from usuarios.forms import CrearUsuarioForm
from usuarios.views import mi_perfil, panel_perfil, solicitar_eliminacion_cuenta


class PasswordEncryptionTests(TestCase):

    def test_usuario_save_cifra_contrasena_en_texto_plano(self):
        """Verifica que guardar un usuario con contraseña plana se cifra con el hasher por defecto (PBKDF2)."""
        usuario = Usuario.objects.create(
            username='cliente_test',
            password='Password123Segura!',
            rol=Usuario.Rol.CLIENTE
        )
        self.assertNotEqual(usuario.password, 'Password123Segura!')
        hasher = identify_hasher(usuario.password)
        self.assertEqual(hasher.algorithm, 'pbkdf2_sha256')
        self.assertTrue(usuario.check_password('Password123Segura!'))

    def test_administrador_createsuperuser_cifra_contrasena(self):
        """Verifica que un administrador/superuser cifra su contraseña y sincroniza su rol."""
        admin = Usuario.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='Sistema'
        )
        self.assertNotEqual(admin.password, 'AdminPassword123!')
        hasher = identify_hasher(admin.password)
        self.assertEqual(hasher.algorithm, 'pbkdf2_sha256')
        self.assertTrue(admin.check_password('AdminPassword123!'))
        self.assertEqual(admin.rol, Usuario.Rol.ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_no_doble_cifrado(self):
        """Verifica que llamar save() en un usuario ya cifrado no altera su hash ni rompe check_password."""
        usuario = Usuario.objects.create_user(
            username='user_doble_save',
            password='ClaveValida987!'
        )
        pwd_hash_inicial = usuario.password
        usuario.first_name = 'Nuevo Nombre'
        usuario.save()
        self.assertEqual(usuario.password, pwd_hash_inicial)
        self.assertTrue(usuario.check_password('ClaveValida987!'))

    def test_formulario_crear_usuario_cifra_contrasena(self):
        """Verifica que CrearUsuarioForm valida y cifra la contraseña al guardar."""
        form_data = {
            'username': 'juan_perez',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'email': 'juan@example.com',
            'Document_Type': 'CC',
            'Number_Document': '1234567890',
            'Date_of_birth': '1995-05-15',
            'password': 'SuperPassword789!',
            'password_confirmacion': 'SuperPassword789!'
        }
        form = CrearUsuarioForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()
        self.assertNotEqual(usuario.password, 'SuperPassword789!')
        self.assertTrue(usuario.check_password('SuperPassword789!'))
        hasher = identify_hasher(usuario.password)
        self.assertEqual(hasher.algorithm, 'pbkdf2_sha256')


class SolicitarEliminacionCuentaTests(SimpleTestCase):

    def setUp(self):
        self.url = reverse('solicitar_eliminacion_cuenta')
        self.user = SimpleNamespace(
            is_authenticated=True,
            username='cliente_test',
            is_superuser=False,
            es_admin=lambda: False,
            es_veterinario=lambda: False,
            delete=Mock(),
        )

    def test_muestra_confirmacion_sin_parametros_de_url(self):
        request = RequestFactory().get(self.url)
        request.user = self.user

        response = solicitar_eliminacion_cuenta(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eliminar mi cuenta')
        self.assertContains(response, self.url)

    def test_elimina_la_cuenta_solo_con_confirmacion(self):
        request = RequestFactory().post(
            self.url,
            {'confirmar_eliminacion': 'SI'},
        )
        request.user = self.user

        with patch('usuarios.views.logout') as logout, patch('usuarios.views.messages.success'):
            response = solicitar_eliminacion_cuenta(request)

        self.assertEqual(response.status_code, 302)
        self.user.delete.assert_called_once_with()
        logout.assert_called_once_with(request)


class PerfilPorRolTests(SimpleTestCase):

    def test_usuario_no_cliente_desde_mi_perfil_va_a_su_perfil(self):
        request = RequestFactory().get(reverse('mi_perfil'))
        request.user = SimpleNamespace(
            rol=Usuario.Rol.ADMIN,
            is_authenticated=True,
        )

        response = mi_perfil(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('editar_perfil_admin'))

    def test_cliente_desde_perfil_admin_va_a_mi_perfil(self):
        request = RequestFactory().get(reverse('editar_perfil_admin'))
        request.user = SimpleNamespace(
            rol=Usuario.Rol.CLIENTE,
            is_authenticated=True,
        )

        response = panel_perfil(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('mi_perfil'))
