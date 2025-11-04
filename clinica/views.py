from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
<<<<<<< HEAD
from django.urls import reverse
from django.db import transaction
from .models import CustomUser, ClientePerfil, Pet, Consulta, Agendamento, Prontuario, HorarioDisponivel, Notificacao
from .forms import CadastroPetForm, AgendamentoClienteForm, ProntuarioForm, HorarioDisponivelForm, ConsultaForm

=======
from django.urls import reverse, reverse_lazy # Adicionei reverse_lazy
from django.db import transaction
from .models import CustomUser, ClientePerfil, Pet, Consulta, Prontuario, HorarioDisponivel, Notificacao
from .forms import CadastroPetForm, ProntuarioForm, HorarioDisponivelForm, ConsultaForm, HorarioFiltroForm, AgendamentoClienteForm, ConsultaFiltroForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from datetime import date
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.timezone import localtime




# --- VIEWS PÚBLICAS / BÁSICAS ---
>>>>>>> f15c0c4d666df049388a13fdf66a37f1a3d6debf

def home(request):
    return render(request, 'clinica/home.html')

def cadastro(request):
    from .forms import CadastroClienteForm 

    if request.method == 'POST':
<<<<<<< HEAD
        pass
    return render(request, 'clinica/cadastro.html')

def login(request):
    if request.method == 'POST':
        pass
    return render(request, 'clinica/login.html')

def perfil_cliente(request, cliente_id):
    cliente = get_object_or_404(ClientePerfil, id=cliente_id)
    pets = Pet.objects.filter(tutor=cliente.user)
    agendamentos = Agendamento.objects.filter(pet__in=pets).order_by('-data_hora')
    return render(request, 'clinica/perfil_cliente.html', {'cliente': cliente, 'pets': pets, 'agendamentos': agendamentos})

def perfil_veterinario(request, veterinario_id):
    veterinario = get_object_or_404(CustomUser, id=veterinario_id, user_type='veterinario')
    consultas = Consulta.objects.filter(veterinario=veterinario).order_by('-data')
    return render(request, 'clinica/perfil_veterinario.html', {'veterinario': veterinario, 'consultas': consultas})

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

def agendamento(request):
    if request.method == 'POST':
        form = AgendamentoClienteForm(request.POST, user=request.user)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.status = 'MARCADO'
            agendamento.save()
            return redirect('perfil_cliente', cliente_id=request.user.clienteperfil.id)
    else:
        form = AgendamentoClienteForm(user=request.user)
    return render(request, 'clinica/agendamento.html', {'form': form})

def prontuario(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    prontuarios = Prontuario.objects.filter(pet=pet).order_by('-data')
    if request.method == 'POST':
        form = ProntuarioForm(request.POST)
        if form.is_valid():
            prontuario = form.save(commit=False)
            prontuario.pet = pet
            prontuario.save()
            return redirect('prontuario', pet_id=pet.id)
    else:
        form = ProntuarioForm()
    return render(request, 'clinica/prontuario.html', {'pet': pet, 'prontuarios': prontuarios, 'form': form})

def gerenciar_horarios(request):
    if request.method == 'POST':
        form = HorarioDisponivelForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gerenciar_horarios'))
    else:
        form = HorarioDisponivelForm()
    horarios = HorarioDisponivel.objects.all().order_by('data_hora')
    return render(request, 'clinica/gerenciar_horarios.html', {'form': form, 'horarios': horarios})

def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, pet__tutor=request.user)
    agendamento.status = 'CANCELADO'
    agendamento.save()
    return redirect('perfil_cliente', cliente_id=request.user.clienteperfil.id)

def detalhes_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    return render(request, 'clinica/detalhes_consulta.html', {'consulta': consulta})

def marcar_consulta(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, pet__tutor=request.user)
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.pet = agendamento.pet
            consulta.veterinario = agendamento.veterinario
            consulta.status = 'MARCADA'
            consulta.save()
            agendamento.status = 'REALIZADO'
            agendamento.save()
            return redirect('perfil_cliente', cliente_id=request.user.clienteperfil.id)
    else:
        form = ConsultaForm()
    return render(request, 'clinica/marcar_consulta.html', {'form': form, 'agendamento': agendamento})
=======
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
def meus_pets_view(request):
    pets = Pet.objects.filter(tutor=request.user).order_by('nome')
    context = {
        'pets': pets,
        'titulo_pagina': 'Meus Pets',
    }
    return render(request, 'clinica/user/meus_pets.html', context)

@login_required
def cadastrar_pet_view(request):
    if request.method == 'POST':
        form = CadastroPetForm(request.POST, request.FILES)
        if form.is_valid():
            novo_pet = form.save(commit=False)
            novo_pet.tutor = request.user
            novo_pet.save()
            messages.success(request, f'O pet "{novo_pet.nome}" foi cadastrado com sucesso!')
            return redirect('meus_pets')
    
    else:
        form = CadastroPetForm()
        
    context = {
        'form': form,
        'titulo_pagina': 'Cadastrar Novo Pet',
    }

    return render(request, 'clinica/user/cadastrar_pet.html', context)

@login_required
def excluir_pet_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, tutor=request.user)
    
    if request.method == 'POST':
        nome_pet = pet.nome
        pet.delete()
        messages.warning(request, f'O pet "{nome_pet}" foi removido com sucesso.')
    return redirect('meus_pets')

@login_required
def detalhes_pet_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, tutor=request.user)
    hoje = date.today()
    context = {
        'pet': pet,
        'titulo_pagina': f'Detalhamento dos dados de {pet.nome}',
    }
    return render(request, 'clinica/user/detalhes_pet.html', context)

@login_required
def editar_pet_form_view(request, pet_id): 
    pet = get_object_or_404(Pet, id=pet_id, tutor=request.user)
    
    if request.method == 'POST':
        form = CadastroPetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f'Os dados de "{pet.nome}" foram atualizados com sucesso.')
            return redirect('detalhes_pet', pet_id=pet.id) 
    else:
        form = CadastroPetForm(instance=pet)
        
    context = {
        'form': form,
        'pet': pet,
        'titulo_pagina': f'Editar Dados: {pet.nome}',
    }
    return render(request, 'clinica/user/editar_pet.html', context) 


@login_required
def minhas_consultas_view(request):
    """
    Lista as consultas do cliente logado com opções de filtro por status e data.
    """
    # Verifica se o usuário é um cliente/tutor
    if request.user.user_type != 'cliente':
        # Redireciona para onde for apropriado para outros tipos de usuário
        return redirect('home_user') 

    # Inicializa o formulário de filtro com os dados do GET (filtros)
    form_filtro = ConsultaFiltroForm(request.GET)
    
    # 1. Queryset Base: Filtra Consultas onde o TUTOR (do Pet) é o usuário logado
    # IMPORTANTE: Ajuste 'pet__tutor' para 'pet__dono' se for o nome do campo no seu modelo Pet
    consultas_queryset = Consulta.objects.filter(
        pet__tutor=request.user 
    ).select_related('pet', 'veterinario', 'horario_agendado').order_by('-horario_agendado__data')

    # 2. Lógica de Filtragem (Usando o Form Limpo)
    if form_filtro.is_valid():
        status_filter = form_filtro.cleaned_data.get('status')
        data_inicio = form_filtro.cleaned_data.get('data_inicio')
        data_fim = form_filtro.cleaned_data.get('data_fim')
        
        # Filtro por Status
        if status_filter and status_filter != 'TODOS':
            consultas_queryset = consultas_queryset.filter(status=status_filter)
        
        # Filtro por Data de Início (>= data_inicio)
        if data_inicio:
            consultas_queryset = consultas_queryset.filter(
                horario_agendado__data__date__gte=data_inicio
            )

        # Filtro por Data Final (< data_fim + 1 dia)
        if data_fim:
            data_fim_exclusiva = data_fim + timezone.timedelta(days=1)
            consultas_queryset = consultas_queryset.filter(
                horario_agendado__data__date__lt=data_fim_exclusiva
            )

    # 3. Paginação
    PAGINATION_SIZE = 5 
    paginator = Paginator(consultas_queryset, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    consultas = paginator.get_page(page_number)
    
    
    # 4. Contexto
    context = {
        'consultas': consultas,
        'form_filtro': form_filtro,
        # Verifica se o queryset inicial está vazio E se não há filtros aplicados
        'consultas_list_vazia': not consultas_queryset.exists() and not request.GET, 
    }
    
    return render(request, 'clinica/user/consultas_user.html', context)

@login_required
def agendar_consulta_view(request):
    """
    Permite ao cliente agendar uma nova consulta.
    """
    if request.user.user_type != 'cliente':
        messages.error(request, "Apenas clientes podem agendar consultas.")
        return redirect('consultas_user') # Ou para a página inicial
    
    if request.method == 'POST':
        # Passa request.POST e o user para o form
        form = AgendamentoClienteForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                # O método save() do form lida com a criação da Consulta e atualização do HorarioDisponivel
                form.save(user=request.user)
                messages.success(request, "Consulta agendada com sucesso!")
                return redirect('consultas_user')
            except Exception as e:
                # Caso ocorra um erro na transação ou salvamento (ex: horário indisponível)
                messages.error(request, f"Ocorreu um erro ao agendar: {e}")
                
    else:
        # GET: Inicializa o formulário, filtrando os pets do cliente
        form = AgendamentoClienteForm(user=request.user)
    
    context = {
        'form': form,
        'titulo': 'Agendar Nova Consulta'
    }
    return render(request, 'clinica/user/cadastrar_consulta.html', context)



from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.timezone import localtime

@require_GET
def obter_horarios_disponiveis_ajax(request):
    veterinario_id = request.GET.get('veterinario_id')

    if not veterinario_id:
        return JsonResponse([], safe=False)

    try:
        # Filtra SOMENTE horários disponíveis para esse veterinário
        horarios = HorarioDisponivel.objects.filter(
            veterinario_id=veterinario_id,
            disponivel=True
        ).order_by('data')

        horarios_data = [
            {
                'id': h.id,
                'display': localtime(h.data).strftime('%d/%m/%Y às %H:%M')
            }
            for h in horarios
        ]
        return JsonResponse(horarios_data, safe=False)
    except Exception as e:
        print("❌ ERRO AO OBTER HORÁRIOS:", e)
        return JsonResponse([], safe=False)


@login_required
def detalhe_consulta_view(request, pk):
    try:
        consulta = Consulta.objects.filter(
            pk=pk, 
            pet__tutor=request.user
        ).select_related('pet', 'veterinario', 'horario_agendado').get()

    except Consulta.DoesNotExist:
        # Se a consulta não existir ou não pertencer ao usuário
        return render(request, 'clinica/erro_acesso.html', {'mensagem': 'Consulta não encontrada ou acesso negado.'}, status=404)
    
    context = {
        'consulta': consulta,
    }
    # O template 'detalhe_consulta.html' já foi fornecido no passo anterior.
    return render(request, 'clinica/detalhes_consulta.html', context)


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

>>>>>>> f15c0c4d666df049388a13fdf66a37f1a3d6debf

def prontuario_veterinario(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id, veterinario=request.user)
    try:
        prontuario = Prontuario.objects.get(consulta=consulta)
    except Prontuario.DoesNotExist:
        prontuario = None
    if request.method == 'POST':
<<<<<<< HEAD
        form = ProntuarioForm(request.POST, instance=prontuario)
=======
        form = ProntuarioForm(request.POST, request.FILES, instance=prontuario) 
>>>>>>> f15c0c4d666df049388a13fdf66a37f1a3d6debf
        if form.is_valid():
            prontuario = form.save(commit=False)
            prontuario.consulta = consulta
            prontuario.save()
            return redirect('detalhes_consulta', consulta_id=consulta.id)
    else:
        form = ProntuarioForm(instance=prontuario)
    return render(request, 'clinica/prontuario_veterinario.html', {'form': form, 'consulta': consulta, 'prontuario': prontuario})

<<<<<<< HEAD
=======

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
>>>>>>> f15c0c4d666df049388a13fdf66a37f1a3d6debf
def notificacoes(request):
    notificacoes = Notificacao.objects.filter(tutor=request.user).order_by('-criada_em')
    return render(request, 'clinica/notificacoes.html', {'notificacoes': notificacoes})

<<<<<<< HEAD
=======
@login_required
>>>>>>> f15c0c4d666df049388a13fdf66a37f1a3d6debf
def marcar_notificacao_como_lida(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, tutor=request.user)
    notificacao.lida = True
    notificacao.save()
<<<<<<< HEAD
    return redirect('notificacoes')
=======
    return redirect('notificacoes')
>>>>>>> f15c0c4d666df049388a13fdf66a37f1a3d6debf
