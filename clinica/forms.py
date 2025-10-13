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
        fields = ['veterinario', 'data']
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
        if CustomUser.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("Este CPF já está cadastrado.")
        return cpf

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
    # ====================================

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
        fields = ['nome', 'especie', 'raca', 'peso', 'vacinas_em_dia', 'alergias', 'doencas']


class AgendamentoClienteForm(forms.Form):
    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),
        label="Selecione o seu Pet"
    )

    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        label="Selecione o Veterinário"
    )

    # NOVO NOME E QUERYSET INICIAL
    horario_agendado = forms.ModelChoiceField(
        queryset=HorarioDisponivel.objects.none(), # Inicialmente vazio
        label="Horário Disponível"
    )
    
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Motivo da Consulta"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields['pet'].queryset = Pet.objects.filter(tutor=user)

            self.fields['veterinario'].queryset = CustomUser.objects.filter(user_type='veterinario')
    

    def save(self, pet_instance, veterinario_instance, horario_instance):
        Consulta.objects.create(
            pet=pet_instance,
            veterinario=veterinario_instance,
            horario_agendado=horario_instance,
            motivo=self.cleaned_data['motivo'],
            status='MARCADA' 
        )

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
