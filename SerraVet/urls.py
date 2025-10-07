"""
URL configuration for SerraVet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from clinica.views import CustomLoginView, redirect_home, home_user, home_vet, cadastro, home, home_atendente

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("cadastro/", cadastro, name="cadastro"),
    path("login/", CustomLoginView.as_view(), name="login"), 
    path("logout/", LogoutView.as_view(), name="logout"),
    path("home_user/", home_user, name="home_user"),
    path("redirect_home/", redirect_home, name="redirect_home"),
    path("home_vet/", home_vet, name="home_vet"),
    path("home_atendente/", home_atendente, name="home_atendente"),
    
]