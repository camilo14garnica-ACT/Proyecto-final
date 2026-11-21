from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import ProductoForm
from .models import Categoria, Producto


class PruebasProductos(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Alimentos", estado="ACTIVO")
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="admin_test", password="Clave12345", rol="ADMIN"
        )

    def datos(self, **cambios):
        datos = {
            "nombre": "Concentrado",
            "descripcion": "Bulto de 10 kg",
            "categoria": self.categoria.pk,
            "precio": "25000",
            "stock": "10",
            "estado": "ACTIVO",
        }
        datos.update(cambios)
        return datos

    # --- VM-727: datos correctos e incorrectos ---
    def test_datos_correctos(self):
        self.assertTrue(ProductoForm(self.datos()).is_valid())

    def test_precio_con_punto_de_miles(self):
        self.assertTrue(ProductoForm(self.datos(precio="10.000")).is_valid())

    def test_nombre_vacio(self):
        self.assertFalse(ProductoForm(self.datos(nombre="")).is_valid())

    def test_precio_cero(self):
        self.assertFalse(ProductoForm(self.datos(precio="0")).is_valid())

    def test_stock_negativo(self):
        self.assertFalse(ProductoForm(self.datos(stock="-1")).is_valid())

    # --- VM-781: que la pantalla guarde o no guarde ---
    def test_admin_crea_producto(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("crear_producto"), self.datos())
        self.assertEqual(Producto.objects.count(), 1)

    def test_datos_malos_no_se_guardan(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("crear_producto"), self.datos(precio="0"))
        self.assertEqual(Producto.objects.count(), 0)	