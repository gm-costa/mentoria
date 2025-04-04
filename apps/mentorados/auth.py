
from .models import Mentorado


def valida_token(token):
    return Mentorado.objects.filter(token=token).first()
