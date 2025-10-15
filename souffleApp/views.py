from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.db import OperationalError, ProgrammingError
from django.contrib import messages
from .models import SouffleApp, Favorite
import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# Create your views here.

def main(request):
    return render(request, 'souffleApp/main.html')

def _safe_favorite_ids(user):
    if not user.is_authenticated:
        return []
    try:
        return list(
            Favorite.objects.filter(usuario=user).values_list('curso_id', flat=True)
        )
    except (OperationalError, ProgrammingError):
        return []


def home(request):
    souffleApp = SouffleApp.objects.all()
    searchTerm = request.GET.get('searchCourse')
    if searchTerm:
        souffleApp = souffleApp.filter(title__icontains=searchTerm)
    favorite_ids = _safe_favorite_ids(request.user)
    return render(
        request,
        'souffleApp/home.html',
        {
            'souffleApp': souffleApp,
            'searchTerm': searchTerm,
            'favorite_ids': favorite_ids,
        },
    )

def semantic_search(request):
    souffleApp = SouffleApp.objects.all()
    semanticQuery = request.GET.get('semanticQuery')
    best_course = None
    similarity = None

    if semanticQuery:
        load_dotenv(os.path.join(os.path.dirname(__file__), '../openAI.env'))
        api_key = os.environ.get('openai_apikey')
        if not api_key:
            return HttpResponse("OpenAI API key not found.", status=500)
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            input=[semanticQuery],
            model="text-embedding-3-small"
        )
        prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)
        max_similarity = -1
        for course in souffleApp:
            if course.embedding:
                course_emb = np.frombuffer(course.embedding, dtype=np.float32)
                sim = np.dot(prompt_emb, course_emb) / (np.linalg.norm(prompt_emb) * np.linalg.norm(course_emb))
                if sim > max_similarity:
                    max_similarity = sim
                    best_course = course
                    similarity = sim
        souffleApp = [best_course] if best_course else []

    favorite_ids = _safe_favorite_ids(request.user)

    return render(request, 'souffleApp/home.html', {
        'souffleApp': souffleApp,
        'semanticQuery': semanticQuery,
        'best_course': best_course,
        'similarity': similarity,
        'favorite_ids': favorite_ids,
    })

def cursos_entry(request):
    return render(request, 'souffleApp/cursos_entry.html')

def login_view(request):
    from django.contrib.auth import authenticate, login
    from django.contrib.auth.models import User
    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = None
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        if user is not None:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'souffleApp/login.html', {'next': next_url})
    if request.GET.get('continuar') == '1':
        return redirect('home')
    return render(request, 'souffleApp/login.html', {'next': next_url})

def signup_view(request):
    from django.contrib.auth.models import User
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
    curso = get_object_or_404(SouffleApp, id=curso_id)
    is_favorite = False
    if request.user.is_authenticated:
        try:
            is_favorite = Favorite.objects.filter(usuario=request.user, curso=curso).exists()
        except (OperationalError, ProgrammingError):
            is_favorite = False
    return render(request, 'souffleApp/curso_detail.html', {'curso': curso, 'is_favorite': is_favorite})


@login_required
def toggle_favorite(request, curso_id):
    if request.method != 'POST':
        return redirect('home')

    curso = get_object_or_404(SouffleApp, id=curso_id)
    try:
        favorite, created = Favorite.objects.get_or_create(usuario=request.user, curso=curso)
        if not created:
            favorite.delete()
    except (OperationalError, ProgrammingError):
        messages.error(request, 'No se pudo actualizar tus favoritos. Intenta nuevamente más tarde.')
    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect('home')
