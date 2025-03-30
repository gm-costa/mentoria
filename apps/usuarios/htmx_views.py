from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User


def check_username(request):
    username = request.GET.get('usuario').lower()

    try:
        user = User.objects.get(username=username)
        return HttpResponse('Este usuário já existe !')
    except User.DoesNotExist:
        return HttpResponse('')

def check_email(request):
    email = request.GET.get('email').lower()

    try:
        user = User.objects.get(email=email)
        return HttpResponse('Este e-mail já existe !')
    except User.DoesNotExist:
        return HttpResponse('')

def check_senha(request):
    senha = request.GET.get('senha')

    if len(senha.strip()) > 0 and len(senha.strip()) < 6:
        return HttpResponse('A senha deve conter 6 ou mais caracteres !')
    else:
        return HttpResponse('')
