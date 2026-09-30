import uuid

from django.db import models
from django.db import router, transaction
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    
    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        VETERINARIO = 'VETERINARIO', 'Veterinario'
        CLIENTE = 'CLIENTE', 'Cliente'
        
        

    TIPO_DOCUMENTO_CHOICES = (
        ('CC', 'Cédula de ciudadanía'),
        ('CE', 'Cédula de extranjería'),
        ('TI', 'Tarjeta de identidad'),
        ('RC', 'Registro civil'),
        ('PA', 'Pasaporte'),
        ('NU', 'Otro')
    )

    first_name = models.CharField(max_length=50, verbose_name="Nombre", blank=True)
    last_name = models.CharField(max_length=50, verbose_name="Apellido", blank=True)
    
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        verbose_name="Rol"
    )
    
    Document_Type = models.CharField(
        max_length=3,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de documento",
        default='CC',
        blank=True,
    )
    Number_Document = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de documento",
        blank=True,
        null=True,
    )
    Date_of_birth = models.DateField(
        verbose_name="Fecha de nacimiento",
        null=True,
        blank=True,
    )
    sync_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    REQUIRED_FIELDS = ["first_name", "last_name", "Document_Type", "Number_Document", "Date_of_birth"]

    def save(self, *args, **kwargs):
        using = kwargs.get('using') or router.db_for_write(type(self), instance=self)
        with transaction.atomic(using=using):
            return super().save(*args, **kwargs)
    
    def es_veterinario(self):
        return self.rol == self.Rol.VETERINARIO
    
    def es_cliente(self):
        return self.rol == self.Rol.CLIENTE
    
    def es_admin(self):
        return self.rol == self.Rol.ADMIN
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class UsuarioSyncPendiente(models.Model):
    class Operacion(models.TextChoices):
        GUARDAR = 'guardar', 'Guardar'
        ELIMINAR = 'eliminar', 'Eliminar'

    sync_uuid = models.UUIDField(unique=True)
    operacion = models.CharField(
        max_length=10,
        choices=Operacion.choices,
        default=Operacion.GUARDAR,
    )
    intentos = models.PositiveIntegerField(default=0)
    reintentar_despues = models.DateTimeField(null=True, blank=True)
    ultimo_error = models.TextField(blank=True)
    revision = models.PositiveBigIntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('creado',)