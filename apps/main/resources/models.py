from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class SystemResource(BaseModel):
    """
    Modelo para controlar quais recursos do sistema estão ativos ou inativos
    """
    name = models.CharField(_("Nome do Recurso"), max_length=100, unique=True)
    display_name = models.CharField(_("Nome de Exibição"), max_length=150)
    description = models.TextField(_("Descrição"), blank=True, null=True)
    is_active = models.BooleanField(_("Ativo"), default=True)
    category = models.CharField(_("Categoria"), max_length=50, choices=[
        ('shop', _('Loja')),
        ('wallet', _('Carteira')),
        ('social', _('Rede Social')),
        ('games', _('Jogos')),
        ('auction', _('Leilões')),
        ('inventory', _('Inventário')),
        ('payment', _('Pagamentos')),
        ('notification', _('Notificações')),
        ('api', _('API')),
        ('admin', _('Administração')),
        ('other', _('Outros')),
    ])
    icon = models.CharField(_("Ícone"), max_length=50, blank=True, null=True, 
                           help_text=_("Classe CSS do ícone (ex: fas fa-shopping-cart)"))
    order = models.PositiveIntegerField(_("Ordem"), default=0, 
                                       help_text=_("Ordem de exibição no painel"))
    
    class Meta:
        verbose_name = _("Recurso do Sistema")
        verbose_name_plural = _("Recursos do Sistema")
        ordering = ['category', 'order', 'display_name']

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.display_name}"

    @classmethod
    def is_resource_active(cls, resource_name):
        """
        Verifica se um recurso específico está ativo
        """
        try:
            resource = cls.objects.get(name=resource_name)
            return resource.is_active
        except cls.DoesNotExist:
            # Se o recurso não existir, considera como ativo por padrão
            return True

    @classmethod
    def get_active_resources_by_category(cls, category):
        """
        Retorna todos os recursos ativos de uma categoria específica
        """
        return cls.objects.filter(category=category, is_active=True).order_by('order', 'display_name')

    @classmethod
    def get_all_resources_by_category(cls):
        """
        Retorna todos os recursos organizados por categoria
        """
        resources = {}
        for resource in cls.objects.all().order_by('category', 'order', 'display_name'):
            if resource.category not in resources:
                resources[resource.category] = []
            resources[resource.category].append(resource)
        return resources
