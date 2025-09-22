from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import (
    CustomUser,
    ClientePerfil,
    Pet,
    Consulta,
    Prontuario,
    Ausencia,
    HorarioDisponivel
)

# Formulários para Ações do Atendente

class HorarioDisponivelForm(forms.ModelForm):
    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(user_type='veterinario'),
        label="Veterinário"
    )
    
    class Meta:
        model = HorarioDisponivel
        fields = ['veterinario', 'data']
        widgets = {
            'data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# Formulário para Ação do Veterinário

class ProntuarioForm(forms.ModelForm):
    receita_prescrita = forms.FileField(
        required=False,
        label="Receita Prescrita (PDF/Imagem)",
        help_text="Faça upload da receita prescrita para o pet (opcional)."
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


# Formulários para Ações do Cliente

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
        required=False,
        validators=[RegexValidator(
            regex=r'^\(\d{2}\) \d{4}-\d{4}$',
            message="Digite o telefone no formato (00) 0000-0000."
        )],
        widget=forms.TextInput(attrs={'class': 'form-control'})
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

    def save(self):
        # Esta lógica de save será usada na view para criar os dois objetos
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=self.cleaned_data['email'],
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
    """
    Formulário para o cliente cadastrar um novo pet.
    """
    class Meta:
        model = Pet
        fields = ['nome', 'especie', 'raca', 'peso', 'vacinas_em_dia', 'alergias', 'doencas']


class AgendamentoClienteForm(forms.Form):
    pet = forms.ModelChoiceField(
        queryset=Pet.objects.none(),
        label="Selecione o seu Pet"
    )

    veterinario = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(user_type='veterinario'),
        label="Selecione o Veterinário"
    )

    horario = forms.ModelChoiceField(
        queryset=HorarioDisponivel.objects.none(),
        required=False,
        label="Horário Disponível"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['pet'].queryset = Pet.objects.filter(tutor=user)
            
