from django import forms
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (CustomUser, ClientePerfil, Pet, Consulta, Prontuario, Ausencia, HorarioDisponivel)

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-mail",
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].label = 'E-mail'

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'nome', 'sobrenome', 'cpf', 'user_type')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'nome', 'sobrenome', 'cpf', 'user_type', 'is_active', 'is_staff', 'is_superuser')

# -------------------------
# Formulários para Ações do Atendente
# -------------------------

class HorarioDisponivelForm(forms.ModelForm):
    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        label="Veterinário"
    )
    
    class Meta:
        model = HorarioDisponivel
        fields = ['veterinario', 'data', 'disponivel']
        widgets = {
            'data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['veterinario'].queryset = CustomUser.objects.filter(user_type='veterinario')

    


# -------------------------
# Formulário para Ação do Veterinário
# -------------------------

class ProntuarioForm(forms.ModelForm):
    receita_prescrita = forms.FileField(
        required=False,
        label="Receita Prescrita (PDF/Imagem)",
        help_text="Faça upload da receita prescrita para o pet (opcional).",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    class Meta:
        model = Prontuario
        fields = [
            'sinais_clinicos',
            'diagnostico',
            'exames_realizados',
            'imunizacao_aplicada',
            'receita_prescrita',
            'observacoes'
        ]
        widgets = {
            'sinais_clinicos': forms.Textarea(attrs={'rows': 5}),
            'diagnostico': forms.Textarea(attrs={'rows': 5}),
            'exames_realizados': forms.Textarea(attrs={'rows': 3}),
            'imunizacao_aplicada': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'sinais_clinicos': 'Sinais Clínicos',
            'diagnostico': 'Diagnóstico',
            'exames_realizados': 'Exames Realizados',
            'imunizacao_aplicada': 'Imunização Aplicada',
            'receita_prescrita': 'Receita Prescrita (PDF/Imagem)',
            'observacoes': 'Observações Adicionais',
        }
        

class AusenciaForm(forms.ModelForm):
    class Meta:
        model = Ausencia
        fields = ['inicio', 'fim', 'motivo']
        widgets = {
            'inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'motivo': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'inicio': 'Início da Ausência',
            'fim': 'Fim da Ausência',
        }


# -------------------------
# Formulários para Ações do Cliente
# -------------------------

class CadastroClienteForm(forms.Form):
    nome = forms.CharField(max_length=30, label="Nome")
    sobrenome = forms.CharField(max_length=30, label="Sobrenome")
    email = forms.EmailField(label="E-mail")
    cpf = forms.CharField(
        label="CPF",
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            message="Digite o CPF no formato 000.000.000-00."
        )],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    telefone = forms.CharField(
        label="Telefone",
        validators=[RegexValidator(
            regex=r'^\(\d{2}\) \d{4,5}-\d{4}$',
            message="Digite o telefone no formato (00) 00000-0000 ou (00) 0000-0000."
        )],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label="Confirme a Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    aceito = forms.BooleanField(
    label="Concordo com as diretrizes do site",
    required=True
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf_limpo = ''.join(filter(str.isdigit, cpf)) 
        if len(cpf_limpo) != 11:
            raise forms.ValidationError("O CPF deve conter exatamente 11 dígitos.")
        return cpf 
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        if not (10 <= len(telefone_limpo) <= 11):
            raise forms.ValidationError("O telefone deve ter 10 ou 11 dígitos.")
        return telefone_limpo

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "As senhas não coincidem.")
            
        return cleaned_data
    

    def save(self, commit=True):
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                nome=self.cleaned_data['nome'],
                sobrenome=self.cleaned_data['sobrenome'],
                cpf=self.cleaned_data['cpf'],
                user_type='cliente'
            )

            ClientePerfil.objects.create(
                user=user,
                telefone=self.cleaned_data.get('telefone', '')
            )
        return user


class CadastroPetForm(forms.ModelForm):
    """ Formulário para o cliente cadastrar um novo pet. """
    class Meta:
        model = Pet
        fields = ['foto_pet', 'nome', 'especie', 'raca', 'peso', 'vacinas_em_dia', 'alergias', 'doencas']


class AgendamentoClienteForm(forms.Form):
    # Campo 1: PET (O cliente só vê os seus)
    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),
        label="Selecione o seu Pet"
    )

    # Campo 2: VETERINÁRIO (Filtra todos os veterinários)
    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        label="Selecione o Veterinário"
    )

    # Campo 3: HORÁRIO DISPONÍVEL (Será preenchido via AJAX/JS após selecionar o veterinário)
    horario_agendado = forms.ModelChoiceField(
        queryset=HorarioDisponivel.objects.none(), # Inicialmente vazio
        label="Horário Disponível",
        # Adicione o atributo 'id' para facilitar a manipulação com JS/AJAX
        widget=forms.Select(attrs={'id': 'id_horario_agendado_ajax'}) 
    )
    
    # Campo 4: MOTIVO
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Descreva o motivo da consulta...'}),
        label="Motivo da Consulta"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            # Filtra os pets apenas para os que pertencem ao cliente logado
            # (Assumo que o campo no Pet se chama 'tutor')
            self.fields['pet'].queryset = Pet.objects.filter(tutor=user).order_by('nome')

            # Filtra todos os usuários que são veterinários
            self.fields['veterinario'].queryset = CustomUser.objects.filter(
                user_type='veterinario'
            ).order_by('nome')
            
    # O método clean garante que os dados sejam válidos, incluindo o horário
    def clean(self):
        cleaned_data = super().clean()
        horario = cleaned_data.get('horario_agendado')
        veterinario = cleaned_data.get('veterinario')
        
        # 1. Validação: Checa se o horário pertence ao veterinário selecionado
        if horario and veterinario and horario.veterinario != veterinario:
             self.add_error('horario_agendado', "O horário selecionado não pertence ao veterinário escolhido.")
             
        # 2. Validação: Checa se o horário ainda está disponível (Dupla checagem)
        if horario and not horario.disponivel:
             self.add_error('horario_agendado', "Este horário não está mais disponível.")
             
        return cleaned_data


    def save(self, user):
        """Salva a consulta e marca o HorarioDisponivel como indisponível."""
        # Se você usar .get() diretamente em clean_data, você terá os objetos do model
        pet_instance = self.cleaned_data.get('pet')
        veterinario_instance = self.cleaned_data.get('veterinario')
        horario_instance = self.cleaned_data.get('horario_agendado')
        motivo = self.cleaned_data.get('motivo')
        
        with transaction.atomic():
            # Cria a instância da consulta
            consulta = Consulta.objects.create(
                pet=pet_instance,
                veterinario=veterinario_instance,
                horario_agendado=horario_instance,
                motivo=motivo,
                status='MARCADA' 
            )
            
            # Marca o horário como indisponível
            horario_instance.disponivel = False
            horario_instance.save()
            
            return consulta

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['pet', 'veterinario', 'horario_agendado', 'motivo', 'status']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'pet': 'Pet',
            'veterinario': 'Veterinário',
            'horario_agendado': 'Horário Agendado',
            'motivo': 'Motivo da Consulta',
            'status': 'Status',
        } 
        
    def clean(self):
        cleaned_data = super().clean()
        veterinario = cleaned_data.get('veterinario')
        horario = cleaned_data.get('horario_agendado')

       
        if veterinario and horario and veterinario != horario.veterinario:
            raise forms.ValidationError(
                "O veterinário selecionado deve corresponder ao veterinário do horário disponível."
            )
        
        return cleaned_data


#=====================
#FILTROS
#=====================

class HorarioFiltroForm(forms.Form):
    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(user_type='veterinario'),
        required=False,
        label="Veterinário"
    )
    data = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Data"
    )
    apenas_disponiveis = forms.BooleanField(
        required=False,
        label="Apenas Disponíveis"
    )

class ConsultaFiltroForm(forms.Form):
    
    # Adiciona 'TODOS' como primeira opção de status
    STATUS_CHOICES_FILTRO = [('TODOS', 'Todos os Status')] + list(Consulta.STATUS_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES_FILTRO,
        required=False,
        label="Status",
        widget=forms.Select(attrs={'class': 'form-select'}) # Adicione classes CSS
    )

    data_inicio = forms.DateField(
        required=False,
        label="Data de Início",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}) # Type 'date' para calendário HTML5
    )
    
    data_fim = forms.DateField(
        required=False,
        label="Data Final",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}) # Type 'date' para calendário HTML5
    )