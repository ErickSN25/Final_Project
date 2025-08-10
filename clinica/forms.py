from django import forms
from .models import Veterinario

class VeterinarioForm(forms.Form):
    nome = forms.CharField(max_length=100, label='Nome')
    sobrenome = forms.CharField(max_length=100, label='Sobrenome')
    cpf = forms.CharField(max_length=11, label='CPF')
    crmv = forms.CharField(max_length=10, label='CRMV')
    gmail = forms.EmailField(max_length=100, label='Email')
    senha = forms.CharField(widget=forms.PasswordInput, max_length=100, label='Senha')

    def save(self):
        veterinario = Veterinario(
            nome=self.cleaned_data['nome'],
            sobrenome=self.cleaned_data['sobrenome'],
            cpf=self.cleaned_data['cpf'],
            crmv=self.cleaned_data['crmv'],
            gmail=self.cleaned_data['gmail'],
            senha=self.cleaned_data['senha']
        )
        veterinario.save()