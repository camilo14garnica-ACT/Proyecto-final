from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .decorators import solo_admin, solo_veterinario, solo_veterianrio
from .forms import CrearUsuarioForm, EditarPerfilForm


# Vista de página de inicio pública
def inicio(request):
    return render(request, 'usuarios/inicio.html')


# Registro de clientes (público)
def crear_usuario(request):
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.rol = 'CLIENTE'  # Se asigna el rol CLIENTE por defecto
            usuario.save()

            login(request, usuario)  # Inicia sesión automáticamente
            return redirect('inicio')
    else:
        form = CrearUsuarioForm()

    return render(
        request,
        'usuarios/crear_usuario.html',
        {'form': form}
    )


# Inicio de sesión (redirige según el rol del usuario)
def iniciar_sesion(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            if usuario.rol == 'ADMIN':
                return redirect('panel_admin')
            elif usuario.rol == 'VETERINARIO':
                return redirect('panel_veterinario')
            else:
                return redirect('inicio')
        else:
            error = 'Usuario o contraseña incorrecta'

    return render(request, 'usuarios/iniciar_sesion.html', {'error': error})


# Cerrar sesión
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')


# Alias por compatibilidad
cerrar_secion = cerrar_sesion


# Panel de Administrador (Protegido con redirección a inicio)
@solo_admin
def panel_admin(request):
    return render(request, 'usuarios/panel_admin.html')


# Panel del Veterinario (Protegido con redirección a inicio)
@solo_veterinario
def panel_veterinario(request):
    return render(request, 'usuarios/panel_veterinario.html')


# Editar Perfil (Requiere inicio de sesión)
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
