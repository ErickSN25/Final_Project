from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy # Adicionei reverse_lazy
from django.db import transaction
from .models import CustomUser, ClientePerfil, Pet, Consulta, Prontuario, HorarioDisponivel, Notificacao
from .forms import CadastroPetForm, ProntuarioForm, HorarioDisponivelForm, ConsultaForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from datetime import date


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
                # 🔒 Criptografa a senha antes de salvar
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
        return redirect("clinica/atendente/home_atendente")
    elif user.user_type == "administrador":
        return redirect("/admin/") 
    return redirect("home") 



# --- VIEWS DE CLIENTE ---
@login_required
def home_user(request):
    pets = Pet.objects.filter(tutor=request.user)
    consultas = Consulta.objects.filter(pet__tutor=request.user).order_by('-data_hora')[:5]
    # Adiciona as informações do usuário ao contexto
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
    veterinario = request.user 
    daqui_7_dias = hoje + timedelta(days=7)

    # Quantidade de consultas futuras do veterinário
    consultas_qtd = Consulta.objects.filter(
        veterinario=veterinario,
        data_hora__gte=hoje
    ).count()

    # Quantidade de prontuários do veterinário (já feitos)
    prontuarios_qtd = Prontuario.objects.filter(
        consulta__veterinario=veterinario
    ).count()

    # Próximas consultas em até 7 dias
    proximas_consultas = Consulta.objects.filter(
        veterinario=veterinario,
        data_hora__gte=hoje,
        data_hora__lte=daqui_7_dias
    ).order_by("data_hora")

    # Histórico completo de consultas
    historico_consultas = Consulta.objects.filter(
        veterinario=veterinario
    ).order_by("-data_hora")

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
        data_hora__date=hoje,
        status__in=['PENDENTE', 'CONFIRMADO'] 
    ).count()
    consultas_pendentes_count = Consulta.objects.filter(
        status__in=['PENDENTE', 'CONFIRMADO'],
        data_hora__date__gte=hoje 
    ).count()
    
    consultas_cadastradas = Consulta.objects.select_related(
        'pet',        
        'veterinario' 
    ).order_by(
        '-data_hora' 
    )[:10]

    contexto = {
        'consultas_do_dia_count': consultas_do_dia_count,
        'consultas_pendentes_count': consultas_pendentes_count,
        'consultas_cadastradas': consultas_cadastradas,
    }

    return render(request, 'clinica/atendente/home_atendente.html', contexto)

def gerenciar_horarios(request):
    if request.method == 'POST':
        form = HorarioDisponivelForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gerenciar_horarios'))
    else:
        form = HorarioDisponivelForm()
    horarios = HorarioDisponivel.objects.all().order_by('data') 
    return render(request, 'clinica/gerenciar_horarios.html', {'form': form, 'horarios': horarios})

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