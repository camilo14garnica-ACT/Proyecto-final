import uuid

from django.db import models
from django.db import router, transaction
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import identify_hasher, is_password_usable
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
    sync_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    creditos_chatbot = models.PositiveIntegerField(
        default=5000,
        verbose_name="Créditos Chatbot IA (Tokens)",
        help_text="Tokens disponibles para interactuar con el asistente de accesibilidad"
    )

    REQUIRED_FIELDS = ["first_name", "last_name", "Document_Type", "Number_Document", "Date_of_birth"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def tiene_creditos(self):
        return self.creditos_chatbot > 0

    def descontar_creditos(self, tokens_consumidos):
        if tokens_consumidos <= 0:
            return self.creditos_chatbot
        self.creditos_chatbot = max(0, self.creditos_chatbot - tokens_consumidos)
        self.save(update_fields=['creditos_chatbot'])
        return self.creditos_chatbot

    def es_veterinario(self):
        return self.rol == self.Rol.VETERINARIO

    def es_cliente(self):
        return self.rol == self.Rol.CLIENTE

    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    def save(self, *args, **kwargs):
        # Sincronizar roles y permisos administrativos
        if self.is_superuser and self.rol != self.Rol.ADMIN:
            self.rol = self.Rol.ADMIN
        if self.rol == self.Rol.ADMIN and not self.is_staff:
            self.is_staff = True

        # Asegurar que la contraseña siempre se guarde cifrada
        if self.password and is_password_usable(self.password):
            try:
                identify_hasher(self.password)
            except ValueError:
                self.set_password(self.password)

        using = kwargs.get('using') or router.db_for_write(type(self), instance=self)
        with transaction.atomic(using=using):
            return super().save(*args, **kwargs)


class Mascota(models.Model):
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mascotas_legacy',
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
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='citas_asignadas_legacy',
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


class UsuarioSyncPendiente(models.Model):
    """Cola de sincronización entre bases de datos"""
    class Operacion(models.TextChoices):
        GUARDAR = 'guardar', 'Guardar'
        ELIMINAR = 'eliminar', 'Eliminar'

    sync_uuid = models.UUIDField(unique=True)
    operacion = models.CharField(max_length=10, choices=Operacion.choices, default=Operacion.GUARDAR)
    intentos = models.PositiveIntegerField(default=0)
    reintentar_despues = models.DateTimeField(null=True, blank=True)
    ultimo_error = models.TextField(blank=True)
    revision = models.PositiveBigIntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('creado',)


class CodigoRecuperacion(models.Model):
    """Código de 6 dígitos para recuperar contraseña por correo"""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='codigos_recuperacion'
    )
    # Código de 6 dígitos generado aleatoriamente
    codigo = models.CharField(max_length=6)
    # Fecha de expiración: 15 minutos desde la creación
    expira_en = models.DateTimeField()
    # Si ya fue usado no puede volver a usarse
    usado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-creado',)

    def __str__(self):
        return f"Código {self.codigo} para {self.usuario.email}"

    def es_valido(self):
        """Retorna True si el código no fue usado y no ha expirado"""
        from django.utils import timezone
        return not self.usado and self.expira_en > timezone.now()
