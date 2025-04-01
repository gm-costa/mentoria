from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from mentorados.models import DisponibilidadeHorario, Navigator, Mentorado, Reuniao


@login_required
def mentorados(request):
    template_name = 'mentorados.html'
    navigators = Navigator.objects.filter(user=request.user)
    mentorados = Mentorado.objects.filter(user=request.user)

    estagios_flat = [i[1] for i in Mentorado.estagio_choices]
    qtd_estagios = []

    for i, j in Mentorado.estagio_choices:
        qtd_estagios.append(Mentorado.objects.filter(estagio=i).count())

    context = {
        'estagios': Mentorado.estagio_choices,
        'navigators': navigators,
        'mentorados': mentorados,
        'estagios_flat': estagios_flat,
        'qtd_estagios': qtd_estagios,
    }
    if request.method == "POST":
        nome = request.POST.get('nome').upper()
        foto = request.FILES.get('foto')
        estagio = request.POST.get("estagio").strip()
        navigator = request.POST.get('navigator').strip()

        context['dados_form'] = request.POST

        if len(nome) == 0 or len(estagio) == 0:
            messages.add_message(request, messages.WARNING, 'Nome e Estágio são obrigatórios !')
            return render(request, template_name, context)

        mentorado = Mentorado(
            nome=nome,
            foto=foto,
            estagio=estagio,
            navigator_id=navigator,
            user=request.user
        )
        try:
            mentorado.save()
            messages.add_message(request, messages.SUCCESS, 'Mentorado cadastrado com sucesso.')
            return redirect(reverse('mentorados'))
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')
            return render(request, template_name, context)
    
    return render(request, template_name, context)

@login_required
def reunioes(request):
    template_name = 'reunioes.html'
    #TODO: a princípio mostrar todas as reunioes, depois filtar pelo template
    reunioes = Reuniao.objects.filter(data__mentor=request.user)
    context = {'reunioes': reunioes}

    if request.method == 'POST':
        data = request.POST.get('data')
        data = datetime.strptime(data, '%Y-%m-%dT%H:%M')

        disponibilidade_horario = DisponibilidadeHorario.objects.filter(
            data_inicial__gte=(data - timedelta(minutes=50)),
            data_inicial__lte=(data + timedelta(minutes=50))
        )

        if disponibilidade_horario.exists():
            mensagem = " e ".join(f"{i.data_inicial.strftime('%d-%m-%Y %H:%M')} à {i.data_final.strftime('%d-%m-%Y %H:%M')}" for i in disponibilidade)
            messages.add_message(request, messages.WARNING, f'Você já possui reuniões em aberto entre: {mensagem}')
            return redirect('reunioes')

        disponibilidade = DisponibilidadeHorario(
            data_inicial=data,
            mentor=request.user
        )
        try:
            disponibilidade.save()
            messages.add_message(request, messages.SUCCESS, 'Horário disponibilizado com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')

        return redirect('reunioes')

    return render(request, template_name, context)

def auth(request):
    template_name = 'auth_mentorado.html'
    if request.method == 'POST':
        token = request.POST.get('token').strip()

        if len(token) == 0:
            messages.add_message(request, messages.WARNING, 'Token não informado !')
            return redirect(reverse('auth_mentorado'))
        
        if not Mentorado.objects.filter(token=token).exists():
            messages.add_message(request, messages.ERROR, 'Token inválido')
            return redirect(reverse('auth_mentorado'))
        
        response = redirect('escolher_dia')
        response.set_cookie('auth_token', token, max_age=3600)
        return response
    
    return render(request, template_name)

def valida_token(token):
    return Mentorado.objects.filter(token=token).first()

def escolher_dia(request):
    template_name = 'escolher_dia.html'
    if not valida_token(request.COOKIES.get('auth_token')):
        #TODO: Fazer através de Modal, ao invés de redirect
        return redirect(reverse('auth_mentorado'))
    if request.method == 'GET':
        disponibilidades = DisponibilidadeHorario.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado=False
        ).values_list('data_inicial', flat=True)
        horarios = []
        for disp in disponibilidades:
            # horarios.append(disp.date().strftime('%d/%m/%Y'))
            horarios.append(disp)

        return render(request, template_name, {'horarios': list(set(horarios))})

def agendar_reuniao(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect(reverse('auth_mentorado'))
    template_name = 'agendar_reuniao.html'
    if request.method == 'GET':
        data = request.GET.get("data")
        data = datetime.strptime(data, '%d-%m-%Y')
        horarios = DisponibilidadeHorario.objects.filter(
            data_inicial__gte=data,
            data_inicial__lt=data + timedelta(days=1),
            agendado=False
        )
        context = {'data': data,'horarios': horarios, 'tags': Reuniao.tag_choices}

        return render(request, template_name, context)

    if request.method == 'POST':
        # rota = request.META['PATH_INFO']
        # print(f'rota:\n{rota}\n')
        #TODO: Solucionar o erro
        horario_id = request.POST.get('horario')
        tag = request.POST.get('tag')
        descricao = request.POST.get("descricao")

        if len(horario_id) == 0 or len(tag) == 0 or len(descricao) == 0:
            messages.add_message(request, messages.WARNING, 'Preencha todos os campos !')
            return redirect(reverse('agendar_reuniao'))

        reuniao = Reuniao(
            data_id=horario_id,
            mentorado=valida_token(request.COOKIES.get('auth_token')),
            tag=tag,
            descricao=descricao
        )
        try:
            reuniao.save()

            horario = DisponibilidadeHorario.objects.get(id=horario_id)
            horario.agendado = True
            horario.save()

            messages.add_message(request, messages.SUCCESS, 'Reunião agendada com sucesso.')
            return redirect(reverse('escolher_dia'))
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')
            return redirect(reverse('agendar_reuniao'))
