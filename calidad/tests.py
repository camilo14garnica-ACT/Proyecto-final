from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from mascotas.models import Producto
from calidad.models import EncuestaSatisfaccion, PQRS, LoteProducto, NoConformidad, Notificacion

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
        """Verifica que los modelos base se instancian correctamente."""
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

        # Notificación
        notif = Notificacion.objects.create(
            usuario=self.cliente_user,
            titulo='Prueba Notificación',
            mensaje='Mensaje de prueba',
            tipo=Notificacion.Tipo.INFO,
        )
        self.assertIn('Prueba Notificación', str(notif))

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
        """El administrador puede acceder a los listados de calidad y al dashboard."""
        self.client.login(username='admin_test', password='Password123!')

        rutas = [
            'admin_dashboard',
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
        self.assertEqual(res.status_code, 302)

    def test_senales_notificaciones_automaticas(self):
        """Verifica que las señales generen notificaciones internas automáticas."""
        # Al crear una PQRS, se notifica al admin y al cliente
        pqrs = PQRS.objects.create(
            tipo=PQRS.Tipo.RECLAMO,
            cliente=self.cliente_user,
            descripcion='No me enviaron la fórmula médica a tiempo.',
        )
        self.assertTrue(Notificacion.objects.filter(usuario=self.admin_user, tipo='PQRS').exists())
        self.assertTrue(Notificacion.objects.filter(usuario=self.cliente_user, tipo='PQRS').exists())

        # Al cambiar el estado de la PQRS, se notifica al cliente
        pqrs.estado = PQRS.Estado.EN_PROCESO
        pqrs.save()
        notif_actualizacion = Notificacion.objects.filter(
            usuario=self.cliente_user,
            titulo__contains='Actualización'
        )
        self.assertTrue(notif_actualizacion.exists())

        # Al registrar una encuesta con puntuación baja, se alerta al admin
        EncuestaSatisfaccion.objects.create(
            cliente=self.cliente_user,
            puntuacion=2,
            comentarios='Atención regular.',
        )
        self.assertTrue(
            Notificacion.objects.filter(
                usuario=self.admin_user,
                tipo='ENCUESTA',
                titulo__contains='Alerta'
            ).exists()
        )

    def test_vistas_notificaciones(self):
        """Prueba la bandeja de notificaciones y la acción de marcar como leída."""
        notif = Notificacion.objects.create(
            usuario=self.cliente_user,
            titulo='Aviso de prueba',
            mensaje='Contenido de aviso',
            leida=False,
        )
        self.client.login(username='cliente_test', password='Password123!')

        # Ver listado de notificaciones
        res = self.client.get(reverse('mis_notificaciones'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Aviso de prueba')

        # Marcar como leída
        res_post = self.client.post(reverse('marcar_notificacion_leida', kwargs={'pk': notif.pk}))
        self.assertEqual(res_post.status_code, 302)
        notif.refresh_from_db()
        self.assertTrue(notif.leida)

    def test_exportacion_excel(self):
        """Verifica que los endpoints de exportación en Excel generen archivos .xlsx."""
        self.client.login(username='admin_test', password='Password123!')

        rutas_excel = [
            'exportar_pqrs',
            'exportar_lotes',
            'exportar_encuestas',
            'exportar_no_conformidades',
        ]
        for ruta in rutas_excel:
            res = self.client.get(reverse(ruta))
            self.assertEqual(res.status_code, 200, f'Error en descarga Excel {ruta}')
            self.assertIn(
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                res['Content-Type']
            )

    def test_api_rest_calidad(self):
        """Verifica los endpoints de la API REST del módulo de calidad."""
        # 1. API PQRS
        self.client.login(username='cliente_test', password='Password123!')
        res_api_pqrs = self.client.get(reverse('api_pqrs_list_create'))
        self.assertEqual(res_api_pqrs.status_code, 200)

        # Crear PQRS vía API
        res_post_api = self.client.post(
            reverse('api_pqrs_list_create'),
            data={'tipo': 'PETICION', 'descripcion': 'Consulta por API REST.'},
            content_type='application/json',
        )
        self.assertEqual(res_post_api.status_code, 201)
        self.assertIn('Consulta por API REST', res_post_api.json()['descripcion'])

        # 2. API Notificaciones
        res_notif_api = self.client.get(reverse('api_notificaciones'))
        self.assertEqual(res_notif_api.status_code, 200)
        self.assertIn('notificaciones', res_notif_api.json())

        # 3. API Indicadores (Solo Admin)
        self.client.login(username='admin_test', password='Password123!')
        res_ind = self.client.get(reverse('api_indicadores'))
        self.assertEqual(res_ind.status_code, 200)
        data = res_ind.json()
        self.assertIn('kpis_generales', data)
        self.assertIn('tasa_resolucion_pqrs', data['kpis_generales'])
        self.assertIn('distribucion_tipo', data['pqrs'])
