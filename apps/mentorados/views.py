from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from mentorados.models import Navigator, Mentorado


def mentorados(request):
    template_name = 'mentorados.html'
    navigators = Navigator.objects.filter(user=request.user.id).all()
    mentorados = Mentorado.objects.filter(user=request.user.id).all()

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
