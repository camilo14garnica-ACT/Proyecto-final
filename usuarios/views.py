from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
import random

from .decorators import solo_admin, solo_veterinario, solo_veterianrio
from .forms import CrearUsuarioForm, EditarPerfilForm, EditarUsuarioForm
from .models import Usuario, CodigoRecuperacion


# Página de inicio pública
def inicio(request):
    return render(request, 'usuarios/inicio.html')


# Registro de clientes
def crear_usuario(request):
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.rol = 'CLIENTE'
            usuario.save()
            login(request, usuario)
            return redirect('inicio')
    else:
        form = CrearUsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})


# Inicio de sesión
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

cerrar_secion = cerrar_sesion


# Panel de Administrador
@solo_admin
def panel_admin(request):
    return render(request, 'usuarios/panel_admin.html')


# Listar usuarios (solo admin)
@solo_admin
def listar_usuarios(request):
    usuarios = Usuario.objects.all().order_by('last_name', 'first_name')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


# Panel del Veterinario
@solo_veterinario
def panel_veterinario(request):
    return render(request, 'usuarios/panel_veterinario.html')


# Editar perfil propio
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


# Eliminar usuario (solo admin)
@solo_admin
@require_POST
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('lista_usuarios')
    username = usuario.username
    usuario.delete()
    messages.success(request, f'El usuario {username} fue eliminado correctamente.')
    return redirect('lista_usuarios')


# Editar usuario desde panel admin
@solo_admin
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('lista_usuarios')
    else:
        form = EditarUsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


# Confirmar eliminación de cuenta propia
@solo_admin
@require_http_methods(["GET", "POST"])
def confirmar_eliminacion_cuenta(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes eliminar tu propia cuenta desde este módulo.')
        return redirect('lista_usuarios')
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'El usuario {username} fue eliminado correctamente.')
        return redirect('lista_usuarios')
    return render(request, 'usuarios/confirmar_eliminacion_cuenta.html', {'usuario': usuario})


# ============================================================
# RECUPERAR CONTRASEÑA CON CÓDIGO DE 6 DÍGITOS
# ============================================================

def recuperar_password_solicitar(request):
    """Paso 1: El usuario ingresa su correo y se genera un código de 6 dígitos"""
    error = None

    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()

        try:
            usuario = Usuario.objects.get(email__iexact=correo)

            # Generamos código de 6 dígitos aleatorio
            codigo = str(random.randint(100000, 999999))

            # Guardamos el código con 15 minutos de expiración
            CodigoRecuperacion.objects.create(
                usuario=usuario,
                codigo=codigo,
                expira_en=timezone.now() + timedelta(minutes=15)
            )

            # Renderizamos la plantilla HTML del correo
            cuerpo_html = render_to_string(
                'usuarios/recuperar_password_email.html',
                {
                    'nombre': usuario.first_name or usuario.username,
                    'codigo': codigo,
                }
            )

            # Enviamos el correo al correo del usuario
            try:
                send_mail(
                    subject='🔑 Tu código de recuperación - Veterinaria Mascott',
                    message=f'Tu código de recuperación es: {codigo}. Expira en 15 minutos.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.email],  # Se envía al correo del usuario
                    html_message=cuerpo_html,
                    fail_silently=False,
                )
                print(f"\n✅ Correo enviado a: {usuario.email} | Código: {codigo}\n")
            except Exception as e:
                # Si falla el envío, mostramos el código en consola como respaldo
                print(f"\n⚠️ Error al enviar correo: {e}")
                print(f"CÓDIGO para {usuario.email}: {codigo}\n")

        except Usuario.DoesNotExist:
            # Por seguridad no revelamos si el correo existe o no
            pass

        # Siempre redirigimos al paso 2 (no revelamos si el correo existe)
        request.session['recuperar_correo'] = correo
        return redirect('recuperar_password_codigo')

    return render(request, 'usuarios/recuperar_password.html', {'error': error})


def recuperar_password_codigo(request):
    """Paso 2: El usuario ingresa el código de 6 dígitos que recibió"""
    correo = request.session.get('recuperar_correo')

    # Si no hay correo en sesión, regresar al paso 1
    if not correo:
        return redirect('recuperar_password_solicitar')

    error = None

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip()

        try:
            usuario = Usuario.objects.get(email__iexact=correo)

            # Buscamos el código más reciente válido para ese usuario
            codigo_obj = CodigoRecuperacion.objects.filter(
                usuario=usuario,
                codigo=codigo_ingresado,
                usado=False
            ).order_by('-creado').first()

            if codigo_obj and codigo_obj.es_valido():
                # Marcamos el código como usado
                codigo_obj.usado = True
                codigo_obj.save()

                # Guardamos en sesión que el código fue verificado
                request.session['recuperar_verificado'] = True
                request.session['recuperar_usuario_id'] = usuario.pk

                return redirect('recuperar_password_nueva')
            else:
                error = 'El código es incorrecto o ya expiró. Intenta de nuevo.'

        except Usuario.DoesNotExist:
            error = 'El código es incorrecto o ya expiró.'

    return render(request, 'usuarios/recuperar_password_enviado.html', {
        'correo': correo,
        'error': error,
    })


def recuperar_password_nueva(request):
    """Paso 3: El usuario crea su nueva contraseña"""
    # Verificamos que pasó por la validación del código
    if not request.session.get('recuperar_verificado'):
        return redirect('recuperar_password_solicitar')

    usuario_id = request.session.get('recuperar_usuario_id')
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    error = None

    if request.method == 'POST':
        nueva = request.POST.get('nueva_password', '')
        confirmar = request.POST.get('confirmar_password', '')

        if not nueva or len(nueva) < 8:
            error = 'La contraseña debe tener al menos 8 caracteres.'
        elif nueva != confirmar:
            error = 'Las contraseñas no coinciden.'
        else:
            # Guardamos la nueva contraseña
            usuario.set_password(nueva)
            usuario.save()

            # Limpiamos la sesión de recuperación
            del request.session['recuperar_verificado']
            del request.session['recuperar_usuario_id']
            del request.session['recuperar_correo']

            return redirect('recuperar_password_completo')

    return render(request, 'usuarios/recuperar_password_confirmar.html', {'error': error})


def recuperar_password_completo(request):
    """Paso 4: Confirmación de que la contraseña fue cambiada"""
    return render(request, 'usuarios/recuperar_password_completo.html')
