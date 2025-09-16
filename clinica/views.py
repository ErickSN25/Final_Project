from django.shortcuts import render,  get_object_or_404

def home(request):
    return render(request, 'clinica/home.html')

def cadastro(request):
    if request.method == 'POST':
        pass
    return render(request, 'clinica/cadastro.html')
