from django.shortcuts import render
from django.http import HttpResponse
from.models import SouffleApp

# Create your views here.

def home(request):
    searchTerm = request.GET.get('Search')
    if searchTerm:
        souffleApp = SouffleApp.objects.filter(title__icontains=searchTerm)
    else:
        souffleApp = SouffleApp.objects.all()
    return render(request, 'souffleApp/home.html', {'searchTerm': searchTerm, 'souffleApp': souffleApp})

def about(request):
    return render(request, 'souffleApp/about.html')

def curso_detail(request, curso_id):
    from django.shortcuts import get_object_or_404
    curso = get_object_or_404(SouffleApp, id=curso_id)
    return render(request, 'souffleApp/curso_detail.html', {'curso': curso})
