from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from .auth import valida_token
from mentorados.models import DisponibilidadeHorario, Navigator, Mentorado, Reuniao, Tarefa, Upload
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')

@login_required
def mentorados(request):
    template_name = 'mentorados.html'
    navigators = Navigator.objects.filter(user=request.user)
    mentorados = Mentorado.objects.filter(user=request.user)

    estagios_flat = [i[1] for i in Mentorado.estagio_choices]
    qtd_estagios = []

    for i, j in Mentorado.estagio_choices:
        qtd_estagios.append(Mentorado.objects.filter(estagio=i, user=request.user).count())

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
@csrf_exempt
def add_navigator(request):

    nome = request.POST.get('nome_navigator').strip()
    print(nome)
    
    if len(nome) > 0:
        try:
            Navigator(nome=nome, user=request.user).save()
            return render(
                request, 
                'options_navigator.html',
                {'navigators': Navigator.objects.all()}   
            )
        except Exception as e:
            return HttpResponse(f'Erro: {e}.')

    return HttpResponse('Nome não informado !')

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
            mentor=request.user,
            data_inicial__gte=(data - timedelta(minutes=50)),
            data_inicial__lte=(data + timedelta(minutes=50))
        )

        if disponibilidade_horario.exists():
            mensagem = " e ".join(f"{i.data_inicial.strftime('%d-%m-%Y %H:%M')} à {i.data_final.strftime('%d-%m-%Y %H:%M')}" for i in disponibilidade)
            messages.add_message(request, messages.WARNING, f'Você já possui reuniões em aberto entre: {mensagem}')
            return redirect(reverse('reunioes'))

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

def auth_mentorado(request):
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

def escolher_dia(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    #TODO: Fazer autenticação através de Modal, ao invés de redirect
    if not mentorado:
        return redirect(reverse('auth_mentorado'))

    template_name = 'escolher_dia.html'

    disponibilidades = DisponibilidadeHorario.objects.filter(
        data_inicial__gte=datetime.now(),
        agendado=False,
        mentor=mentorado.user
    ).values_list('data_inicial', flat=True)

    # print(disponibilidades.query)

    datas = sorted(list(set([x.date() for x in disponibilidades])))

    return render(request, template_name, {'datas': datas})

def agendar_reuniao(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect(reverse('auth_mentorado'))
    
    template_name = 'agendar_reuniao.html'
    data_str = request.GET.get('data')
    print(data_str)
    data = datetime.strptime(data_str, '%d-%m-%Y')
    print(data)
    horarios = DisponibilidadeHorario.objects.filter(
        data_inicial__gte=data,
        data_inicial__lt=data + timedelta(days=1),
        agendado=False,
        mentor=mentorado.user
    )
    context = {'data': data_str, 'horarios': horarios, 'tags': Reuniao.tag_choices}    

    if request.method == 'POST':
        horario_id = request.POST.get('horario')
        tag = request.POST.get('tag')
        descricao = request.POST.get("descricao")

        if len(horario_id) == 0 or len(tag) == 0 or len(descricao) == 0:
            messages.add_message(request, messages.WARNING, 'Preencha todos os campos !')
            return redirect(f'/mentorados/agendar-reuniao/?data={data_str}')

        try:
            horario = DisponibilidadeHorario.objects.get(id=horario_id)
        except DisponibilidadeHorario.DoesNotExist:
        # if not horario:
            messages.add_message(request, messages.WARNING, 'Este horário não está cadastrado !')
            return redirect(f'/mentorados/agendar-reuniao/?data={data_str}')

        if horario.mentor != mentorado.user:
            messages.add_message(request, messages.WARNING, 'Este horário não pertence ao seu mentor !')
            return redirect(f'/mentorados/agendar-reuniao/?data={data_str}')

        reuniao = Reuniao(
            data_id=horario_id,
            mentorado=mentorado,
            tag=tag,
            descricao=descricao
        )
        #TODO: implementar atomicidade
        try:
            reuniao.save()

            horario = horario
            horario.agendado = True
            horario.save()

            messages.add_message(request, messages.SUCCESS, 'Reunião agendada com sucesso.')
            return redirect(reverse('escolher_dia'))
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')
            return redirect(reverse('agendar_reuniao'))

    return render(request, template_name, context)

@login_required
def tarefa_adicionar(request, id):
    mentorado = Mentorado.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    template_name = 'tarefa_adicionar.html'
    tarefas = Tarefa.objects.filter(mentorado=mentorado)
    videos = Upload.objects.filter(mentorado=mentorado)
    context = {'mentorado': mentorado, 'tarefas': tarefas, 'videos': videos}

    if request.method == 'POST':
        tarefa = request.POST.get('tarefa').strip()

        if len(tarefa) == 0:
            messages.add_message(request, messages.WARNING, 'Tarefa não informada !')
            return redirect(f'/mentorados/{mentorado.id}/tarefa-adicionar/')

        t = Tarefa(
            mentorado=mentorado,
            tarefa=tarefa,
        )
        try:
            t.save()
            messages.add_message(request, messages.SUCCESS, 'Tarefa adicionada com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')
            
        return redirect(f'/mentorados/{mentorado.id}/tarefa-adicionar/')
    
    return render(request, template_name, context)

@login_required
def upload(request, id):
    if request.method == 'POST':
        mentorado = Mentorado.objects.get(id=id)
        if mentorado.user != request.user:
            raise Http404()
        
        video = request.FILES.get('video')
        print(video)

        if not video:
            messages.add_message(request, messages.WARNING, 'Vídeo não escolhido !')
            return redirect(f'/mentorados/{mentorado.id}/tarefa-adicionar/')

        upload = Upload(mentorado=mentorado, video=video)

        try:
            upload.save()
            messages.add_message(request, messages.SUCCESS, 'Vídeo enviado com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')
        
        return redirect(f'/mentorados/{mentorado.id}/tarefa/')

def tarefas(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')
    
    template_name = 'tarefas.html'
    videos = Upload.objects.filter(mentorado=mentorado)
    tarefas = Tarefa.objects.filter(mentorado=mentorado)
    
    context = {'mentorado': mentorado, 'videos': videos, 'tarefas': tarefas}

    return render(request, template_name, context)

@csrf_exempt
def tarefa_concluir(request, id_tarefa):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')

    tarefa = Tarefa.objects.get(id=id_tarefa)

    if mentorado != tarefa.mentorado:
        raise Http404()
    
    tarefa.realizada = not tarefa.realizada
    tarefa.save()

    return HttpResponse('teste')
