from datetime import datetime, timedelta
 
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
 
from .disponibilidad import MINUTOS_POR_BLOQUE  # cada bloque dura 30 minutos
 
# Con cuántas horas de anticipación el cliente puede cancelar o reprogramar
# (decisión del proyecto: 24 horas). Si cambia la regla, se cambia solo aquí.
HORAS_MINIMAS_CANCELAR = 24
 
 
def ahora_local():
    """Fecha y hora actual en la zona horaria del proyecto, sin zona (para comparar con las citas)."""
    ahora = timezone.now()
    if timezone.is_aware(ahora):
        ahora = timezone.localtime(ahora).replace(tzinfo=None)
    return ahora
 
 
class CategoriaServicio(models.Model):
    """Grupo de servicios: consulta, vacunación, peluquería, cirugía..."""
 
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"
 
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)
 
    class Meta:
        verbose_name = "categoría de servicio"
        verbose_name_plural = "categorías de servicios"
        ordering = ["nombre"]
 
    def __str__(self):
        return self.nombre
 
 
class Servicio(models.Model):
    """Lo que ofrece la veterinaria y el cliente puede agendar."""
 
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"
 
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(
        CategoriaServicio, on_delete=models.PROTECT, related_name="servicios"
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    # Cuántos bloques de 30 minutos ocupa (1 = 30 min, 2 = 1 hora, ...)
    bloques = models.PositiveSmallIntegerField(default=1)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)
 
    class Meta:
        ordering = ["categoria__nombre", "nombre"]
 
    def __str__(self):
        return self.nombre
 
    @property
    def duracion_minutos(self):
        return self.bloques * MINUTOS_POR_BLOQUE
 
    def clean(self):
        if self.precio is not None and self.precio < 0:
            raise ValidationError({"precio": "El precio no puede ser negativo."})
        if self.bloques < 1:
            raise ValidationError({"bloques": "El servicio debe ocupar al menos un bloque."})
 
 
class HorarioVeterinario(models.Model):
    """Días y horas en que atiende cada veterinario. Puede haber varios bloques por día."""
 
    class Dia(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miércoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"
 
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="horarios",
        limit_choices_to={"rol": "VETERINARIO"},
    )
    dia_semana = models.PositiveSmallIntegerField(choices=Dia.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
 
    class Meta:
        verbose_name = "horario de veterinario"
        verbose_name_plural = "horarios de veterinarios"
        ordering = ["veterinario", "dia_semana", "hora_inicio"]
 
    def __str__(self):
        return f"{self.veterinario} - {self.get_dia_semana_display()} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}"
 
    def clean(self):
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora de fin debe ser después de la hora de inicio.")
 
        # No permitir bloques que se crucen el mismo día para el mismo veterinario
        if self.veterinario_id and self.hora_inicio and self.hora_fin:
            cruzados = HorarioVeterinario.objects.filter(
                veterinario_id=self.veterinario_id,
                dia_semana=self.dia_semana,
                activo=True,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            ).exclude(pk=self.pk)
            if cruzados.exists():
                raise ValidationError("Este horario se cruza con otro que ya existe ese día.")
 
 
class DiaNoDisponible(models.Model):
    """Vacaciones, festivos o permisos. Sin veterinario = cierra toda la veterinaria."""
 
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dias_no_disponibles",
        limit_choices_to={"rol": "VETERINARIO"},
        null=True,
        blank=True,
        help_text="Déjalo vacío si aplica para toda la veterinaria.",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.CharField(max_length=150, blank=True)
 
    class Meta:
        verbose_name = "día no disponible"
        verbose_name_plural = "días no disponibles"
        ordering = ["-fecha_inicio"]
 
    def __str__(self):
        quien = self.veterinario or "Toda la veterinaria"
        return f"{quien}: {self.fecha_inicio} a {self.fecha_fin}"
 
    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha final no puede ser antes de la inicial.")
 
 
class Cita(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        ATENDIDA = "ATENDIDA", "Atendida"
        CANCELADA = "CANCELADA", "Cancelada"
        NO_ASISTIO = "NO_ASISTIO", "No asistió"
 
    # Qué cambios de estado se permiten (VM-589)
    CAMBIOS_PERMITIDOS = {
        "PENDIENTE": ["CONFIRMADA", "CANCELADA"],
        "CONFIRMADA": ["ATENDIDA", "NO_ASISTIO", "CANCELADA"],
        "ATENDIDA": [],
        "CANCELADA": [],
        "NO_ASISTIO": [],
    }
 
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="citas",
        limit_choices_to={"rol": "CLIENTE"},
    )
    mascota = models.ForeignKey("mascotas.Mascota", on_delete=models.PROTECT, related_name="citas")
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="citas")
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="citas_asignadas",
        limit_choices_to={"rol": "VETERINARIO"},
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
 
    # Quién la agendó: el mismo cliente o alguien del personal
    agendada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="citas_agendadas"
    )
 
    observaciones = models.TextField(blank=True)  # las escribe el veterinario al atender
 
    # Datos de cancelación
    motivo_cancelacion = models.CharField(max_length=200, blank=True)
    cancelada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas_canceladas",
    )
 
    # Si fue reprogramada, guarda la fecha y hora anteriores
    fecha_anterior = models.DateField(null=True, blank=True)
    hora_anterior = models.TimeField(null=True, blank=True)
 
    recordatorio_enviado = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ["fecha", "hora_inicio"]
        indexes = [models.Index(fields=["veterinario", "fecha"])]
 
    def __str__(self):
        return f"{self.mascota} - {self.servicio} - {self.fecha} {self.hora_inicio:%H:%M}"
 
    @property
    def inicio(self):
        return datetime.combine(self.fecha, self.hora_inicio)
 
    def puede_cambiar_a(self, nuevo_estado):
        return nuevo_estado in self.CAMBIOS_PERMITIDOS.get(self.estado, [])
 
    def puede_cancelar_cliente(self, ahora=None):
        """El cliente puede cancelar hasta 24 horas antes (decisión del proyecto)."""
        ahora = ahora or ahora_local()
        if self.estado not in (self.Estado.PENDIENTE, self.Estado.CONFIRMADA):
            return False
        return self.inicio - ahora >= timedelta(hours=HORAS_MINIMAS_CANCELAR)
 
    def clean(self):
        if self.mascota_id and self.cliente_id and self.mascota.Cliente_id != self.cliente_id:
            raise ValidationError({"mascota": "Esa mascota no pertenece a este cliente."})
 
 
class CambioEstadoCita(models.Model):
    """Historial: quién cambió el estado de una cita y cuándo (VM-589)."""
 
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name="cambios_estado")
    estado_anterior = models.CharField(max_length=12, choices=Cita.Estado.choices)
    estado_nuevo = models.CharField(max_length=12, choices=Cita.Estado.choices)
    cambiado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    fecha = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = "cambio de estado de cita"
        verbose_name_plural = "cambios de estado de citas"
        ordering = ["-fecha"]
 
    def __str__(self):
        return f"{self.cita_id}: {self.estado_anterior} -> {self.estado_nuevo}"
 