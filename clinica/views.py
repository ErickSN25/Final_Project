from django.shortcuts import render,  get_object_or_404
from .models import Veterinario

def home(request):
    return render(request, 'clinica/home.html')


def listar_veterinarios(request):
    veterinarios = Veterinario.objects.all()
    return render(request, 'clinica/listar_veterinarios.html', {'veterinarios': veterinarios})

def veterinario_detalhes(request, id):
    veterinario = get_object_or_404(Veterinario, pk=id)
    return render(request, 'clinica/detalhe_veterinario.html', {'veterinario': veterinario})

