from functools import wraps

from django.contrib import messages
from  django.contrib.auth.decorators import login_required
from  django.shortcuts import redirect


def solo_clientes(vista):
    """"deja entrar solo a clientes con sesion iniciada.
    
    si no tiene sesion, lo manda a iniciar (login_requiered).
    si el administrador o veterinario, lo devuelve al inicio con aviso
    """
    
    @wraps(vista)
    def envoltura(request, *args,  **kwargs):
        if request.user.rol != "CLIENTE":
            messages.warning(request,  "Esta seccion es solo para clientes.")
            return redirect("inicio")
        return vista(request, *args, **kwargs)
    
    return  login_required(envoltura)
    
