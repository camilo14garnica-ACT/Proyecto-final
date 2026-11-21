from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from productos.models import Producto


class Promocion(models.Model):
    ESTADOS = [("ACTIVA", "Activa"), ("INACTIVA", "Inactiva")]

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    descuento = models.DecimalField(
        "Descuento (%)",
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"), message="El descuento debe ser mayor a 0."),
            MaxValueValidator(Decimal("100"), message="El descuento no puede pasar de 100%."),
        ],
    )
    fecha_inicio = models.DateField("Fecha de inicio")
    fecha_fin = models.DateField("Fecha de fin")
    productos = models.ManyToManyField(Producto, related_name="promociones")
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVA")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "promoción"
        verbose_name_plural = "promociones"

    def __str__(self):
        return self.nombre