from django import forms
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    CustomUser,
    ClientePerfil,
    Pet,
    Consulta,
    Prontuario,
    HorarioDisponivel,
)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model


# =====================
# CUSTOM USERS FORMS
# =====================


User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-mail",
        max_length=254,
        widget=forms.TextInput(attrs={"autofocus": True}),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].label = "E-mail"


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "nome", "sobrenome", "cpf", "user_type")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "nome",
            "sobrenome",
            "cpf",
            "user_type",
            "is_active",
            "is_staff",
            "is_superuser",
        )


# =====================
# ATTENDANT FORMS
# =====================


class HorarioDisponivelForm(forms.ModelForm):
    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(), label="Veterinário"
    )

    class Meta:
        model = HorarioDisponivel
        fields = ["veterinario", "data", "disponivel"]
        widgets = {
            "data": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["veterinario"].queryset = CustomUser.objects.filter(
            user_type="veterinario"
        )


# =====================
# VETS FORMS
# =====================


class ProntuarioForm(forms.ModelForm):
    receita_prescrita = forms.FileField(
        required=False,
        label="Receita Prescrita (PDF/Imagem)",
        help_text="Faça upload da receita prescrita para o pet (opcional).",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"])
        ],
    )

    class Meta:
        model = Prontuario
        fields = [
            "sinais_clinicos",
            "diagnostico",
            "exames_realizados",
            "imunizacao_aplicada",
            "receita_prescrita",
            "observacoes",
            "finalizado",
        ]
        widgets = {
            "sinais_clinicos": forms.Textarea(attrs={"rows": 5}),
            "diagnostico": forms.Textarea(attrs={"rows": 5}),
            "exames_realizados": forms.Textarea(attrs={"rows": 3}),
            "imunizacao_aplicada": forms.Textarea(attrs={"rows": 3}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
            "finalizado": forms.CheckboxInput(),
        }
        labels = {
            "sinais_clinicos": "Sinais Clínicos",
            "diagnostico": "Diagnóstico",
            "exames_realizados": "Exames Realizados",
            "imunizacao_aplicada": "Imunização Aplicada",
            "receita_prescrita": "Receita Prescrita (PDF/Imagem)",
            "observacoes": "Observações Adicionais",
            "finalizado": "Prontuário Finalizado",
        }


# =====================
# USERS FORMS
# =====================


class CadastroClienteForm(forms.Form):
    nome = forms.CharField(max_length=30, label="Nome")
    sobrenome = forms.CharField(max_length=30, label="Sobrenome")
    email = forms.EmailField(label="E-mail")
    cpf = forms.CharField(
        label="CPF",
        validators=[
            RegexValidator(
                regex=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$",
                message="Digite o CPF no formato 000.000.000-00.",
            )
        ],
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    telefone = forms.CharField(
        label="Telefone",
        validators=[
            RegexValidator(
                regex=r"^\(\d{2}\) \d{4,5}-\d{4}$",
                message="Digite o telefone no formato (00) 00000-0000 ou (00) 0000-0000.",
            )
        ],
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password_confirm = forms.CharField(
        label="Confirme a Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    aceito = forms.BooleanField(
        label="Concordo com as diretrizes do site", required=True
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        cpf_limpo = "".join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            raise forms.ValidationError("O CPF deve conter exatamente 11 dígitos.")
        return cpf

    def clean_telefone(self):
        telefone = self.cleaned_data.get("telefone")
        telefone_limpo = "".join(filter(str.isdigit, telefone))
        if not (10 <= len(telefone_limpo) <= 11):
            raise forms.ValidationError("O telefone deve ter 10 ou 11 dígitos.")
        return telefone_limpo

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=self.cleaned_data["email"],
                password=self.cleaned_data["password"],
                nome=self.cleaned_data["nome"],
                sobrenome=self.cleaned_data["sobrenome"],
                cpf=self.cleaned_data["cpf"],
                user_type="cliente",
            )

            ClientePerfil.objects.create(
                user=user, telefone=self.cleaned_data.get("telefone", "")
            )
        return user


# =====================
# PETS FORMS
# =====================


class CadastroPetForm(forms.ModelForm):
    """Formulário para o cliente cadastrar um novo pet."""

    class Meta:
        model = Pet
        fields = [
            "foto_pet",
            "nome",
            "especie",
            "raca",
            "peso",
            "vacinas_em_dia",
            "alergias",
            "doencas",
        ]


class AgendamentoClienteForm(forms.Form):

    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(), label="Selecione o seu Pet"
    )

    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(), label="Selecione o Veterinário"
    )

    horario_agendado = forms.ModelChoiceField(
        queryset=HorarioDisponivel.objects.none(),
        label="Horário Disponível",
        widget=forms.Select(attrs={"id": "id_horario_agendado_ajax"}),
    )

    motivo = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "Descreva o motivo da consulta..."}
        ),
        label="Motivo da Consulta",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields["pet"].queryset = Pet.objects.filter(tutor=user).order_by(
                "nome"
            )
            self.fields["veterinario"].queryset = CustomUser.objects.filter(
                user_type="veterinario"
            ).order_by("nome")

    def clean(self):
        cleaned_data = super().clean()
        horario = cleaned_data.get("horario_agendado")
        veterinario = cleaned_data.get("veterinario")

        if horario and veterinario and horario.veterinario != veterinario:
            self.add_error(
                "horario_agendado",
                "O horário selecionado não pertence ao veterinário escolhido.",
            )

        if horario and not horario.disponivel:
            self.add_error("horario_agendado", "Este horário não está mais disponível.")

        return cleaned_data

    def save(self, user):
        """Salva a consulta e marca o HorarioDisponivel como indisponível."""

        pet_instance = self.cleaned_data.get("pet")
        veterinario_instance = self.cleaned_data.get("veterinario")
        horario_instance = self.cleaned_data.get("horario_agendado")
        motivo = self.cleaned_data.get("motivo")

        with transaction.atomic():

            consulta = Consulta.objects.create(
                pet=pet_instance,
                veterinario=veterinario_instance,
                horario_agendado=horario_instance,
                motivo=motivo,
                status="MARCADA",
            )

            horario_instance.disponivel = False
            horario_instance.save()

            return consulta


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ["pet", "veterinario", "horario_agendado", "motivo", "status"]
        widgets = {
            "motivo": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "pet": "Pet",
            "veterinario": "Veterinário",
            "horario_agendado": "Horário Agendado",
            "motivo": "Motivo da Consulta",
            "status": "Status",
        }

    def clean(self):
        cleaned_data = super().clean()
        veterinario = cleaned_data.get("veterinario")
        horario = cleaned_data.get("horario_agendado")

        if veterinario and horario and veterinario != horario.veterinario:
            raise forms.ValidationError(
                "O veterinário selecionado deve corresponder ao veterinário do horário disponível."
            )

        return cleaned_data


# =====================
# PERFIL FORMS
# =====================
class ClientePerfilForm(forms.ModelForm):

    class Meta:
        model = ClientePerfil
        fields = (
            "foto_user",
            "telefone",
            "endereco",
            "numero",
            "bairro",
            "cidade",
            "estado",
        )

        widgets = {
            "foto_user": forms.FileInput(attrs={"class": "form-control-file"}),
            "telefone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "(XX) XXXXX-XXXX"}
            ),
            "endereco": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Rua/Avenida..."}
            ),
            "numero": forms.TextInput(attrs={"class": "form-control"}),
            "bairro": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
        }

        labels = {
            "foto_user": "Foto de Perfil",
            "telefone": "Telefone",
            "endereco": "Rua/Avenida (Logradouro)",
            "numero": "Número",
            "bairro": "Bairro",
            "cidade": "Cidade",
            "estado": "Estado",
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


# =====================
# FILTERS FORMS
# =====================


class HorarioFiltroForm(forms.Form):
    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(user_type="veterinario"),
        required=False,
        label="Veterinário",
    )
    data = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Data"
    )
    apenas_disponiveis = forms.BooleanField(required=False, label="Apenas Disponíveis")


class ConsultaFiltroForm(forms.Form):

    STATUS_CHOICES_FILTRO = [("TODOS", "Todos os Status")] + list(
        Consulta.STATUS_CHOICES
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES_FILTRO,
        required=False,
        label="Status",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    data_inicio = forms.DateField(
        required=False,
        label="Data de Início",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    data_fim = forms.DateField(
        required=False,
        label="Data Final",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )


class VeterinarioConsultaFiltroForm(forms.Form):
    STATUS_CONSULTA_CHOICES = [("TODOS", "Todos os Status")] + [
        (s[0], s[1])
        for s in Consulta.STATUS_CHOICES
        if s[0] in ["MARCADA", "EM_ANDAMENTO", "REALIZADA", "CANCELADA"]
    ]

    STATUS_PRONTUARIO_CHOICES = [
        ("TODOS", "Todos"),
        ("PENDENTE", "Prontuário Pendente"),
        ("FINALIZADO", "Prontuário Finalizado"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CONSULTA_CHOICES,
        required=False,
        label="Status da Consulta",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    prontuario_status = forms.ChoiceField(
        choices=STATUS_PRONTUARIO_CHOICES,
        required=False,
        label="Status Prontuário",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    data_inicio = forms.DateField(
        required=False,
        label="Data a Partir de",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    data_fim = forms.DateField(
        required=False,
        label="Data Até",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    pesquisa = forms.CharField(
        required=False,
        label="Pet/Tutor/Motivo",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nome do Pet ou Tutor..."}
        ),
    )


class ConsultaFinalizadasFiltroForm(forms.Form):

    PRONTUARIO_STATUS_CHOICES = [
        ("", "Status Prontuário"),
        ("pendente", "Pendente"),
        ("ok", "Finalizado"),
    ]

    STATUS_CHOICES = [
        ("", "Status Consulta"),
        ("REALIZADA", "Realizada"),
        ("CANCELADA", "Cancelada"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    prontuario_status = forms.ChoiceField(
        choices=PRONTUARIO_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class ConsultaAtivasFiltroForm(forms.Form):
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )


class PetsFiltroForm(forms.Form):

    ESPECIES_CHOICES_FILTRO = [("TODAS", "Todas as espécies")] + list(
        Pet.especieChoices
    )

    nome = forms.CharField(
        required=False,
        label="Pet",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nome do Pet..."}
        ),
    )

    vacinas_em_dia = forms.BooleanField(required=False, label="Vacinas em dia")

    especie = forms.ChoiceField(
        choices=ESPECIES_CHOICES_FILTRO,
        required=False,
        label="Status",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
