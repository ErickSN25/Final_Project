from django.shortcuts import render,  get_object_or_404
from .models import Veterinario
from .forms import VeterinarioForm
from django.shortcuts import redirect

def home(request):
    return render(request, 'clinica/home.html')


def listar_veterinarios(request):
    veterinarios = Veterinario.objects.all()
    return render(request, 'clinica/listar_veterinarios.html', {'veterinarios': veterinarios})

def veterinario_detalhes(request, id):
    veterinario = get_object_or_404(Veterinario, pk=id)
    return render(request, 'clinica/detalhe_veterinario.html', {'veterinario': veterinario})

def cadastrar_veterinario(request):
    if request.method == 'POST':
        form = VeterinarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_veterinarios')
    else:
        form = VeterinarioForm()
    return render(request, 'clinica/cadastrar_veterinario.html', {'form': form})

def editar_veterinario(request, id):
    veterinario = get_object_or_404(Veterinario, pk=id)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        if not nome:
        # Trate erro, ou retorne uma mensagem para o usuário
            return render(request, 'clinica/editar_veterinario.html', {
            'veterinario': veterinario,
            'error': 'O campo nome é obrigatório.'
    })
        veterinario.nome = nome

        veterinario.sobrenome = request.POST.get('sobrenome')
        veterinario.cpf = request.POST.get('cpf')
        veterinario.crmv = request.POST.get('crmv')
        veterinario.gmail = request.POST.get('gmail')
        veterinario.save()
        return redirect('listar_veterinarios')  # redireciona para a lista após salvar

    context = {'veterinario': veterinario}
    return render(request, 'clinica/editar_veterinario.html', context)

def deletar_veterinario(request, id):
    veterinario = get_object_or_404(Veterinario, pk=id)
    if request.method == 'POST':
        veterinario.delete()
        return redirect('listar_veterinarios')
    return render(request, 'clinica/deletar_veterinario.html', {'veterinario': veterinario})