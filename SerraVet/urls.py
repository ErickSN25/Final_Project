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
from clinica import views
from django.conf import settings
from django.conf.urls.static import static


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
    path('home_atendente/atd/gerenciar_horarios/', views.gerenciar_horarios, name='gerenciar_horarios'),
    path('home_atendente/atd/editar_horario/<int:horario_id>/', views.editar_horario, name='editar_horario'),
    path('home_atendente/atd/excluir_horario/<int:horario_id>/', views.excluir_horario, name='excluir_horario'),
    path('home_atendente/atd/gerenciar_horarios/<int:horario_id>/reservar/', views.reservar_horario, name='reservar_horario'),
    path('home_atendente/atd/gerenciar_horarios/criar/', views.criar_horario, name='criar_horario'),
    path('meus-pets/', views.meus_pets_view, name='meus_pets'),
    path('meus-pets/cadastrar/', views.cadastrar_pet_view, name='cadastrar_pet'),
    path('meus-pets/excluir/<int:pet_id>/', views.excluir_pet_view, name='excluir_pet'),
    path('meus-pets/detalhes/<int:pet_id>/', views.detalhes_pet_view, name='detalhes_pet'),
    path('meus-pets/editar/<int:pet_id>/', views.editar_pet_form_view, name='editar_pet'),
    path('consultas/', views.minhas_consultas_view, name='consultas_user'), 
    path('agendar-consulta/', views.agendar_consulta_view, name='cadastrar_consulta'),
    path('ajax/obter_horarios/', views.obter_horarios_disponiveis_ajax, name='obter_horarios_ajax'),
    path('consultas/<int:pk>/', views.detalhe_consulta_view, name='detalhes_consulta'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)