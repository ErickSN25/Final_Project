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
from clinica import views
from clinica.views import home, listar_veterinarios, veterinario_detalhes, cadastrar_veterinario

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('veterinarios/', views.listar_veterinarios, name='listar_veterinarios'),
    path('veterinarios/<int:id>/', views.veterinario_detalhes, name='veterinario_detalhes'),
    path('veterinarios/cadastrar/', views.cadastrar_veterinario, name='cadastrar_veterinario'),
    path('veterinarios/editar/<int:id>/', views.editar_veterinario, name='veterinario_editar'),
    path('veterinarios/deletar/<int:id>/', views.deletar_veterinario, name='veterinario_deletar'),
]
