from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from mascotas.models import Producto
from calidad.models import EncuestaSatisfaccion, PQRS, LoteProducto, NoConformidad

Usuario = get_user_model()


class CalidadModuloTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Usuario Administrador
        self.admin_user = Usuario.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Password123!',
            rol=Usuario.Rol.ADMIN,
            is_staff=True,
            first_name='Admin',
            last_name='Test',
            Number_Document='10000001',
        )

        # Usuario Cliente
        self.cliente_user = Usuario.objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='Password123!',
            rol=Usuario.Rol.CLIENTE,
            first_name='Cliente',
            last_name='Prueba',
            Number_Document='20000002',
        )

        # Producto para Lotes
        self.producto = Producto.objects.create(
            nombre='Vacuna Antirrábica',
            precio=45000.00,
            stock=10,
        )

    def test_creacion_modelos_calidad(self):
        """Verifica que los 4 modelos se instancian correctamente."""
        # PQRS
        pqrs = PQRS.objects.create(
            tipo=PQRS.Tipo.QUEJA,
            cliente=self.cliente_user,
            descripcion='La cita se demoró 20 minutos en iniciar.',
        )
        self.assertIn('Queja', str(pqrs))

        # Encuesta
        encuesta = EncuestaSatisfaccion.objects.create(
            cliente=self.cliente_user,
            puntuacion=4,
            comentarios='Buena atención.',
        )
        self.assertIn('4★', str(encuesta))

        # Lote
        lote = LoteProducto.objects.create(
            producto=self.producto,
            numero_lote='LOT-TEST-99',
            fecha_vencimiento=date.today() + timedelta(days=60),
            estado_calidad=LoteProducto.EstadoCalidad.APROBADO,
        )
        self.assertIn('LOT-TEST-99', str(lote))

        # No Conformidad vinculada a PQRS
        nc = NoConformidad.objects.create(
            pqrs=pqrs,
            descripcion_problema='Retraso en agenda médica.',
            accion_correctiva='Ajustar tiempos entre consultas.',
            estado=NoConformidad.Estado.ABIERTA,
        )
        self.assertIn('NC #', str(nc))

    def test_cliente_puede_radicar_pqrs(self):
        """Un cliente autenticado puede radicar una PQRS vía formulario."""
        self.client.login(username='cliente_test', password='Password123!')
        url = reverse('radicar_pqrs')

        response = self.client.post(url, {
            'tipo': PQRS.Tipo.PETICION,
            'descripcion': 'Deseo solicitar copia de la historia clínica de mi perro.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PQRS.objects.filter(cliente=self.cliente_user).count(), 1)

    def test_cliente_puede_ver_mis_pqrs(self):
        """El cliente puede ver el listado de sus propias PQRS."""
        PQRS.objects.create(
            tipo=PQRS.Tipo.SUGERENCIA,
            cliente=self.cliente_user,
            descripcion='Poner dispensador de agua para mascotas.',
        )
        self.client.login(username='cliente_test', password='Password123!')
        response = self.client.get(reverse('mis_pqrs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Poner dispensador de agua')

    def test_cliente_puede_enviar_encuesta(self):
        """Un cliente puede enviar una encuesta de satisfacción."""
        self.client.login(username='cliente_test', password='Password123!')
        response = self.client.post(reverse('crear_encuesta'), {
            'puntuacion': 5,
            'comentarios': 'Excelente servicio médico.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EncuestaSatisfaccion.objects.count(), 1)

    def test_admin_acceso_panel_calidad(self):
        """El administrador puede acceder a los listados de calidad."""
        self.client.login(username='admin_test', password='Password123!')

        rutas = [
            'admin_pqrs_list',
            'admin_lotes_list',
            'admin_no_conformidades_list',
            'admin_encuestas_list',
        ]
        for ruta in rutas:
            res = self.client.get(reverse(ruta))
            self.assertEqual(res.status_code, 200, f'Fallo en ruta {ruta}')

    def test_cliente_no_puede_acceder_admin_calidad(self):
        """Un cliente no tiene permiso para entrar al panel administrativo de calidad."""
        self.client.login(username='cliente_test', password='Password123!')
        res = self.client.get(reverse('admin_pqrs_list'))
        # Redirige a inicio por @solo_admin
        self.assertEqual(res.status_code, 302)
