from django.db import models
from core.models import BaseModel
from django.utils.translation import gettext_lazy as _

class Auditor(BaseModel):
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Data"))
    
    total_time = models.FloatField(verbose_name=_("Tempo Total"))
    python_time = models.FloatField(verbose_name=_("Tempo Python"))
    db_time = models.FloatField(verbose_name=_("Tempo DB"))
    total_queries = models.IntegerField(verbose_name=_("Total de Consultas"))

    path = models.TextField(verbose_name=_("Caminho"))
    method = models.CharField(max_length=10, verbose_name=_("Método"))
    host = models.CharField(max_length=100, verbose_name=_("Host"))
    port = models.IntegerField(null=True, verbose_name=_("Porta"))
    content_type = models.CharField(max_length=100, null=True, verbose_name=_("Tipo de Conteúdo"))
    body = models.TextField(null=True, verbose_name=_("Corpo"))
    user_agent = models.TextField(null=True, verbose_name=_("User Agent"))
    response_content = models.TextField(null=True, verbose_name=_("Conteúdo da Resposta"))
    response_status_code = models.IntegerField(null=True, verbose_name=_("Código de Status da Resposta"))

    ip = models.GenericIPAddressField(null=True, verbose_name=_("IP"))
    proxy_verified = models.BooleanField(null=True, verbose_name=_("Proxy Verificado"))

    def __str__(self):
        return f'{_("Auditor")}: {self.date}'

    class Meta:
        verbose_name = _('Histórico')
        verbose_name_plural = _('Históricos')
