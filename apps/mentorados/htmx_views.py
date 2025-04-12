from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from mentorados.models import DisponibilidadeHorario, Navigator, Tarefa
from .auth import valida_token


@login_required
def add_navigator(request):

    nome = request.POST.get('nome_navigator').strip().upper()
    
    if len(nome) > 0:
        Navigator(nome=nome, user=request.user).save()

    navigators = Navigator.objects.filter(user=request.user).order_by('nome')

    return render(request, 'options_navigator.html', {'navigators':  navigators})

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

@login_required
def busca_horarios(request):
    template_name = 'hx/horarios.html'
    data = request.GET.get('data2')
    data = datetime.strptime(data + 'T00:01', '%Y-%m-%dT%H:%M')

    horarios = [str(h).zfill(2) for h in range(8, 18) if h not in (12, 13)]

    disponibilidade_horario = DisponibilidadeHorario.objects.filter(
        mentor=request.user,
        data_inicial__gte=(data),
        data_inicial__lte=(data + timedelta(minutes=(23*60 + 58)))
    )

    list_horarios = [i.data_inicial.strftime('%H') for i in disponibilidade_horario]

    # horarios_disponiveis = sorted(list(set(horarios) - set(list_horarios)))

    context = {'horarios': horarios, 'list_horarios': list_horarios}

    return render(request, template_name, context)
