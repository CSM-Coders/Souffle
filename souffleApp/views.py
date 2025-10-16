from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlencode
from .models import SouffleApp, Favorite, Horario, Compra
from .decorators import admin_required, is_admin_user
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import random

# Create your views here.

def main(request):
    return render(request, 'souffleApp/main.html')

def home(request):
    souffleApp = SouffleApp.objects.all()
    searchTerm = request.GET.get('searchCourse')
    semanticQuery = request.GET.get('semanticQuery')
    best_course = None
    similarity = None
    
    # Búsqueda normal por título
    if searchTerm:
        souffleApp = souffleApp.filter(title__icontains=searchTerm)
    
    # Búsqueda semántica
    elif semanticQuery:
        try:
            load_dotenv(os.path.join(os.path.dirname(__file__), '../gemini.env'))
            api_key = os.environ.get('gemini_apikey')
            if api_key:
                genai.configure(api_key=api_key)
                
                # Usar el modelo de embeddings de Gemini
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=semanticQuery,
                    task_type="retrieval_query"
                )
                prompt_emb = np.array(result['embedding'], dtype=np.float32)
                
                # Lista para almacenar cursos con similitud
                course_similarities = []
                
                for course in souffleApp:
                    if course.embedding:
                        course_emb = np.frombuffer(course.embedding, dtype=np.float32)
                        sim = np.dot(prompt_emb, course_emb) / (np.linalg.norm(prompt_emb) * np.linalg.norm(course_emb))
                        course_similarities.append((course, sim))
                
                # Ordenar por similitud descendente
                course_similarities.sort(key=lambda x: x[1], reverse=True)
                
                if course_similarities:
                    best_similarity = course_similarities[0][1]
                    best_course = course_similarities[0][0]
                    similarity = best_similarity
                    
                    # Lógica inteligente para determinar cuántos resultados mostrar
                    if best_similarity > 0.6:
                        # Similitud muy alta: mostrar solo el mejor resultado
                        souffleApp = [best_course]
                    elif best_similarity > 0.45:
                        # Similitud buena: verificar si hay una diferencia clara con el segundo
                        if len(course_similarities) > 1:
                            second_similarity = course_similarities[1][1]
                            difference = best_similarity - second_similarity
                            
                            if difference > 0.1:  # Diferencia significativa
                                souffleApp = [best_course]  # Solo el mejor
                            else:
                                # Mostrar hasta 2 resultados si son similares
                                souffleApp = [course for course, sim in course_similarities[:2] if sim > 0.4]
                        else:
                            souffleApp = [best_course]
                    elif best_similarity > 0.3:
                        # Similitud moderada: mostrar hasta 3 resultados
                        souffleApp = [course for course, sim in course_similarities[:3] if sim > 0.3]
                    else:
                        # Similitud baja: mostrar solo el mejor
                        souffleApp = [best_course]
                else:
                    souffleApp = []
                        
        except Exception as e:
            # En caso de error, mostrar todos los cursos
            print(f"Error en búsqueda semántica: {e}")
            souffleApp = SouffleApp.objects.all()

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list('curso_id', flat=True)
        )

    return render(
        request,
        'souffleApp/home.html',
        {
            'souffleApp': souffleApp,
            'searchTerm': searchTerm,
            'semanticQuery': semanticQuery,
            'best_course': best_course,
            'similarity': similarity,
            'favorite_ids': favorite_ids,
            'is_admin': is_admin_user(request.user),
        },
    )

def cursos_entry(request):
    return render(request, 'souffleApp/cursos_entry.html')

def login_view(request):
    from django.contrib.auth import authenticate, login
    from django.contrib import messages
    from django.contrib.auth.models import User

    next_url = request.GET.get('next') or request.POST.get('next')

    def resolve_redirect_url(url):
        if url and url_has_allowed_host_and_scheme(url, {request.get_host()}, request.is_secure()):
            return url
        return reverse('home')

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
            return redirect(resolve_redirect_url(next_url))
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'souffleApp/login.html', {'next': next_url})
    if request.GET.get('continuar') == '1':
        return redirect('home')
    return render(request, 'souffleApp/login.html', {'next': next_url})

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
    curso = get_object_or_404(SouffleApp, id=curso_id)
    # Obtener horarios disponibles para este curso
    horarios = Horario.objects.filter(curso=curso, cupos__gt=0).order_by('fecha', 'hora')
    
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list('curso_id', flat=True)
        )
    
    context = {
        'curso': curso,
        'favorite_ids': favorite_ids,
        'horarios': horarios,
        'is_admin': is_admin_user(request.user)
    }
    return render(request, 'souffleApp/curso_detail.html', context)


@require_POST
def toggle_favorite(request, curso_id):
    if not request.user.is_authenticated:
        login_url = reverse('login')
        next_target = request.POST.get('next') or request.get_full_path()
        query = urlencode({'next': next_target})
        return redirect(f"{login_url}?{query}")

    curso = get_object_or_404(SouffleApp, id=curso_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, curso=curso)
    if not created:
        favorite.delete()

    redirect_to = request.POST.get('next')
    if redirect_to and url_has_allowed_host_and_scheme(redirect_to, {request.get_host()}, request.is_secure()):
        return redirect(redirect_to)
    return redirect('home')


@admin_required
def estadisticas(request):
    """
    Vista para mostrar estadísticas REALES de ventas de cursos.
    Solo accesible para administradores.
    """
    # Obtener todos los cursos con sus ventas reales
    cursos = SouffleApp.objects.all()
    
    # Crear datos para el gráfico basados en ventas reales
    cursos_data = []
    for curso in cursos:
        ventas_reales = curso.ventas_totales
        if ventas_reales > 0:  # Solo incluir cursos con ventas
            cursos_data.append({
                'nombre': curso.title,
                'ventas': ventas_reales,
                'ingresos': curso.ingresos_totales,
                'curso_obj': curso
            })
    
    # Ordenar por ventas de mayor a menor
    cursos_data.sort(key=lambda x: x['ventas'], reverse=True)
    
    # Preparar datos para los gráficos
    cursos_nombres = [item['nombre'] for item in cursos_data]
    ventas_numeros = [item['ventas'] for item in cursos_data]
    
    # Generar datos de ventas por mes de los últimos 6 meses (basados en compras reales)
    meses = []
    ventas_por_mes = []
    fecha_actual = datetime.now()
    
    for i in range(5, -1, -1):  # Últimos 6 meses
        fecha_mes = fecha_actual - timedelta(days=30*i)
        mes_nombre = fecha_mes.strftime('%B %Y')
        meses.append(mes_nombre)
        
        # Contar compras reales de ese mes
        ventas_mes = Compra.objects.filter(
            estado='confirmada',
            fecha_compra__year=fecha_mes.year,
            fecha_compra__month=fecha_mes.month
        ).count()
        ventas_por_mes.append(ventas_mes)
    
    # Encontrar el curso más vendido
    curso_mas_vendido = cursos_data[0] if cursos_data else None
    
    # Calcular estadísticas adicionales
    total_ventas = sum(ventas_numeros) if ventas_numeros else 0
    total_ingresos = sum(item['ingresos'] for item in cursos_data)
    promedio_ventas = total_ventas / len(cursos_data) if cursos_data else 0
    
    # Obtener compras recientes para mostrar actividad
    compras_recientes = Compra.objects.filter(estado='confirmada').order_by('-fecha_compra')[:10]
    
    context = {
        'cursos_nombres': json.dumps(cursos_nombres),
        'ventas_numeros': json.dumps(ventas_numeros),
        'meses': json.dumps(meses),
        'ventas_por_mes': json.dumps(ventas_por_mes),
        'curso_mas_vendido': curso_mas_vendido,
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'promedio_ventas': round(promedio_ventas, 1),
        'total_cursos': len(cursos_data),
        'cursos_data': cursos_data,
        'compras_recientes': compras_recientes,
        'hay_datos': total_ventas > 0,
    }
    
    return render(request, 'souffleApp/estadisticas.html', context)


@login_required
@require_POST
def comprar_curso(request, horario_id):
    """
    Vista para procesar la compra de un curso en un horario específico.
    """
    horario = get_object_or_404(Horario, id=horario_id)
    
    # Verificar que el horario tiene cupos disponibles
    if not horario.tiene_cupos:
        messages.error(request, f'Lo sentimos, el horario del {horario.fecha} a las {horario.hora} ya no tiene cupos disponibles.')
        return redirect('curso_detail', curso_id=horario.curso.id)
    
    # Verificar que el usuario no haya comprado ya este horario
    compra_existente = Compra.objects.filter(
        usuario=request.user,
        horario=horario,
        estado='confirmada'
    ).exists()
    
    if compra_existente:
        messages.warning(request, 'Ya has comprado este horario para este curso.')
        return redirect('curso_detail', curso_id=horario.curso.id)
    
    # Procesar la compra usando transacción para evitar condiciones de carrera
    try:
        with transaction.atomic():
            # Volver a verificar cupos en la transacción
            horario.refresh_from_db()
            if not horario.tiene_cupos:
                messages.error(request, 'Este horario se agotó mientras procesábamos tu compra. Por favor selecciona otro horario.')
                return redirect('curso_detail', curso_id=horario.curso.id)
            
            # Crear la compra (los campos se autocompletar gracias al método save del modelo)
            compra = Compra.objects.create(
                usuario=request.user,
                curso=horario.curso,
                horario=horario
            )
            
            # Reducir el cupo
            horario.reducir_cupo()
            
            # Enviar email de confirmación
            try:
                enviar_email_confirmacion(compra)
            except Exception as email_error:
                # No fallar la compra si hay error en el email, solo registrar el problema
                print(f"Error enviando email de confirmación: {email_error}")
            
            messages.success(
                request, 
                f'¡Compra exitosa! Has reservado tu lugar para {horario.curso.title} '
                f'el {horario.fecha} a las {horario.hora}. '
                f'Se ha enviado una confirmación a {request.user.email}.'
            )
            
            return redirect('curso_detail', curso_id=horario.curso.id)
            
    except Exception as e:
        messages.error(request, 'Ocurrió un error al procesar tu compra. Por favor intenta nuevamente.')
        return redirect('curso_detail', curso_id=horario.curso.id)


def enviar_email_confirmacion(compra):
    """
    Envía un email de confirmación de compra al usuario con toda la información del curso.
    """
    try:
        # Preparar el contexto para el template
        context = {
            'usuario': compra.usuario,
            'curso': compra.curso,
            'horario': compra.horario,
            'compra': compra,
            'precio_total': compra.curso.price,
        }
        
        # Renderizar el template HTML
        html_message = render_to_string('souffleApp/emails/confirmacion_compra.html', context)
        
        # Enviar el email
        send_mail(
            subject=f'Confirmación de compra - {compra.curso.title}',
            message='',  # Mensaje de texto plano vacío
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[compra.usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error enviando email de confirmación: {e}")
        return False
