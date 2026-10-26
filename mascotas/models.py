import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

class Especie(models.Model):
    ESTADOS = [('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')]
    
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    sync_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.nombre
    

class Raza(models.Model):
    ESTADOS = [('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')]

    especie = models.ForeignKey(Especie, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    sync_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['especie', 'nombre'], name='raza_unica_por_especie'),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.especie})"
    


class Mascota(models.Model):
    SEXOS = [('M', 'Macho'), ('H', 'Hembra')]
    ESTADOS = [('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')]
    
    Cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'rol': 'CLIENTE'}, related_name='mascotas')
    
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT)
    raza = models.ForeignKey(Raza, on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    edad_aproximada_meses = models.PositiveSmallIntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXOS)
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=80, blank=True)
    microchip = models.CharField(max_length=80, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    esterilizado = models.CharField(max_length=20)
    observaciones = models.CharField(max_length=1000, blank=True)
    sync_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def clean(self):
        super().clean()
        if self.raza_id and self.especie_id and self.raza.especie_id != self.especie_id:
            raise ValidationError({'raza': 'La raza no corresponde a la especie elegida'})

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
# Create your models here.


class Servicio(models.Model):
    """Servicios que ofrece la veterinaria (Consulta, Vacunación, Estética, etc.)"""
    ESTADOS = [('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')]

    nombre = models.CharField(max_length=100, verbose_name="Nombre del servicio")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    duracion_minutos = models.PositiveIntegerField(default=30, verbose_name="Duración (minutos)")
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio")
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    sync_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"


class Cita(models.Model):
    """Cita veterinaria: conecta mascota, veterinario, servicio, fecha y hora"""

    class Estado(models.TextChoices):
        PROGRAMADA  = 'PROGRAMADA',  'Programada'
        CONFIRMADA  = 'CONFIRMADA',  'Confirmada'
        EN_CURSO    = 'EN_CURSO',    'En curso'
        COMPLETADA  = 'COMPLETADA',  'Completada'
        CANCELADA   = 'CANCELADA',   'Cancelada'
        NO_ASISTIO  = 'NO_ASISTIO',  'No asistió'

    # Relación con la mascota (app mascotas)
    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name="Mascota"
    )

    # Veterinario asignado (solo usuarios con rol VETERINARIO)
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas_asignadas',
        limit_choices_to={'rol': 'VETERINARIO'},
        verbose_name="Veterinario asignado"
    )

    # Servicio solicitado
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name="Servicio"
    )

    # Fecha y hora de la cita
    fecha_hora = models.DateTimeField(verbose_name="Fecha y hora")

    # Motivo adicional del cliente
    motivo = models.TextField(blank=True, verbose_name="Motivo / observaciones del cliente")

    # Estado de la cita
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
        verbose_name="Estado"
    )

    # Notas del veterinario después de la cita
    notas_veterinario = models.TextField(blank=True, verbose_name="Notas del veterinario")

    # Fechas de auditoría
    creada_en   = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    sync_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    def __str__(self):
        return f"{self.mascota.nombre} - {self.servicio.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"


class Producto(models.Model):
    """Productos de la tienda veterinaria"""
    CATEGORIAS = [
        ('NUTRICION',   'Nutrición'),
        ('HIGIENE',     'Higiene'),
        ('FARMACIA',    'Farmacia'),
        ('ACCESORIOS',  'Accesorios'),
        ('OTROS',       'Otros'),
    ]
    ESTADOS = [('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')]

    nombre      = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    categoria   = models.CharField(max_length=20, choices=CATEGORIAS, default='OTROS')
    precio      = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    imagen      = models.ImageField(upload_to='productos/', null=True, blank=True)
    estado      = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    sync_uuid   = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


class Carrito(models.Model):
    """Carrito de compras por usuario"""
    usuario    = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    creado_en  = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())

    def __str__(self):
        return f"Carrito de {self.usuario.username}"


class ItemCarrito(models.Model):
    """Ítem dentro del carrito"""
    carrito   = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto  = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad  = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
