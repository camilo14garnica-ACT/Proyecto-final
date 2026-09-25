from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


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


class Mascota(models.Model):
    # Conectamos con el modelo Usuario, filtrando para que solo aparezcan CLIENTES
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mascotas',
        limit_choices_to={'rol': 'CLIENTE'},
        verbose_name="Dueño"
    )
    nombre = models.CharField(max_length=50, verbose_name="Nombre de la mascota")
    especie = models.CharField(max_length=50, verbose_name="Especie (Ej. Perro, Gato)")
    raza = models.CharField(max_length=50, blank=True, verbose_name="Raza")
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")

    def __str__(self):
        return f"{self.nombre} - Dueño: {self.propietario.first_name}"


class Cita(models.Model):
    class EstadoCita(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='citas', verbose_name="Mascota")
    # Conectamos con el modelo Usuario, filtrando para que solo aparezcan VETERINARIOS
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='citas_asignadas',
        limit_choices_to={'rol': 'VETERINARIO'},
        verbose_name="Veterinario asignado"
    )
    fecha_hora = models.DateTimeField(verbose_name="Fecha y Hora de la cita")
    motivo = models.CharField(max_length=255, verbose_name="Motivo de la consulta")
    estado = models.CharField(max_length=15, choices=EstadoCita.choices, default=EstadoCita.PROGRAMADA, verbose_name="Estado")

    def __str__(self):
        return f"Cita: {self.mascota.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"


class HistorialMedico(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='historiales', verbose_name="Mascota")
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'rol': 'VETERINARIO'},
        verbose_name="Atendido por"
    )
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha de registro")
    diagnostico = models.TextField(verbose_name="Diagnóstico")
    tratamiento = models.TextField(verbose_name="Tratamiento recetado")
    notas_adicionales = models.TextField(blank=True, verbose_name="Notas adicionales")

    def __str__(self):
        return f"Historial {self.mascota.nombre} - {self.fecha}"