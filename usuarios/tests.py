from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase

from .models import Usuario, UsuarioSyncPendiente
from .sync import procesar_pendientes


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
