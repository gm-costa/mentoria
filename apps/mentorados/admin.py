from django.contrib import admin
from .models import Mentorado


class MentoradoAdmin(admin.ModelAdmin):
    model = Mentorado
    list_display = ['nome', 'estagio', 'user', 'criado_em']

admin.site.register(Mentorado, MentoradoAdmin)
