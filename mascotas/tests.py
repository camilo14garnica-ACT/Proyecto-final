from types import SimpleNamespace

from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.test import override_settings
from django.urls import NoReverseMatch, resolve, reverse


class RutasMascotasTests(SimpleTestCase):

    def test_ruta_editar_mascota_apunta_a_vista_editar(self):
        url = reverse('editar_mascota', args=[1])

        self.assertEqual(resolve(url).url_name, 'editar_mascota')
        self.assertEqual(
            resolve(url).func.view_class.__name__,
            'EditarMascotaView',
        )

    def test_ruta_eliminar_mascota_apunta_a_vista_eliminar(self):
        url = reverse('eliminar_mascota', args=[1])

        self.assertEqual(resolve(url).url_name, 'eliminar_mascota')
        self.assertEqual(
            resolve(url).func.view_class.__name__,
            'EliminarMascotaView',
        )

    def test_rutas_del_crud_de_razas_resuelven_a_vistas_genericas(self):
        rutas = (
            ('lista_razas', [], 'ListaRazasView'),
            ('registrar_raza', [], 'CrearRazaView'),
            ('editar_raza', [1], 'EditarRazaView'),
            ('eliminar_raza', [1], 'EliminarRazaView'),
        )
        for nombre, argumentos, vista in rutas:
            with self.subTest(nombre=nombre):
                resolucion = resolve(reverse(nombre, args=argumentos))
                self.assertEqual(resolucion.func.view_class.__name__, vista)

    def test_rutas_del_crud_de_mascotas_resuelven_a_vistas_genericas(self):
        rutas = (
            ('lista_mascotas', [], 'ListaMascotasView'),
            ('registrar_mascota', [], 'CrearMascotaView'),
            ('editar_mascota', [1], 'EditarMascotaView'),
            ('eliminar_mascota', [1], 'EliminarMascotaView'),
        )
        for nombre, argumentos, vista in rutas:
            with self.subTest(nombre=nombre):
                resolucion = resolve(reverse(nombre, args=argumentos))
                self.assertEqual(resolucion.func.view_class.__name__, vista)

    def test_rutas_del_carrito_no_estan_habilitadas(self):
        for route_name in (
            'ver_carrito',
            'agregar_carrito',
            'quitar_carrito',
            'pagar_carrito',
        ):
            with self.subTest(route_name=route_name):
                with self.assertRaises(NoReverseMatch):
                    reverse(route_name)


class ListaMascotasTemplateTests(SimpleTestCase):

    @override_settings(
        STORAGES={
            'default': {
                'BACKEND': 'django.core.files.storage.FileSystemStorage',
            },
            'staticfiles': {
                'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
            },
        }
    )
    def test_muestra_las_mascotas_recibidas_en_el_contexto(self):
        mascota = SimpleNamespace(
            pk=1,
            nombre='Luna',
            especie=SimpleNamespace(nombre='Perro'),
            raza=SimpleNamespace(nombre='Mestiza'),
            estado='ACTIVO',
            get_sexo_display=lambda: 'Hembra',
        )

        contenido = render_to_string(
            'mascotas/lista_mascotas.html',
            {
                'base_template': 'mascotas/base_cliente.html',
                'titulo': 'Mis mascotas',
                'mascotas': [mascota],
                'es_personal': False,
            },
        )

        self.assertIn('Luna', contenido)
        self.assertIn('Perro', contenido)
        self.assertIn('Mestiza', contenido)
