import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class RegistroClinico(models.Model):
    ESTADOS = [('ACTIVO', 'Activo'), ('ANULADO', 'Anulado')]

    mascota = models.ForeignKey(
        'mascotas.Mascota',
        on_delete=models.PROTECT,
        related_name='registros_clinicos',
    )
    fecha = models.DateField()
    motivo = models.CharField(max_length=255)
    diagnostico = models.TextField()
    tratamiento = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros_clinicos_creados',
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    sync_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ['-fecha', '-fecha_creacion']
        verbose_name = 'Registro clínico'
        verbose_name_plural = 'Registros clínicos'

    def clean(self):
        super().clean()
        if self.fecha and self.fecha > timezone.localdate():
            raise ValidationError({'fecha': 'La fecha no puede ser futura.'})

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mascota} - {self.fecha} - {self.motivo}"


# Create your models here.
