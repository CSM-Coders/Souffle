from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """
    Decorador que verifica si el usuario es administrador.
    Solo permite acceso a usuarios con is_superuser=True.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos de administrador para acceder a esta sección.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def is_admin_user(user):
    """
    Función helper para verificar si un usuario es administrador.
    """
    return user.is_authenticated and user.is_superuser