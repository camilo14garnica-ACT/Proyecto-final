from datetime import date, datetime, timedelta 

from django.contrib import messages 
from django.contrib.admin.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import protectedErro, Q
from django.http import JsonRespnsabe 
from django.shortcuts import get_object_or_404, redirect 
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from mascotas.models import Mascota 
from mascotas.permisos import es_personal # ajusta la ruta si tu permisos.py esta en otra app 

from .forms import (
    CategoriaServicioForm,
    CitaForm,
    DiaNoDisponibleForm,
    HorarioVeterinarioForm,
    ServicioForm,
)
from .models import (
    HORAS_MINIMAS_CANCELAR,
    MINUTOS_POR_BLOQUE, 
    CategoriaServicio, 
    Cita,
    DiaNoDisponible,
    HorarioVeterinario,
    Servicio,
)

# Disponiblidad de horarios

ESTADOS_QUE_OCUPAN = (Cita.Estado.PENDIENTE,Cita.Estado.CONFIRMADA)


def calcular_hora_fin(fecha, hora_inicio, servicio):
    """Hora de fin = hora de inicio + duración del servicio (bloques x 30 min)"""
    inicio = datetime.combine(fecha, hora_inicio)
    return (inicio + timedelta(minutes=servicio.duracion_minutos)).time()
    
     







