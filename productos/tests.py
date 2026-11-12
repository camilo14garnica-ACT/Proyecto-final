from decimal import Decimal

from django.test import TestCase

from .models import Categoria, Producto


class ProductoTests(TestCase):
	def setUp(self):
		self.categoria = Categoria.objects.create(nombre='Farmacia')

	def test_producto_se_asocia_a_categoria_y_refleja_stock_agotado(self):
		producto = Producto.objects.create(
			nombre='Vacuna',
			categoria=self.categoria,
			precio=Decimal('12.50'),
			stock=0,
		)

		self.assertEqual(producto.categoria, self.categoria)
		self.assertTrue(producto.agotado)
		self.assertEqual(str(producto), 'Vacuna')

	def test_producto_con_stock_no_esta_agotado(self):
		producto = Producto.objects.create(
			nombre='Alimento',
			categoria=self.categoria,
			precio=Decimal('45.00'),
			stock=4,
		)

		self.assertFalse(producto.agotado)
