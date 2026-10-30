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