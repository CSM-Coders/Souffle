from django.shortcuts import render, redirect
from django.http import HttpResponse
from.models import SouffleApp
import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# Create your views here.

def main(request):
    return render(request, 'souffleApp/main.html')

def home(request):
    souffleApp = SouffleApp.objects.all()
    searchTerm = request.GET.get('searchCourse')
    if searchTerm:
        souffleApp = souffleApp.filter(title__icontains=searchTerm)
    return render(request, 'souffleApp/home.html', {'souffleApp': souffleApp, 'searchTerm': searchTerm})

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

    return render(request, 'souffleApp/home.html', {
        'souffleApp': souffleApp,
        'semanticQuery': semanticQuery,
        'best_course': best_course,
        'similarity': similarity
    })

def cursos_entry(request):
    return render(request, 'souffleApp/cursos_entry.html')

def login_view(request):
    from django.contrib.auth import authenticate, login
    from django.contrib import messages
    from django.contrib.auth.models import User
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
            return redirect('home')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'souffleApp/login.html')
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
