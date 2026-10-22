from django.contrib.auth import authenticate, login, logout
<<<<<<< HEAD
=======
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CrearUsuarioForm, EditarPerfilForm, EditarUsuarioForm
from .decorators import solo_admin, solo_veterianrio
>>>>>>> 4877cb84795950d378de70a9c5694b3ce7374643
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
<<<<<<< HEAD
from django.shortcuts import render, redirect

from .decorators import solo_admin, solo_veterinario, solo_veterianrio
from .forms import CrearUsuarioForm, EditarPerfilForm
=======
from django.contrib import messages
from usuarios.models import Usuario
from django.views.decorators.http import require_http_methods, require_POST

>>>>>>> 4877cb84795950d378de70a9c5694b3ce7374643


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
    if request.user.is_authenticated:
        if request.user.rol == 'ADMIN':
            return redirect('panel_admin')
        elif request.user.rol == 'VETERINARIO':
            return redirect('panel_veterinario')
        return redirect('inicio')

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

<<<<<<< HEAD
=======

#LISTAR USUARIOS
@solo_admin
def listar_usuarios(request):
    usuarios = Usuario.objects.all().order_by(
        'last_name',
        'first_name'
    )
    
    return render(
        request,
        'usuarios/lista_usuarios.html',
        {'usuarios': usuarios}
    )


#PANEL DEL VETERINARIO 
>>>>>>> 4877cb84795950d378de70a9c5694b3ce7374643

# Panel del Veterinario (Protegido con redirección a inicio)
@solo_veterinario
def panel_veterinario(request):
    return render(request, 'usuarios/panel_veterinario.html')


<<<<<<< HEAD
# Editar Perfil (Requiere inicio de sesión)
=======
#EDITAR PERFIL
>>>>>>> 4877cb84795950d378de70a9c5694b3ce7374643
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
<<<<<<< HEAD
=======

#ELIMINACION DE CUENTA PERSONAL
# ELIMINACIÓN DE USUARIOS DESDE EL PANEL ADMINISTRATIVO

# ELIMINAR USUARIOS DESDE EL PANEL ADMINISTRATIVO
@solo_admin
@require_POST
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('lista_usuarios')

    username = usuario.username
    usuario.delete()

    messages.success(
        request,
        f'El usuario {username} fue eliminado correctamente.'
    )

    return redirect('lista_usuarios')

#EDITAR USUARIOS DESDE EL PANEL ADMINISTRATIVO 
@solo_admin
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = EditarUsuarioForm(
            request.POST,
            instance=usuario
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Usuario actualizado correctamente.'
            )

            return redirect('lista_usuarios')

    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(
        request,
        'usuarios/editar_usuario.html',
        {
            'form': form,
            'usuario': usuario
        }
    )
    
#Eliminacion de cuentas de clientes desde el panel administrativo
@solo_admin
@require_http_methods(["GET", "POST"])
def confirmar_eliminacion_cuenta(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    # Evitar que el administrador elimine su propia cuenta
    if usuario.pk == request.user.pk:
        messages.error(
            request,
            'No puedes eliminar tu propia cuenta desde este módulo.'
        )
        return redirect('lista_usuarios')
    #Eliminar unicamente cuando se confirme mediante POST
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()

        messages.success(
            request,
            f'El usuario {username} fue eliminado correctamente.'
        )

        return redirect('lista_usuarios')
    #Mostrar la pantalla de confirmacion.
    return render(
        request,
        'usuarios/confirmar_eliminacion_cuenta.html',
        {'usuario': usuario}
    )
    
# Create your views here.
>>>>>>> 4877cb84795950d378de70a9c5694b3ce7374643
