from datetime import datetime, timedelta
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .auth import valida_token
from mentorados.models import DisponibilidadeHorario, Navigator, Mentorado, Reuniao, Tarefa, Upload
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db import transaction


def home(request):
    c_hide = '' if request.GET.get('src') else 'hidden'
    return render(request, 'home.html', {'c_hide': c_hide})

@login_required
def mentorados(request):
    template_name = 'mentorados.html'
    navigators = Navigator.objects.filter(user=request.user).order_by('nome')
    mentorados = Mentorado.objects.filter(user=request.user).order_by('nome')

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
        nome = request.POST.get('nome').strip().upper()
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
    data_filter = request.GET.get('data-filter')
    mentorado_filter = request.GET.get('mentorado-filter')

    reunioes = Reuniao.objects.filter(data__mentor=request.user)

    if data_filter:
        data_filter_date = datetime.strptime(data_filter + 'T00:01', '%Y-%m-%dT%H:%M')
        reunioes = reunioes.filter(
            data__data_inicial__gte=data_filter_date,
            data__data_inicial__lte=(data_filter_date + timedelta(minutes=(23*60 + 58)))
        )
    if mentorado_filter:
        reunioes = reunioes.filter(mentorado__nome__icontains=mentorado_filter)

    context = {'reunioes': reunioes, 'data_filter': data_filter, 'mentorado_filter': mentorado_filter}

    if request.method == 'POST':
        data = request.POST.get('data')
        horarios_list = request.POST.getlist('horario')

        disponibilidades = []
        for hora in horarios_list:
            dt = datetime.strptime(data+'T'+hora+':00', '%Y-%m-%dT%H:%M')

            disponibilidade_horario = DisponibilidadeHorario.objects.filter(mentor=request.user, data_inicial=dt)

            if disponibilidade_horario.exists():
                messages.add_message(request, messages.WARNING, f"Você já possui reunião em {dt.strftime('%d/%m/%Y')} às {dt.strftime('%H:%M')}")
                return redirect('reunioes')
            
            disponibilidades.append(DisponibilidadeHorario(data_inicial=dt, mentor=request.user))

        try:
            DisponibilidadeHorario.objects.bulk_create(disponibilidades)
            mensagem = 'Horários disponibilizados' if len(disponibilidades) > 1 else 'Horário disponibilizado'
            messages.add_message(request, messages.SUCCESS, f'{mensagem} com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')

        return redirect('reunioes')

    return render(request, template_name, context)

def auth_mentorado(request):
    body = json.loads(request.body)
    token = body['token']
    if len(token) == 0:
        return JsonResponse({'status': 2, 'mensagem': 'Token não informado !'})
    
    if not Mentorado.objects.filter(token=token).exists():
        return JsonResponse({'status': 1, 'mensagem': 'Token inválido.'})
    
    return JsonResponse({'status': 0, 'mensagem': 'Sucesso'})

def escolher_dia(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('/mentorados/home/?src=escolher-dia')
    
    template_name = 'escolher_dia.html'

    if mentorado:
        disponibilidades = DisponibilidadeHorario.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado=False,
            mentor=mentorado.user
        ).values_list('data_inicial', flat=True)

        datas = sorted(list(set([x.date() for x in disponibilidades])))

        return render(request, template_name, {'datas': datas})
    
    return render(request, template_name)

def agendar_reuniao(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('/mentorados/home/?src=escolher-dia')
    
    template_name = 'agendar_reuniao.html'
    data_str = request.GET.get('data')
    data = datetime.strptime(data_str, '%d-%m-%Y')
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

        try:
            with transaction.atomic():
                reuniao.save()
                # horario = horario
                # horario.agendado = True
                # horario.save()
                reuniao.data.agendado = True
                reuniao.data.save()

            messages.add_message(request, messages.SUCCESS, 'Reunião agendada com sucesso.')
            return redirect(reverse('escolher_dia'))
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')
            return redirect(f'/mentorados/agendar-reuniao/?data={data_str}')

    return render(request, template_name, context)

@login_required
def tarefa_adicionar(request, id): #id do mentorado
    mentorado = Mentorado.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    template_name = 'tarefa_adicionar.html'
    tarefas = Tarefa.objects.filter(mentorado=mentorado)
    videos = Upload.objects.filter(mentorado=mentorado)
    context = {'mentorado': mentorado, 'tarefas': tarefas, 'videos': videos}

    if request.method == 'POST':
        tarefa_descricao = request.POST.get('tarefa').strip()

        if len(tarefa_descricao) == 0:
            messages.add_message(request, messages.WARNING, 'Tarefa não informada !')
            return redirect(f'/mentorados/{mentorado.id}/tarefa-adicionar/')

        tarefa = Tarefa(
            mentorado=mentorado,
            tarefa=tarefa_descricao,
        )
        try:
            tarefa.save()
            messages.add_message(request, messages.SUCCESS, 'Tarefa adicionada com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')
            
        return redirect(f'/mentorados/{mentorado.id}/tarefa-adicionar/')
    
    return render(request, template_name, context)

@login_required
def upload(request, id): #id do mentorado
    if request.method == 'POST':
        mentorado = Mentorado.objects.get(id=id)
        if mentorado.user != request.user:
            raise Http404()
        
        video = request.FILES.get('video')

        if not video:
            messages.add_message(request, messages.WARNING, 'Vídeo não escolhido !')
            return redirect(f'/mentorados/{mentorado.id}/tarefa-adicionar/')

        upload = Upload(mentorado=mentorado, video=video)

        try:
            upload.save()
            messages.add_message(request, messages.SUCCESS, 'Vídeo enviado com sucesso.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}.')
        
        return redirect(f'/mentorados/{mentorado.id}/tarefa-adicionar/')

def tarefas(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('/mentorados/home/?src=tarefas')
    
    template_name = 'tarefas.html'
    videos = Upload.objects.filter(mentorado=mentorado)
    tarefas = Tarefa.objects.filter(mentorado=mentorado)
    
    context = {'mentorado': mentorado, 'videos': videos, 'tarefas': tarefas}

    return render(request, template_name, context)
