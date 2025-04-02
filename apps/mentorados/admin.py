from django.contrib import admin
from .models import *


class NavigatorAdmin(admin.ModelAdmin):
    model = Navigator
    list_display = ['nome', 'user']

class MentoradoAdmin(admin.ModelAdmin):
    model = Mentorado
    list_display = ['nome', 'estagio', 'user', 'token', 'criado_em']

class DisponibilidadeHorarioAdmin(admin.ModelAdmin):
    model = DisponibilidadeHorario
    list_display = ['data_inicial', 'mentor', 'agendado']

class ReuniaoAdmin(admin.ModelAdmin):
    model = Reuniao
    list_display = ['data', 'mentorado', 'tag', 'descricao']

class TarefaAdmin(admin.ModelAdmin):
    model = Tarefa
    list_display = ['mentorado', 'tarefa', 'realizada']

class UploadAdmin(admin.ModelAdmin):
    model = Upload
    list_display = ['mentorado', 'video']

admin.site.register(Navigator, NavigatorAdmin)
admin.site.register(Mentorado, MentoradoAdmin)
admin.site.register(DisponibilidadeHorario, DisponibilidadeHorarioAdmin)
admin.site.register(Reuniao, ReuniaoAdmin)
admin.site.register(Tarefa, TarefaAdmin)
admin.site.register(Upload, UploadAdmin)
