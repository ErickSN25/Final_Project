from django.shortcuts import render,  get_object_or_404
from .models import Veterinario

def home(request):
    return render(request, 'clinica/home.html')

def cadastro(request):
    if request.method == 'POST':
        pass
    return render(request, 'clinica/cadastro.html')
