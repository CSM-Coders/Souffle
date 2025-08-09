from django.urls import path
from . import views

urlpatterns = [
    path('', views.home,         name='home'),         
    path('courses/', views.list, name='courses_list')  
]
