from django.urls import path
from . import views


urlpatterns = [
    path('', views.mentorados, name='mentorados'),
    path('reunioes/', views.reunioes, name='reunioes'),
    path('autenticar/', views.auth_mentorado, name="auth_mentorado"),
    path('escolher-dia/', views.escolher_dia, name='escolher_dia'),
    path('agendar-reuniao/', views.agendar_reuniao, name='agendar_reuniao'),
    path('<int:id>/tarefa-adicionar/', views.tarefa_adicionar, name='tarefa_adicionar'),
    path('<int:id>/upload/', views.upload, name='upload'),
    path('tarefas/', views.tarefas, name='tarefas'),
    path('tarefa-concluir/<int:id_tarefa>/', views.tarefa_concluir, name='tarefa_concluir'),
]
