from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from .models import CustomUser, ClientePerfil, Pet, Consulta, Agendamento, Prontuario, HorarioDisponivel, Notificacao
from .forms import CadastroPetForm, AgendamentoClienteForm, ProntuarioForm, HorarioDisponivelForm, ConsultaForm


def home(request):
    return render(request, 'clinica/home.html')

def cadastro(request):
    if request.method == 'POST':
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

def prontuario_veterinario(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id, veterinario=request.user)
    try:
        prontuario = Prontuario.objects.get(consulta=consulta)
    except Prontuario.DoesNotExist:
        prontuario = None
    if request.method == 'POST':
        form = ProntuarioForm(request.POST, instance=prontuario)
        if form.is_valid():
            prontuario = form.save(commit=False)
            prontuario.consulta = consulta
            prontuario.save()
            return redirect('detalhes_consulta', consulta_id=consulta.id)
    else:
        form = ProntuarioForm(instance=prontuario)
    return render(request, 'clinica/prontuario_veterinario.html', {'form': form, 'consulta': consulta, 'prontuario': prontuario})

def notificacoes(request):
    notificacoes = Notificacao.objects.filter(tutor=request.user).order_by('-criada_em')
    return render(request, 'clinica/notificacoes.html', {'notificacoes': notificacoes})

def marcar_notificacao_como_lida(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, tutor=request.user)
    notificacao.lida = True
    notificacao.save()
    return redirect('notificacoes')
