from datetime import timedelta
import secrets
from django.db import models
from django.contrib.auth.models import User

class Navigator(models.Model):
    nome = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome
    
class Mentorado(models.Model):
    estagio_choices = (
        ('E1', '10-100k'),
        ('E2', '100-1KK')
    )
    nome = models.CharField(max_length=255)
    foto = models.ImageField(upload_to='fotos', null=True, blank=True)
    estagio = models.CharField(max_length=2, choices=estagio_choices)
    navigator = models.ForeignKey(Navigator, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=16, null=True, blank=True)
    criado_em = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token: 
            self.token = self.gerar_token_unico()
        super().save(*args, **kwargs)

    def gerar_token_unico(self):
        while True:
            token = secrets.token_urlsafe(8)
            if not Mentorado.objects.filter(token=token).exists():
                return token
 
    def __str__(self):
        return self.nome

class DisponibilidadeHorario(models.Model):
    data_inicial = models.DateTimeField(null=True, blank=True)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    agendado = models.BooleanField(default=False)

    @property
    def data_final(self):
        return self.data_inicial + timedelta(minutes=50)
    
class Reuniao(models.Model):
    tag_choices = (
        ('G', 'Gestão'),
        ('M', 'Marketing'),
        ('RH', 'Gestão de pessoas'),
        ('I', 'Impostos')
    )

    data = models.ForeignKey(DisponibilidadeHorario, on_delete=models.CASCADE)
    mentorado = models.ForeignKey(Mentorado, on_delete=models.CASCADE)
    tag = models.CharField(max_length=2, choices=tag_choices)
    descricao = models.TextField()

    class Meta:
        verbose_name_plural = 'reunioes'
