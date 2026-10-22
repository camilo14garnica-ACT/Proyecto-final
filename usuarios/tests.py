from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase
from django.contrib.auth.hashers import identify_hasher
from usuarios.models import Usuario
from usuarios.forms import CrearUsuarioForm


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
