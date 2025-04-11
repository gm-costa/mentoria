from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def cadastro(request):
    if request.user.is_authenticated:
        sair(request)
    
    template_name = 'cadastro.html'
    if request.method == "POST":
        username = request.POST.get('usuario').lower()
        email = request.POST.get("email").lower()
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get('confirmar_senha')

        context = {
            'username': username,
            'email': email,
            'senha': senha,
            'confirmar_senha': confirmar_senha,
        }
        
        if not all(('username', 'email', 'senha', 'confirmar_senha')):
            messages.add_message(request, messages.WARNING, 'Preencha todos os campos !')
            return render(request, template_name, context)
        
        if len(senha.strip()) < 6:
            messages.add_message(request, messages.WARNING, 'A senha deve conter 6 ou mais caracteres !')
            return render(request, template_name, context)
        
        if senha != confirmar_senha:
            messages.add_message(request, messages.WARNING, 'Senhas diferentes !')
            return render(request, template_name, context)

        users = User.objects.filter(username=username)

        if users.exists():
            messages.add_message(request, messages.WARNING, 'Já existe um usuário com este nome.')
            return render(request, template_name, context)

        users_email = User.objects.filter(email=email)

        if users_email.exists():
            messages.add_message(request, messages.WARNING, 'Já existe um usuário com este e-mail.')
            return render(request, template_name, context)
        
        try:
            User.objects.create_user(
                username=username,
                email=email,
                password=senha
            )
            messages.add_message(request, messages.SUCCESS, 'Cadastro efetuado com sucesso, efetue login.')
            return render(request, 'login.html', {'username': username})
            
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e} !')

        return render(request, template_name, context)

    return render(request, template_name)

def logar(request):
    if request.user.is_authenticated:
        sair(request)
    
    template_name = 'login.html'
    if request.method == 'POST':
        username = request.POST.get('usuario').lower()
        senha = request.POST.get('senha')

        context = {
            'username': username,
            'senha': senha,
        }

        if not all(('username', 'senha')):
            messages.add_message(
                request, messages.WARNING, 'Preencha todos os campos!'
            )
            return render(request, template_name, context)
        
        if len(senha.strip()) < 6:
            messages.add_message(request, messages.WARNING, 'A senha deve conter 6 ou mais caracteres !')
            return render(request, template_name, context)
        
        if not User.objects.filter(username=username):
            messages.add_message(
                request, messages.WARNING, 'Usuário não cadastrado !'
            )
            return render(request, template_name, context)
        
        user = authenticate(request, username=username, password=senha)

        if user:
            login(request, user)
            return redirect('mentorados')

        messages.add_message(request, messages.ERROR, 'Senha inválida !')
        return render(request, template_name, context)

    return render(request, template_name)

def sair(request):
    logout(request)
    return redirect('home')
