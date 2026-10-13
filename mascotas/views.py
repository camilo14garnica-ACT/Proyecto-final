from django.shortcuts import render, redirect
from .models import Mascota
from django.contrib.auth.decorators import login_required
from .permisos import es_personal

from .forms import  EspecieForm, MascotaForm
from .models import Mascota, Raza
from .permisos import es_personal, solo_admin
from django.contrib import messages
from django.http import JsonResponse

def mascotas_visible(usuario):
    mascotas = Mascota.objects.select_related('Cliente', 'especie', 'raza')
    if es_personal(usuario):
        return mascotas
    return mascotas.filter(Cliente=usuario)


@login_required
def lista_mascotas(request):
    mascotas = mascotas_visible(request.user)
    return render(request, 'mascotas/lista_mascotas.html', {'mascotas': mascotas})

@login_required
def registrar_mascota(request):
    form = MascotaForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        mascota = form.save(commit=False)
        if not es_personal(request.user):
            mascota.Cliente = request.user                          #El cliente siempre es el dueño
        mascota.save()
        messages.success(request, 'Mascota registrada correctamente.')
        return redirect('lista_mascotas')
    return render(request, 'mascotas/mascota_form.html', {'form': form})

@login_required
def razas_por_especie(request, especie_id):
    razas = Raza.objects.filter(especie_id=especie_id, estado='ACTIVO').order_by('nombre')
    return JsonResponse({'razas': [{'id': r.id, 'nombre': r.nombre} for r in razas]})


@solo_admin
def crear_especie(request):
    form = EspecieForm(request.POST or  None)
    if request.method == 'POST' and form.is_valid():
        messages.success(request, 'Especie registrada correctamente.')
        return redirect('crear_especie')
    return render(request, 'mascota/especie_form.html', {'form': form})

# Create your views here.
