from django.contrib import admin
from .models import Mentorado, Reuniao


class MentoradoAdmin(admin.ModelAdmin):
    model = Mentorado
    list_display = ['nome', 'estagio', 'user', 'criado_em']

class ReuniaoAdmin(admin.ModelAdmin):
    model = Reuniao
    list_display = ['data', 'mentorado', 'tag', 'descricao']

admin.site.register(Mentorado, MentoradoAdmin)
admin.site.register(Reuniao, ReuniaoAdmin)
