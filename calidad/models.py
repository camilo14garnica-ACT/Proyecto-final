from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class EncuestaSatisfaccion(models.Model):
    """Encuesta de satisfacción del cliente tras un servicio."""

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'CLIENTE'},
        related_name='encuestas_satisfaccion',
        verbose_name='Cliente',
    )
    cita = models.ForeignKey(
        'citas.Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='encuestas',
        verbose_name='Cita / Servicio evaluado',
    )
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Puntuación (1-5)',
        help_text='1 = Muy malo, 5 = Excelente',
    )
    comentarios = models.TextField(
        blank=True,
        verbose_name='Comentarios',
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        verbose_name = 'Encuesta de satisfacción'
        verbose_name_plural = 'Encuestas de satisfacción'
        ordering = ['-fecha']

    def __str__(self):
        return f'Encuesta #{self.pk} — {self.cliente} — {self.puntuacion}★'


class PQRS(models.Model):
    """Peticiones, Quejas, Reclamos y Sugerencias."""

    class Tipo(models.TextChoices):
        PETICION    = 'PETICION',    'Petición'
        QUEJA       = 'QUEJA',       'Queja'
        RECLAMO     = 'RECLAMO',     'Reclamo'
        SUGERENCIA  = 'SUGERENCIA',  'Sugerencia'

    class Estado(models.TextChoices):
        ABIERTA     = 'ABIERTA',     'Abierta'
        EN_PROCESO  = 'EN_PROCESO',  'En proceso'
        CERRADA     = 'CERRADA',     'Cerrada'

    tipo = models.CharField(
        max_length=12,
        choices=Tipo.choices,
        verbose_name='Tipo de solicitud',
    )
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.ABIERTA,
        verbose_name='Estado',
    )
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'CLIENTE'},
        related_name='pqrs',
        verbose_name='Cliente',
    )
    descripcion = models.TextField(
        verbose_name='Descripción',
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de radicación',
    )

    class Meta:
        verbose_name = 'PQRS'
        verbose_name_plural = 'PQRS'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} #{self.pk} — {self.cliente}'


class LoteProducto(models.Model):
    """Control de lotes y vencimiento de productos."""

    class EstadoCalidad(models.TextChoices):
        APROBADO    = 'APROBADO',    'Aprobado'
        RECHAZADO   = 'RECHAZADO',   'Rechazado'
        EN_REVISION = 'EN_REVISION', 'En revisión'

    producto = models.ForeignKey(
        'mascotas.Producto',
        on_delete=models.CASCADE,
        related_name='lotes',
        verbose_name='Producto',
    )
    numero_lote = models.CharField(
        max_length=80,
        unique=True,
        verbose_name='Número de lote',
    )
    fecha_vencimiento = models.DateField(
        verbose_name='Fecha de vencimiento',
    )
    estado_calidad = models.CharField(
        max_length=12,
        choices=EstadoCalidad.choices,
        default=EstadoCalidad.EN_REVISION,
        verbose_name='Estado de calidad',
    )

    class Meta:
        verbose_name = 'Lote de producto'
        verbose_name_plural = 'Lotes de productos'
        ordering = ['fecha_vencimiento']

    def __str__(self):
        return f'Lote {self.numero_lote} — {self.producto}'


class NoConformidad(models.Model):
    """Registro de no conformidades vinculadas a PQRS o encuestas."""

    class Estado(models.TextChoices):
        ABIERTA     = 'ABIERTA',     'Abierta'
        EN_PROCESO  = 'EN_PROCESO',  'En proceso'
        RESUELTA    = 'RESUELTA',    'Resuelta'

    pqrs = models.ForeignKey(
        PQRS,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='no_conformidades',
        verbose_name='PQRS origen',
    )
    encuesta = models.ForeignKey(
        EncuestaSatisfaccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='no_conformidades',
        verbose_name='Encuesta origen',
    )
    descripcion_problema = models.TextField(
        verbose_name='Descripción del problema',
    )
    accion_correctiva = models.TextField(
        blank=True,
        verbose_name='Acción correctiva',
    )
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.ABIERTA,
        verbose_name='Estado',
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        verbose_name = 'No conformidad'
        verbose_name_plural = 'No conformidades'
        ordering = ['-fecha']

    def __str__(self):
        origen = ''
        if self.pqrs:
            origen = f'PQRS #{self.pqrs.pk}'
        elif self.encuesta:
            origen = f'Encuesta #{self.encuesta.pk}'
        else:
            origen = 'Sin origen'
        return f'NC #{self.pk} — {origen}'
