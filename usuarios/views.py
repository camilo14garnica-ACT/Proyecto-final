from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CrearUsuarioForm, EditarPerfilForm, EditarUsuarioForm
from .decorators import solo_admin, solo_veterianrio
from django.contrib.auth.decorators import login_required
from .forms import CrearUsuarioForm, EditarPerfilForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from usuarios.models import Usuario
from django.views.decorators.http import require_http_methods, require_POST



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


#CERRAR SESION 

def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')


#PANEL DE ADMINISTRADOR (PROTEGIDO)
@solo_admin
def panel_admin(request):
    return render(request, 'usuarios/panel_admin.html')


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
