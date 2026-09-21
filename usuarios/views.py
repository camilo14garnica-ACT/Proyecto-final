from django.shortcuts import render, redirect
from .forms import CrearUsuarioForm


# Creamos nuestra vista
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

            # Guardamos el usuario
            usuario.save()

            # Redirigimos
            return redirect('crear_usuario')

    else:
        # Mostramos un formulario vacío
        form = CrearUsuarioForm()

    return render(
        request,
        'usuarios/crear_usuario.html',
        {'form': form}
    )



# Create your views here.
