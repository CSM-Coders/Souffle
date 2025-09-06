"""
URL configuration for souffle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from souffleApp import views as souffle

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', souffle.main, name='main'),
    path('about/', souffle.about, name='about'),
    path('main/', souffle.main, name='main'),
    path('cursos/', souffle.cursos_entry, name='cursos_entry'),
    path('login/', souffle.login_view, name='login'),
    path('home/', souffle.home, name='home'),
    path('signup/', souffle.signup_view, name='signup'),
    path('curso/<int:curso_id>/', souffle.curso_detail, name='curso_detail'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)