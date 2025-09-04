from django.shortcuts import render, redirect
from django.http import HttpResponse
from.models import SouffleApp

# Create your views here.

def main(request):
    return render(request, 'souffleApp/main.html')

def home(request):
    souffleApp = SouffleApp.objects.all()
    return render(request, 'souffleApp/home.html', {'souffleApp': souffleApp})

def cursos_entry(request):
    return render(request, 'souffleApp/cursos_entry.html')

def login_view(request):
    from django.contrib.auth import authenticate, login
    from django.contrib import messages
    from django.shortcuts import redirect
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        from django.contrib.auth.models import User
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'souffleApp/login.html')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            from django.shortcuts import redirect
            return redirect('home')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
    # Si el usuario hace GET a /login?continuar=1, mostrar cursos sin login
    if request.GET.get('continuar') == '1':
        return redirect('home')
    return render(request, 'souffleApp/login.html')

def signup_view(request):
    from django.contrib.auth.models import User
    from django.contrib import messages
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')
            return redirect('login')
    return render(request, 'souffleApp/signup.html')

def about(request):
    return render(request, 'souffleApp/about.html')

def curso_detail(request, curso_id):
    from django.shortcuts import get_object_or_404
    curso = get_object_or_404(SouffleApp, id=curso_id)
    return render(request, 'souffleApp/curso_detail.html', {'curso': curso})
