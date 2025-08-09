from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def list(request):
    return render(request, 'courses.html')
