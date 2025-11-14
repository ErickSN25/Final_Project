from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy  
from .models import (
    ClientePerfil,
    Pet,
    Consulta,
    Prontuario,
    HorarioDisponivel,
)
from .forms import (
    CadastroPetForm,
    ProntuarioForm,
    HorarioDisponivelForm,
    HorarioFiltroForm,
    AgendamentoClienteForm,
    ConsultaFiltroForm,
    ConsultaAtivasFiltroForm,
    ConsultaFinalizadasFiltroForm,
)
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
from django.contrib.auth import update_session_auth_hash
from .forms import ClientePerfilForm, CustomPasswordChangeForm
from django.db.models import OuterRef, Exists
from django.utils.timezone import now


#=====================
# BASIC VIEWS
#=====================


def home(request):
    return render(request, "clinica/home.html")


def cadastro(request):
    from .forms import CadastroClienteForm

    if request.method == "POST":
        form = CadastroClienteForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save(commit=False)
                usuario.set_password(form.cleaned_data["password"])
                usuario.save()

                messages.success(
                    request, "Cadastro realizado com sucesso! Por favor, faça login."
                )
                return redirect("login")

            except Exception as e:
                print(f"ERRO AO SALVAR CADASTRO: {e}")
                messages.error(
                    request,
                    "Ocorreu um erro inesperado ao finalizar seu cadastro. Tente novamente.",
                )

    else:
        form = CadastroClienteForm()

    context = {"form": form}
    return render(request, "clinica/cadastro.html", context)


#=====================
# CUSTOM LOGIN VIEWS
#=====================


class CustomLoginView(LoginView):
    template_name = "clinica/home.html"
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        user = self.request.user
        print(
            f"DEBUG: Usuário logado: {user.email}, Tipo detectado: '{user.user_type}'"
        )
        if user.user_type == "cliente":
            return reverse_lazy("home_user")

        elif user.user_type == "veterinario":
            return reverse_lazy("home_vet")

        elif user.user_type == "atendente":
            return reverse_lazy("home_atendente")

        elif user.user_type == "administrador":
            return reverse_lazy("admin:index")

        return reverse_lazy("home")


#=====================
# REDIRECT VIEWS
#=====================


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


#=====================
# CLIENT VIEWS
#=====================


@login_required
def home_user(request):
    pets = Pet.objects.filter(tutor=request.user)
    consultas = Consulta.objects.filter(pet__tutor=request.user).order_by(
        "-horario_agendado"
    )[:5]
    context = {
        "user": request.user,
        "pets": pets,
        "consultas": consultas,
    }
    return render(request, "clinica/user/home_user.html", context)


@login_required
def meus_pets_view(request):
    pets = Pet.objects.filter(tutor=request.user).order_by("nome")
    context = {
        "pets": pets,
        "titulo_pagina": "Meus Pets",
    }
    return render(request, "clinica/user/meus_pets.html", context)


@login_required
def cadastrar_pet_view(request):
    if request.method == "POST":
        form = CadastroPetForm(request.POST, request.FILES)
        if form.is_valid():
            novo_pet = form.save(commit=False)
            novo_pet.tutor = request.user
            novo_pet.save()
            messages.success(
                request, f'O pet "{novo_pet.nome}" foi cadastrado com sucesso!'
            )
            return redirect("meus_pets")

    else:
        form = CadastroPetForm()

    context = {
        "form": form,
        "titulo_pagina": "Cadastrar Novo Pet",
    }

    return render(request, "clinica/user/cadastrar_pet.html", context)


@login_required
def excluir_pet_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, tutor=request.user)

    if request.method == "POST":
        nome_pet = pet.nome
        pet.delete()
        messages.warning(request, f'O pet "{nome_pet}" foi removido com sucesso.')
    return redirect("meus_pets")


@login_required
def detalhes_pet_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, tutor=request.user)
    hoje = date.today()
    context = {
        "pet": pet,
        "titulo_pagina": f"Detalhamento dos dados de {pet.nome}",
    }
    return render(request, "clinica/user/detalhes_pet.html", context)


@login_required
def editar_pet_form_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, tutor=request.user)

    if request.method == "POST":
        form = CadastroPetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Os dados de "{pet.nome}" foram atualizados com sucesso.'
            )
            return redirect("detalhes_pet", pet_id=pet.id)
    else:
        form = CadastroPetForm(instance=pet)

    context = {
        "form": form,
        "pet": pet,
        "titulo_pagina": f"Editar Dados: {pet.nome}",
    }
    return render(request, "clinica/user/editar_pet.html", context)


@login_required
def minhas_consultas_view(request):
    if request.user.user_type != "cliente":
        return redirect("home_user")
    form_filtro = ConsultaFiltroForm(request.GET)
    consultas_queryset = (
        Consulta.objects.filter(pet__tutor=request.user)
        .select_related("pet", "veterinario", "horario_agendado")
        .order_by("-horario_agendado__data")
    )

    if form_filtro.is_valid():
        status_filter = form_filtro.cleaned_data.get("status")
        data_inicio = form_filtro.cleaned_data.get("data_inicio")
        data_fim = form_filtro.cleaned_data.get("data_fim")

        if status_filter and status_filter != "TODOS":
            consultas_queryset = consultas_queryset.filter(status=status_filter)

        if data_inicio:
            consultas_queryset = consultas_queryset.filter(
                horario_agendado__data__date__gte=data_inicio
            )

        if data_fim:
            data_fim_exclusiva = data_fim + timezone.timedelta(days=1)
            consultas_queryset = consultas_queryset.filter(
                horario_agendado__data__date__lt=data_fim_exclusiva
            )

    PAGINATION_SIZE = 5
    paginator = Paginator(consultas_queryset, PAGINATION_SIZE)
    page_number = request.GET.get("page")
    consultas = paginator.get_page(page_number)

    context = {
        "consultas": consultas,
        "form_filtro": form_filtro,
        "consultas_list_vazia": not consultas_queryset.exists() and not request.GET,
    }

    return render(request, "clinica/user/consultas_user.html", context)


def agendar_consulta_view(request):
    if request.user.user_type != "cliente":
        messages.error(request, "Apenas clientes podem agendar consultas.")
        return redirect("consultas_user")

    if request.method == "POST":
        form = AgendamentoClienteForm(request.POST, user=request.user)

        veterinario_id = request.POST.get("veterinario")
        if veterinario_id:
            form.fields["horario_agendado"].queryset = HorarioDisponivel.objects.filter(
                veterinario_id=veterinario_id, disponivel=True
            )

        if form.is_valid():
            horario = form.cleaned_data["horario_agendado"]
            motivo = form.cleaned_data["motivo"]
            pet = form.cleaned_data["pet"]

            Consulta.objects.create(
                pet=pet,
                veterinario=horario.veterinario,
                horario_agendado=horario,
                motivo=motivo,
                status="MARCADA",
            )

            horario.disponivel = False
            horario.save()

            messages.success(request, "Consulta agendada com sucesso!")
            return redirect("consultas_user")
    else:
        form = AgendamentoClienteForm(user=request.user)

    return render(
        request,
        "clinica/user/cadastrar_consulta.html",
        {"form": form, "titulo": "Agendar Nova Consulta"},
    )


@require_GET
def obter_horarios_disponiveis_ajax(request):
    veterinario_id = request.GET.get("veterinario_id")

    if not veterinario_id:
        return JsonResponse([], safe=False)

    try:
        horarios = HorarioDisponivel.objects.filter(
            veterinario_id=veterinario_id, disponivel=True
        ).order_by("data")

        horarios_data = [
            {"id": h.id, "display": localtime(h.data).strftime("%d/%m/%Y às %H:%M")}
            for h in horarios
        ]
        return JsonResponse(horarios_data, safe=False)
    except Exception as e:
        print("ERRO AO OBTER HORÁRIOS:", e)
        return JsonResponse([], safe=False)


@login_required
def detalhe_consulta_view(request, pk):
    try:
        consulta = (
            Consulta.objects.filter(pk=pk, pet__tutor=request.user)
            .select_related("pet", "veterinario", "horario_agendado")
            .get()
        )

    except Consulta.DoesNotExist:
        return render(
            request,
            "clinica/erro_acesso.html",
            {"mensagem": "Consulta não encontrada ou acesso negado."},
            status=404,
        )

    try:
        prontuario = Prontuario.objects.get(consulta=consulta)
        
    except Prontuario.DoesNotExist:
            prontuario = None

    context = {
            "consulta": consulta,
            "prontuario": prontuario,   
        }
    return render(request, "clinica/user/detalhes_consulta.html", context)


@login_required
def perfil_user(request):
    try:
        perfil = request.user.clienteperfil
    except ClientePerfil.DoesNotExist:
        perfil = ClientePerfil.objects.create(user=request.user)
    form_perfil = ClientePerfilForm(instance=perfil)
    form_password_change = CustomPasswordChangeForm(user=request.user)
    if request.method == "POST":
        if "submit_endereco" in request.POST:
            form_perfil = ClientePerfilForm(
                request.POST, request.FILES, instance=perfil
            )
            if form_perfil.is_valid():
                form_perfil.save()
                messages.success(
                    request,
                    "Suas informações e foto de perfil foram atualizadas com sucesso!",
                )
                return redirect("perfil_user")
            else:
                messages.error(
                    request,
                    "Houve um erro na atualização do Perfil. Verifique os campos.",
                )
        elif "submit_senha" in request.POST:
            form_password_change = CustomPasswordChangeForm(
                user=request.user, data=request.POST
            )

            if form_password_change.is_valid():
                user = form_password_change.save()
                update_session_auth_hash(request, user)

                messages.success(
                    request,
                    "Sua senha foi alterada com sucesso! Você pode fazer login com sua nova senha.",
                )
                return redirect("perfil_user")
            else:
                messages.error(
                    request,
                    "Houve um erro na alteração da senha. Verifique sua senha atual e as novas senhas.",
                )
                form_perfil = ClientePerfilForm(instance=perfil)

    context = {
        "form_endereco": form_perfil,
        "form_password_change": form_password_change,
        "perfil": perfil,
    }
    return render(request, "clinica/user/perfil_user.html", context)

@login_required
def prontuario_view(request, pk):
    prontuario = get_object_or_404(
        Prontuario.objects.select_related("consulta__pet", "consulta__veterinario"),
        pk=pk
    )

    consulta = prontuario.consulta
    pet = consulta.pet

    context = {
        "prontuario": prontuario,
        "consulta": consulta,
        "pet": pet,
    }

    return render(request, "clinica/user/prontuario_user.html", context)




#=====================
# VETS VIEWS
#=====================


@login_required
def home_vet(request):
    if request.user.user_type != "veterinario":
        messages.error(request, "Acesso não autorizado.")
        return redirect("home")

    veterinario = request.user
    hoje = now().date()
    consultas_futuras_e_andamento = (
        Consulta.objects.filter(
            veterinario=veterinario,
            horario_agendado__data__gte=now() - timedelta(minutes=30),
        )
        .filter(status__in=["MARCADA", "EM_ANDAMENTO"])
        .order_by("horario_agendado__data")
    )
    consultas_hoje = consultas_futuras_e_andamento.filter(
        horario_agendado__data__date=hoje
    )
    count_em_andamento = consultas_hoje.filter(status="EM_ANDAMENTO").count()
    count_marcadas = consultas_futuras_e_andamento.filter(status="MARCADA").count()
    prontuarios_pendentes = (
        Consulta.objects.filter(
            veterinario=veterinario, status__in=["REALIZADA", "EM_ANDAMENTO"]
        )
        .annotate(
            prontuario_finalizado=Exists(
                Prontuario.objects.filter(consulta=OuterRef("pk"), finalizado=True)
            )
        )
        .exclude(prontuario_finalizado=True)
        .count()
    )
    proximas_consultas = consultas_futuras_e_andamento[:5]

    context = {
        "count_em_andamento": count_em_andamento,
        "count_marcadas": count_marcadas,
        "count_prontuarios_pendentes": prontuarios_pendentes,
        "proximas_consultas": proximas_consultas,
    }
    return render(request, "clinica/vet/home_vet.html", context)


@login_required
def lista_consultas_vet(request):
    """
    Lista consultas em duas seções (Ativas e Finalizadas) com filtros independentes.
    """
    if request.user.user_type != "veterinario":
        messages.error(request, "Acesso negado.")
        return redirect("home")

    veterinario = request.user
    hoje = timezone.now().date()


    form_ativas = ConsultaAtivasFiltroForm(request.GET)

    consultas_ativas_qs = (
        Consulta.objects.filter(
            veterinario=veterinario, status__in=["MARCADA", "EM_ANDAMENTO"]
        )
        .select_related("pet", "pet__tutor", "horario_agendado")
        .order_by("horario_agendado__data")
    )

    if form_ativas.is_valid():
        data_inicio = form_ativas.cleaned_data.get("data_inicio")
        data_fim = form_ativas.cleaned_data.get("data_fim")
        query_busca_ativas = request.GET.get("q_ativas")

        if data_inicio:
            consultas_ativas_qs = consultas_ativas_qs.filter(
                horario_agendado__data__date__gte=data_inicio
            )
        if data_fim:
            data_fim_exclusiva = data_fim + timedelta(days=1)
            consultas_ativas_qs = consultas_ativas_qs.filter(
                horario_agendado__data__date__lt=data_fim_exclusiva
            )
        if query_busca_ativas:
            consultas_ativas_qs = consultas_ativas_qs.filter(
                Q(pet__nome__icontains=query_busca_ativas)
                | Q(pet__tutor__first_name__icontains=query_busca_ativas)
                | Q(pet__tutor__last_name__icontains=query_busca_ativas)
                | Q(status__icontains=query_busca_ativas)
            )

    paginator_ativas = Paginator(consultas_ativas_qs, 5)
    page_number_ativas = request.GET.get(
        "page_ativas"
    )
    consultas_ativas = paginator_ativas.get_page(page_number_ativas)


    form_finalizadas = ConsultaFinalizadasFiltroForm(request.GET)

    consultas_finalizadas_qs = (
        Consulta.objects.filter(
            veterinario=veterinario, status__in=["REALIZADA", "CANCELADA"]
        )
        .select_related("pet", "pet__tutor", "horario_agendado")
        .order_by("-horario_agendado__data")
    )


    consultas_finalizadas_qs = consultas_finalizadas_qs.annotate(
        has_prontuario=Exists(Prontuario.objects.filter(consulta_id=OuterRef("pk")))
    )

    if form_finalizadas.is_valid():
        status_filter = form_finalizadas.cleaned_data.get("status")
        prontuario_filter = form_finalizadas.cleaned_data.get("prontuario_status")
        query_busca_finalizadas = request.GET.get("q_finalizadas")

        if status_filter:
            consultas_finalizadas_qs = consultas_finalizadas_qs.filter(
                status=status_filter
            )

        if prontuario_filter == "ok":
            consultas_finalizadas_qs = consultas_finalizadas_qs.filter(
                has_prontuario=True
            )
        elif prontuario_filter == "pendente":

            consultas_finalizadas_qs = consultas_finalizadas_qs.filter(
                has_prontuario=False, status="REALIZADA"
            )

        if query_busca_finalizadas:
            consultas_finalizadas_qs = consultas_finalizadas_qs.filter(
                Q(pet__nome__icontains=query_busca_finalizadas)
                | Q(pet__tutor__first_name__icontains=query_busca_finalizadas)
                | Q(pet__tutor__last_name__icontains=query_busca_finalizadas)
            )


    paginator_finalizadas = Paginator(consultas_finalizadas_qs, 5)
    page_number_finalizadas = request.GET.get(
        "page_finalizadas"
    )
    consultas_finalizadas = paginator_finalizadas.get_page(page_number_finalizadas)


    context = {
        "consultas_ativas": consultas_ativas,
        "form_ativas": form_ativas,
        "consultas_finalizadas": consultas_finalizadas,
        "form_finalizadas": form_finalizadas,
    }

    return render(request, "clinica/vet/lista_consultas_vet.html", context)


@login_required
def detalhe_consulta_vet(request, consulta_id):
    consulta = get_object_or_404(
        Consulta.objects.select_related(
            "pet__tutor", "pet__tutor__clienteperfil", "horario_agendado__veterinario"
        ).prefetch_related("pet__tutor__pet_set"),
        id=consulta_id,
        veterinario=request.user,
    )
    try:
        prontuario = Prontuario.objects.get(consulta=consulta)
        prontuario_existe = True
        prontuario_finalizado = prontuario.finalizado
    except Prontuario.DoesNotExist:
        prontuario = None
        prontuario_existe = False
        prontuario_finalizado = False

    tutor = consulta.pet.tutor
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "iniciar_consulta" and consulta.status == "MARCADA":
            consulta.status = "EM_ANDAMENTO"
            consulta.save(update_fields=["status"])
            messages.success(
                request, f"Consulta de {consulta.pet.nome} iniciada (Em Andamento)!"
            )
            return redirect("detalhe_consulta_vet", consulta_id=consulta.id)

        else:
            messages.error(request, "Ação inválida para o status atual da consulta.")
            return redirect("detalhe_consulta_vet", consulta_id=consulta.id)

    context = {
        "consulta": consulta,
        "tutor": tutor,
        "perfil_tutor": ClientePerfil.objects.filter(user=tutor).first(),
        "pets_do_tutor": Pet.objects.filter(tutor=tutor).exclude(id=consulta.pet.id),
        "prontuario": prontuario,
        "prontuario_existe": prontuario_existe,
        "prontuario_finalizado": prontuario_finalizado,
        "titulo_pagina": f"Detalhes da Consulta - {consulta.pet.nome}",
    }
    return render(request, "clinica/vet/detalhe_consulta_vet.html", context)

@login_required
def cadastrar_prontuario_vet(request, consulta_id):
    consulta = get_object_or_404(
        Consulta.objects.select_related("pet__tutor"),
        id=consulta_id,
        veterinario=request.user,
    )
    if consulta.status == "MARCADA":
        consulta.status = "EM_ANDAMENTO"
        consulta.save(update_fields=["status"])

    try:
        prontuario = Prontuario.objects.get(consulta=consulta)
    except Prontuario.DoesNotExist:
        prontuario = Prontuario(consulta=consulta)

    if request.method == "POST":
        form = ProntuarioForm(request.POST, request.FILES, instance=prontuario)
        action = request.POST.get("action")

        if form.is_valid():
            prontuario_salvo = form.save(commit=False)

            if action == "finalizar":
                prontuario_salvo.finalizado = True
                messages.success(
                    request,
                    f"Prontuário de {consulta.pet.nome} finalizado com sucesso! Status da consulta alterado para 'Realizada'.",
                )
            else:
                prontuario_salvo.finalizado = False
                messages.info(
                    request, "Prontuário salvo como rascunho. Continue o atendimento!"
                )

            prontuario_salvo.save()
            return redirect("detalhe_consulta_vet", consulta_id=consulta.id)

    else:
        form = ProntuarioForm(instance=prontuario)

    context = {
        "form": form,
        "consulta": consulta,
        "prontuario": prontuario,
        "is_new": prontuario.pk is None,
        "titulo_pagina": f"Prontuário de {consulta.pet.nome}",
    }
    return render(request, "clinica/vet/cadastrar_prontuario_vet.html", context)


#=====================
# ATTENDANT VIEWS
#=====================


def gerenciar_horarios(request):
    horarios = HorarioDisponivel.objects.all().order_by("data")
    for horario in horarios:
        horario.consulta = Consulta.objects.filter(horario_agendado=horario).first()

    filtro_form = HorarioFiltroForm(request.GET or None)

    if filtro_form.is_valid():
        veterinario = filtro_form.cleaned_data.get("veterinario")
        if veterinario:
            horarios = horarios.filter(veterinario=veterinario)

        data = filtro_form.cleaned_data.get("data")
        if data:
            horarios = horarios.filter(data__date=data)

        apenas_disponiveis = filtro_form.cleaned_data.get("apenas_disponiveis")
        if apenas_disponiveis:
            horarios = horarios.filter(disponivel=True)

    paginator = Paginator(horarios, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    contexto = {
        "horarios": page_obj,
        "page_obj": page_obj,
        "filtro_form": filtro_form,
    }

    return render(request, "clinica/atd/home_atendente.html", contexto)


def criar_horario(request):
    if request.method == "POST":
        form = HorarioDisponivelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Horário criado com sucesso!")
            return redirect("home_atendente")
    else:
        form = HorarioDisponivelForm()

    return render(request, "clinica/atd/criar_horario.html", {"form": form})


def editar_horario(request, horario_id):
    """Edita um horário existente."""
    horario = get_object_or_404(HorarioDisponivel, id=horario_id)
    if request.method == "POST":
        form = HorarioDisponivelForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return redirect("home_atendente")
    else:
        form = HorarioDisponivelForm(instance=horario)

    return render(
        request, "clinica/atd/editar_horario.html", {"form": form, "horario": horario}
    )


def excluir_horario(request, horario_id):
    """Confirma e exclui um horário."""
    horario = get_object_or_404(HorarioDisponivel, id=horario_id)
    if request.method == "POST":
        horario.delete()
        return redirect("home_atendente")
    return render(request, "clinica/atd/excluir_horario.html", {"horario": horario})
