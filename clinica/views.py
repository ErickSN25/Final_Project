from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy # Adicionei reverse_lazy
from django.db import transaction
from .models import CustomUser, ClientePerfil, Pet, Consulta, Prontuario, HorarioDisponivel, Notificacao
from .forms import CadastroPetForm, ProntuarioForm, HorarioDisponivelForm, ConsultaForm, HorarioFiltroForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from datetime import date
from django.core.paginator import Paginator


# --- VIEWS PÚBLICAS / BÁSICAS ---

def home(request):
    return render(request, 'clinica/home.html')

def cadastro(request):
    from .forms import CadastroClienteForm 

    if request.method == 'POST':
        form = CadastroClienteForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save(commit=False)
                usuario.set_password(form.cleaned_data["password"])
                usuario.save()
                
                messages.success(request, "Cadastro realizado com sucesso! Por favor, faça login.")
                return redirect('login')

            except Exception as e:
                print(f"ERRO AO SALVAR CADASTRO: {e}")
                messages.error(request, "Ocorreu um erro inesperado ao finalizar seu cadastro. Tente novamente.")
        
    else:
        form = CadastroClienteForm()
        
    context = {'form': form}
    return render(request, 'clinica/cadastro.html', context)


# --- VIEW DE LOGIN CUSTOMIZADA ---

class CustomLoginView(LoginView):
    template_name = "clinica/home.html" 
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        user = self.request.user
        print(f"DEBUG: Usuário logado: {user.email}, Tipo detectado: '{user.user_type}'") 
        if user.user_type == "cliente":
            return reverse_lazy("home_user")
            
        elif user.user_type == "veterinario":
            return reverse_lazy("home_vet")
            
        elif user.user_type == "atendente":
            return reverse_lazy("home_atendente")
            
        elif user.user_type == "administrador":
            return reverse_lazy("admin:index")
            
        return reverse_lazy("home") 

# --- VIEWS DE REDIRECIONAMENTO  ---

@login_required
def redirect_home(request):
    user = request.user
    if user.user_type == "cliente":
        return redirect("clinica/user/home_user")
    elif user.user_type == "veterinario":
        return redirect("clinica/vet/home_vet", veterinario_id=user.id)
    elif user.user_type == "atendente":
        return redirect("clinica/atd/home_atendente")
    elif user.user_type == "administrador":
        return redirect("/admin/") 
    return redirect("home") 



# --- VIEWS DE CLIENTE ---
@login_required
def home_user(request):
    pets = Pet.objects.filter(tutor=request.user)
    consultas = Consulta.objects.filter(pet__tutor=request.user).order_by('-horario_agendado')[:5]
    context = {
        'user': request.user,
        'pets': pets,
        'consultas': consultas,
    }
    return render(request, 'clinica/user/home_user.html', context)

@login_required
def cadastro_pet(request):
    if request.method == 'POST':
        form = CadastroPetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.tutor = request.user
            pet.save()
            return redirect('perfil_cliente', cliente_id=request.user.clienteperfil.id)
    else:
        form = CadastroPetForm()
    return render(request, 'clinica/cadastro_pet.html', {'form': form})



# --- VIEWS DE VETERINÁRIO ---
@login_required
def home_vet(request):
    hoje = timezone.now() 
    daqui_7_dias = hoje + timedelta(days=7)
    veterinario = request.user

    consultas_qtd = Consulta.objects.filter(veterinario=veterinario, horario_agendado__data__gte=hoje).count()

    prontuarios_qtd = Prontuario.objects.filter(consulta__veterinario=veterinario).count()

    proximas_consultas = Consulta.objects.filter(veterinario=veterinario, horario_agendado__data__gte=hoje, horario_agendado__data__lte=daqui_7_dias).order_by("horario_agendado__data")

    historico_consultas = Consulta.objects.filter(veterinario=veterinario).order_by("-horario_agendado__data")[:5]

    return render(request, "clinica/vet/home_vet.html", {
        "consultas_qtd": consultas_qtd,
        "prontuarios_qtd": prontuarios_qtd,
        "proximas_consultas": proximas_consultas,
        "historico_consultas": historico_consultas,
        "active_page": "home",
    })


def prontuario_veterinario(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id, veterinario=request.user)
    try:
        prontuario = Prontuario.objects.get(consulta=consulta)
    except Prontuario.DoesNotExist:
        prontuario = None
    if request.method == 'POST':
        form = ProntuarioForm(request.POST, request.FILES, instance=prontuario) 
        if form.is_valid():
            prontuario = form.save(commit=False)
            prontuario.consulta = consulta
            prontuario.save()
            return redirect('detalhes_consulta', consulta_id=consulta.id)
    else:
        form = ProntuarioForm(instance=prontuario)
    return render(request, 'clinica/prontuario_veterinario.html', {'form': form, 'consulta': consulta, 'prontuario': prontuario})


# --- VIEWS DE ATENDENTE ---
@login_required
def home_atendente(request):
    hoje = date.today()
    consultas_do_dia_count = Consulta.objects.filter(
        horario_agendado__data=hoje,
        status__in=['PENDENTE', 'CONFIRMADO'] 
    ).count()
    consultas_pendentes_count = Consulta.objects.filter(
        status__in=['PENDENTE', 'CONFIRMADO'],
        horario_agendado__data__gte=hoje 
    ).count()

    consultas_cadastradas = Consulta.objects.filter(horario_agendado__data__gte=timezone.now())


    contexto = {
        'consultas_do_dia_count': consultas_do_dia_count,
        'consultas_pendentes_count': consultas_pendentes_count,
        'consultas_cadastradas': consultas_cadastradas,
    }

    return render(request, 'clinica/atd/home_atendente.html', contexto)

def gerenciar_horarios(request):
    # 1. Buscar todos os horários
    horarios = HorarioDisponivel.objects.all().order_by('data')

    # 2. Adiciona a consulta relacionada a cada horário (ou None)
    for horario in horarios:
        horario.consulta = Consulta.objects.filter(horario_agendado=horario).first()

    # 3. Formulário de filtros
    filtro_form = HorarioFiltroForm(request.GET or None)

    if filtro_form.is_valid():
        veterinario = filtro_form.cleaned_data.get('veterinario')
        if veterinario:
            horarios = horarios.filter(veterinario=veterinario)

        data = filtro_form.cleaned_data.get('data')
        if data:
            horarios = horarios.filter(data__date=data)

        apenas_disponiveis = filtro_form.cleaned_data.get('apenas_disponiveis')
        if apenas_disponiveis:
            horarios = horarios.filter(disponivel=True)

    # ----------------------
    # Paginação (3 horários por página)
    paginator = Paginator(horarios, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # ----------------------

    contexto = {
        'horarios': page_obj,       # queryset paginado
        'page_obj': page_obj,       # para controles de paginação
        'filtro_form': filtro_form,
    }

    return render(request, 'clinica/atd/gerenciar_horarios.html', contexto)

def criar_horario(request):
    if request.method == 'POST':
        form = HorarioDisponivelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Horário criado com sucesso!")
            return redirect('gerenciar_horarios')
    else:
        form = HorarioDisponivelForm()

    return render(request, 'clinica/atd/criar_horario.html', {'form': form})

def reservar_horario(request, horario_id):
    """
    View para reservar um horário já existente, vinculando cliente e pet.
    """
    horario = get_object_or_404(HorarioDisponivel, id=horario_id)

    # Buscar todos os clientes e pets existentes
    clientes = ClientePerfil.objects.all()
    pets = Pet.objects.all()

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        pet_id = request.POST.get('pet_id')
        observacoes = request.POST.get('observacoes', '')

        cliente = get_object_or_404(ClientePerfil, id=cliente_id)
        pet = get_object_or_404(Pet, id=pet_id)

        # Criar a consulta
        Consulta.objects.create(
            pet=pet,
            veterinario=horario.veterinario,
            horario_agendado=horario,
            motivo=observacoes,
            status='Agendada'
        )

        # Atualizar status do horário
        horario.disponivel = False
        horario.save()

        messages.success(request, f"Horário reservado para {cliente.user.get_full_name()} e o pet {pet.nome}!")
        return redirect('gerenciar_horarios')

    contexto = {
        'horario': horario,
        'clientes': clientes,
        'pets': pets,
    }
    return render(request, 'clinica/atd/reservar_horario.html', contexto)

def editar_horario(request, horario_id):
    """Edita um horário existente."""
    horario = get_object_or_404(HorarioDisponivel, id=horario_id)
    if request.method == 'POST':
        form = HorarioDisponivelForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return redirect('gerenciar_horarios')
    else:
        form = HorarioDisponivelForm(instance=horario)

    return render(request, 'clinica/atd/editar_horario.html', {'form': form, 'horario': horario})


def excluir_horario(request, horario_id):
    """Confirma e exclui um horário."""
    horario = get_object_or_404(HorarioDisponivel, id=horario_id)
    if request.method == 'POST':
        horario.delete()
        return redirect('gerenciar_horarios')
    return render(request, 'clinica/atd/excluir_horario.html', {'horario': horario})
# --- VIEWS DE NOTIFICAÇÃO ---

@login_required
def notificacoes(request):
    notificacoes = Notificacao.objects.filter(tutor=request.user).order_by('-criada_em')
    return render(request, 'clinica/notificacoes.html', {'notificacoes': notificacoes})

@login_required
def marcar_notificacao_como_lida(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, tutor=request.user)
    notificacao.lida = True
    notificacao.save()
    return redirect('notificacoes')