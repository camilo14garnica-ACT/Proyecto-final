from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase
from django.contrib.auth.hashers import identify_hasher
from usuarios.models import Usuario, UsuarioSyncPendiente
from usuarios.forms import CrearUsuarioForm
from .sync import procesar_pendientes


class PasswordEncryptionTests(TestCase):

    def test_usuario_save_cifra_contrasena_en_texto_plano(self):
        """Verifica que guardar un usuario con contraseña plana se cifra con el hasher por defecto (PBKDF2)."""
        usuario = Usuario.objects.create(
            username='cliente_test',
            password='Password123Segura!',
            rol=Usuario.Rol.CLIENTE
        )
        # La contraseña en base de datos no debe ser el texto plano
        self.assertNotEqual(usuario.password, 'Password123Segura!')
        # Debe ser identificada por el hasher por defecto (PBKDF2)
        hasher = identify_hasher(usuario.password)
        self.assertEqual(hasher.algorithm, 'pbkdf2_sha256')
        # check_password debe validar la contraseña correctamente
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
        # Guardar nuevamente sin cambiar la contraseña
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


class SincronizacionUsuarioTests(TestCase):
    def crear_usuario(self):
        return Usuario.objects.create_user(
            username='cliente-prueba',
            password='ClaveDePrueba-123',
            email='cliente@example.com',
        )

    def test_guardar_usuario_crea_un_pendiente_local(self):
        usuario = self.crear_usuario()

        pendiente = UsuarioSyncPendiente.objects.get(sync_uuid=usuario.sync_uuid)

        self.assertEqual(pendiente.operacion, UsuarioSyncPendiente.Operacion.GUARDAR)

    def test_ediciones_se_consolidan_en_un_pendiente(self):
        usuario = self.crear_usuario()
        pendiente = UsuarioSyncPendiente.objects.get(sync_uuid=usuario.sync_uuid)
        revision_inicial = pendiente.revision

        usuario.first_name = 'Nombre actualizado'
        usuario.save()

        pendiente.refresh_from_db()
        self.assertEqual(UsuarioSyncPendiente.objects.count(), 1)
        self.assertEqual(pendiente.revision, revision_inicial + 1)

    @patch('usuarios.sync.copiar_usuario_a_remota')
    def test_exito_remoto_elimina_el_pendiente(self, copiar_usuario):
        usuario = self.crear_usuario()

        resultado = procesar_pendientes()

        copiar_usuario.assert_called_once_with(usuario.sync_uuid)
        self.assertEqual(resultado['sincronizados'], 1)
        self.assertFalse(UsuarioSyncPendiente.objects.exists())

    @patch('usuarios.sync.eliminar_usuario_remoto')
    def test_eliminar_usuario_encola_borrado_remoto(self, eliminar_usuario):
        usuario = self.crear_usuario()
        sync_uuid = usuario.sync_uuid
        usuario.delete()

        pendiente = UsuarioSyncPendiente.objects.get(sync_uuid=sync_uuid)
        self.assertEqual(pendiente.operacion, UsuarioSyncPendiente.Operacion.ELIMINAR)

        resultado = procesar_pendientes()

        eliminar_usuario.assert_called_once_with(sync_uuid)
        self.assertEqual(resultado['sincronizados'], 1)
        self.assertFalse(UsuarioSyncPendiente.objects.exists())

    @patch('usuarios.sync.copiar_usuario_a_remota', side_effect=OperationalError('sin conexión'))
    def test_error_remoto_conserva_pendiente_y_programa_reintento(self, copiar_usuario):
        usuario = self.crear_usuario()

        resultado = procesar_pendientes()

        pendiente = UsuarioSyncPendiente.objects.get(sync_uuid=usuario.sync_uuid)
        self.assertEqual(resultado['fallidos'], 1)
        self.assertEqual(pendiente.intentos, 1)
        self.assertIsNotNone(pendiente.reintentar_despues)
