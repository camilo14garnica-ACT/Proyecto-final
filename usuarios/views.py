from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import CrearUsuarioForm
from .decorators import solo_admin, solo_veterianrio
from django.contrib.auth.decorators import login_required
from .forms import CrearUsuarioForm, EditarPerfilForm
from django.contrib.auth.forms import AuthenticationForm


def inicio(request):
    return render(request, 'usuarios/inicio.html')


# Creamos nuestra vista
#Registro de clientes (publico)
def crear_usuario(request):

    if request.method == 'POST':
        # El usuario envía el formulario
        form = CrearUsuarioForm(request.POST)

        # Validamos
        if form.is_valid():
            # Creamos el usuario sin guardarlo todavía
            usuario = form.save(commit=False)

            # Encriptamos la contraseña
            usuario.set_password(
                form.cleaned_data['password']
            )
            usuario.rol = 'CLIENTE'         # se asigna a la fuerza, sin importar qué mande el formulario

            # Guardamos el usuario
            usuario.save()
            
            from django.contrib.auth import login
            login(request, usuario)         # lo deja logueado automaticamente

            # Redirigimos
            return redirect('inicio')          #Lo redirije al inicio.

    else:
        # Mostramos un formulario vacío
        form = CrearUsuarioForm()

    return render(
        request,
        'usuarios/crear_usuario.html',
        {'form': form}
    )


#Inicio de sesion (todos entran por aqui, luego se redirige el rol)
from django.contrib.auth.forms import AuthenticationForm


def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)

            if usuario.rol == 'ADMIN':
                return redirect('panel_admin')
            elif usuario.rol == 'VETERINARIO':
                return redirect('panel_veterinario')
            else:
                return redirect('inicio')
    else:
        form = AuthenticationForm()

    return render(request, 'usuarios/iniciar_sesion.html', {'form': form})


#CERRAR SESION 

def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')


#PANEL DE ADMINISTRADOR (PROTEGIDO)
@solo_admin
def panel_admin(request):
    return render(request, 'usuarios/panel_admin.html')

#PANEL DEL VETERINARIO 

@solo_veterianrio
def panel_veterinario(request):
    return render(request, 'usuarios/panel_veterinario.html')


#EDITAR PERFIL

@login_required
def mi_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('mi_perfil')
    else:
        form = EditarPerfilForm(instance=request.user)
        
    return render(request, 'usuarios/perfil.html', {'form': form})
        
# Create your views here.
