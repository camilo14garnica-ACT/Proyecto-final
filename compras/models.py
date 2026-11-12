import uuid
from django.db import models
from django.conf import settings
from mascotas.models import Producto


class Proveedor(models.Model):
    """Proveedor de productos para la veterinaria"""
    nombre      = models.CharField(max_length=120, verbose_name="Nombre")
    contacto    = models.CharField(max_length=120, blank=True, verbose_name="Contacto")
    telefono    = models.CharField(max_length=20, blank=True)
    email       = models.EmailField(blank=True)
    direccion   = models.CharField(max_length=255, blank=True)
    activo      = models.BooleanField(default=True)
    sync_uuid   = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']


class OrdenCompra(models.Model):
    """VM-271 — Orden de compra a un proveedor"""

    class Estado(models.TextChoices):
        BORRADOR    = 'BORRADOR',   'Borrador'
        ENVIADA     = 'ENVIADA',    'Enviada'
        RECIBIDA    = 'RECIBIDA',   'Recibida parcialmente'
        COMPLETADA  = 'COMPLETADA', 'Completada'
        CANCELADA   = 'CANCELADA',  'Cancelada'

    proveedor       = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='ordenes')
    creada_por      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ordenes_compra')
    fecha_orden     = models.DateField(auto_now_add=True)
    fecha_esperada  = models.DateField(null=True, blank=True, verbose_name="Fecha esperada de entrega")
    estado          = models.CharField(max_length=15, choices=Estado.choices, default=Estado.BORRADOR)
    notas           = models.TextField(blank=True)
    sync_uuid       = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"OC-{self.pk} | {self.proveedor} | {self.get_estado_display()}"

    class Meta:
        verbose_name = "Orden de compra"
        verbose_name_plural = "Órdenes de compra"
        ordering = ['-fecha_orden']


class ItemOrdenCompra(models.Model):
    """Línea de producto dentro de una orden de compra"""
    orden       = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='items')
    producto    = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad    = models.PositiveIntegerField(default=1)
    precio_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")

    def subtotal(self):
        return self.cantidad * self.precio_unit

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"


class Lote(models.Model):
    """VM-273 — Lote de un producto con fecha de vencimiento"""
    producto        = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes_compra')
    orden           = models.ForeignKey(OrdenCompra, on_delete=models.SET_NULL, null=True, blank=True, related_name='lotes')
    numero_lote     = models.CharField(max_length=80, blank=True, verbose_name="Número de lote")
    cantidad        = models.PositiveIntegerField(verbose_name="Cantidad recibida")
    fecha_ingreso   = models.DateField(auto_now_add=True)
    fecha_vence     = models.DateField(null=True, blank=True, verbose_name="Fecha de vencimiento")
    sync_uuid       = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def vencido(self):
        from django.utils import timezone
        if self.fecha_vence:
            return self.fecha_vence < timezone.now().date()
        return False

    def __str__(self):
        return f"Lote {self.numero_lote or self.pk} — {self.producto.nombre}"

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ['fecha_vence']


class RecepcionCompra(models.Model):
    """VM-272 — Recepción e ingreso al inventario de una orden de compra"""
    orden           = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='recepciones')
    recibido_por    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    notas           = models.TextField(blank=True)

    def __str__(self):
        return f"Recepción OC-{self.orden.pk} — {self.fecha_recepcion.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Recepción de compra"
        verbose_name_plural = "Recepciones de compra"
        ordering = ['-fecha_recepcion']


class ItemRecepcion(models.Model):
    """Producto recibido en una recepción"""
    recepcion       = models.ForeignKey(RecepcionCompra, on_delete=models.CASCADE, related_name='items')
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad        = models.PositiveIntegerField()
    numero_lote     = models.CharField(max_length=80, blank=True)
    fecha_vence     = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
