from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET, require_http_methods

from . import services
from .forms import AgendarCitaForm
from .models import HORAS_MINIMAS_CANCELAR, CategoriaServicio, Cita, Servicio, ahora_local
from .permisos import solo_clientes



def lista_servicios(request):
    """Página pública con los servicios activos, agrupados por categoría."""
    categorias = (
        CategoriaServicio.objects.filter(estado="ACTIVO")
        .prefetch_related(
            Prefetch(
                "servicios",
                queryset=Servicio.objects.filter(estado="ACTIVO"),
                to_attr="servicios_activos",
            )
        )
    )
    categorias = [c for c in categorias if c.servicios_activos]
    return render(request, "citas/servicios.html", {"categorias": categorias})


@solo_clientes
@require_http_methods(["GET", "POST"])
def agendar_cita(request):
    if request.method == "POST":
        form = AgendarCitaForm(request.POST, cliente=request.user)
        if form.is_valid():
            datos = form.cleaned_data
            try:
                cita = services.agendar_cita(
                    cliente=request.user,
                    mascota=datos["mascota"],
                    servicio=datos["servicio"],
                    fecha=datos["fecha"],
                    hora=datos["hora"],
                    agendada_por=request.user,
                )
            except services.ReglaDeCitaError as error:
                form.add_error(None, str(error))
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(
                    request,
                    f"Tu cita quedó agendada para el {cita.fecha:%d/%m/%Y} a las {cita.hora_inicio:%H:%M}.",
                )
                return redirect("citas:mis_citas")
    else:
        #si viene desde la pagina de servicios, ya trae el servicio elegido
        form = AgendarCitaForm(clientes=request.user, initial={"servicio": request.GET.get("servicio")})
        
    hoy = ahora_local().date()
    contexto = {
        "form": form,
        "tiene_mascotas": form.fields["mascota"].queryset.exists(),
        "fecha_min": hoy,
        # FullCalendar trata el final del rango como "hasta, sin incluir"
        "fecha_max": hoy + timedelta(days=services.DIAS_MAXIMOS_AGENDA + 1),
    }
    
    return render(request, "citas/agendar,html", contexto)

@solo_clientes
def mis_citas(request):
    ahora = ahora_local()
    citas = Cita.objects.filter(cliente=request.user).select_related(
        "mascota", "servicio", "veterinario"
    )
    proximas, anteriores = [], []
    for cita in citas:
        activa = cita.estado in (Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA)
        if activa and cita.inicio >= ahora:
            cita.cancelable = cita.puede_cancelar_cliente(ahora)
            proximas.append(cita)
        else:
            anteriores.append(cita)
    proximas.sort(key=lambda c: c.inicio)
    anteriores.sort(key=lambda c: c.inicio, reverse=True)

    return render(request, "citas/mis_citas.html", {
        "proximas": proximas,
        "anteriores": anteriores,
        "horas_cancelar": HORAS_MINIMAS_CANCELAR,
    })
    
@solo_clientes
@require_http_methods(["GET", "POST"])
def cancelar_cita(request, pk):
    # Solo encuentra citas del propio cliente: si cambia el número en la dirección, da 404
    cita = get_object_or_404(
        Cita.objects.select_related("mascota", "servicio", "veterinario"),
        pk=pk,
        cliente=request.user,
    )

    if request.method == "POST":
        motivo = request.POST.get("motivo", "").strip()[:200]
        try:
            services.cancelar_cita(cita, request.user, motivo)
        except services.ReglaDeCitaError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "Tu cita fue cancelada.")
        return redirect("citas:mis_citas")
    
    return render(request, "citas/cancelar_cita.html", {
        "cita": cita,
        "puede_cancelar": cita.puede_cancelar_cliente(),
        "horas_cancelar": HORAS_MINIMAS_CANCELAR,
    })
def _servicio_activo(request):
    """Lee ?servicio=<id> de la dirección. Devuelve None si no es válido."""
    try:
        pk = int(request.GET.get("servicio", ""))
    except ValueError:
        return None
    return Servicio.objects.filter(pk=pk, estado="ACTIVO", categoria__estado="ACTIVO").first()


def _fecha(texto):
    """'2026-11-20' o '2026-11-20T00:00:00-05:00' -> date (o None si no es válida)."""
    try:
        return parse_date((texto or "")[:10])
    except ValueError:
        return None
    
    
@solo_clientes
@require_GET
def api_horarios(request):
    """Horas libres de un día para el servicio elegido."""
    servicio = _servicio_activo(request)
    fecha = _fecha(request.GET.get("fecha"))
    if servicio is None or fecha is None:
        return JsonResponse({"error": "Datos no válidos."}, status=400)
    horas = [f"{hora:%H:%M}" for hora in services.horarios_libres(servicio, fecha)]
    return JsonResponse({"horas": horas})

    
    @solo_clientes
    @require_GET
    def api_dias(request):
        """dias  con horarios libres, en el formato que entiende fullcalendar."""
        servicio = _servicio_activo(request)
        desde = _fecha(request.GET.get("start"))
        hasta = _fecha(require_GET.get("end"))
        if Servicio is none:
            return JsonResponse([], safe=False) # todavia no eligio servicio
        if desde is none or hasta is none:
            return JsonResponse({"error": "datos no validos."}, status=400)
        dias = services.dias_con_disponibilidad(servicio, desde, hasta)
        eventos =[
           {"start": f"{dia:%Y-%m-%d}", "display": "background", "color": "#198754"}
        for dia in dias
    ]
    return JsonResponse(eventos, safe=False)
