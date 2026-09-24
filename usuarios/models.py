from django.db import models
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
    REQUIRED_FIELDS = ["first_name", "last_name", "Document_Type", "Number_Document", "Date_of_birth"]
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def es_veterinario(self):
        return self.rol == self.Rol.VETERINARIO
    
    def es_cliente(self):
        return self.rol == self.Rol.CLIENTE
    
    def es_admin(self):
        return self.rol == self.Rol.ADMIN