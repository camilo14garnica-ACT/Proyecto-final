from django.conf import settings
from django.db import models
from productos.models import Producto


class Venta(models.Model):
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=150)
    metodo_pago = models.CharField(max_length=15, choices=METODOS_PAGO, default='EFECTIVO')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta #{self.pk} - {self.cliente}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"


class ReporteGuardado(models.Model):
    """VM-681: reportes guardados con sus filtros"""
    nombre = models.CharField(max_length=120)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    categoria = models.ForeignKey(
        'productos.Categoria', on_delete=models.SET_NULL, null=True, blank=True
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class RegistroAuditoria(models.Model):
    """VM-687: quién consultó o exportó reportes y cuándo"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    accion = models.CharField(max_length=150)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.accion} - {self.fecha:%d/%m/%Y %H:%M}"