from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from core.models import BaseModel
from .utils import license_validator


class License(BaseModel):
    """
    Modelo para gerenciar licenças do L2JPremium (Painel Definitivo Lineage)
    """
    LICENSE_TYPES = [
        ('free', _('L2JPremium FREE - Uso Livre')),
        ('pro', _('L2JPremium PRO - Com Vínculo Contratual')),
    ]
    
    LICENSE_STATUS = [
        ('active', _('Ativa')),
        ('expired', _('Expirada')),
        ('suspended', _('Suspensa')),
        ('pending', _('Pendente')),
    ]
    
    license_type = models.CharField(
        max_length=10, 
        choices=LICENSE_TYPES, 
        default='free',
        verbose_name=_("Tipo de Licença")
    )
    
    license_key = models.CharField(
        max_length=64, 
        unique=True,
        verbose_name=_("Chave de Licença")
    )
    
    domain = models.CharField(
        max_length=255,
        verbose_name=_("Domínio Ativado")
    )
    
    company_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Nome da Empresa/Cliente")
    )
    
    contact_email = models.EmailField(
        verbose_name=_("E-mail de Contato")
    )
    
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Telefone de Contato")
    )
    
    status = models.CharField(
        max_length=20,
        choices=LICENSE_STATUS,
        default='pending',
        verbose_name=_("Status da Licença")
    )
    
    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data de Ativação")
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Data de Expiração")
    )
    
    last_verification = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Última Verificação")
    )
    
    verification_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Contador de Verificações")
    )
    
    # Campos específicos do L2JPremium PRO
    contract_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Número do Contrato")
    )
    
    support_hours_used = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Horas de Suporte Utilizadas")
    )
    
    support_hours_limit = models.PositiveIntegerField(
        default=500,
        verbose_name=_("Limite de Horas de Suporte")
    )
    
    # Configurações da licença
    features_enabled = models.JSONField(
        default=dict,
        verbose_name=_("Funcionalidades Habilitadas")
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Observações")
    )
    
    class Meta:
        verbose_name = _("Licença")
        verbose_name_plural = _("Licenças")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_license_type_display()} - {self.domain}"
    
    def save(self, *args, **kwargs):
        # Gera chave de licença se não existir
        if not self.license_key:
            self.license_key = self.generate_license_key()
        
        # Define funcionalidades baseadas no tipo de licença
        if not self.features_enabled:
            self.features_enabled = self.get_default_features()
        
        # Verifica se o status foi alterado
        if self.pk:
            try:
                old_instance = License.objects.get(pk=self.pk)
                status_changed = old_instance.status != self.status
            except License.DoesNotExist:
                status_changed = True
        else:
            status_changed = True
        
        super().save(*args, **kwargs)
        
        # Limpa o cache se o status foi alterado
        if status_changed:
            from django.core.cache import cache
            cache.delete('current_license')
            print(f"[License] Cache limpo devido à mudança de status: {self.status}")
    
    def generate_license_key(self):
        """Gera uma chave de licença única"""
        from .utils import _get_license_validator
        return _get_license_validator().generate_license_key()
    
    def get_default_features(self):
        """Retorna as funcionalidades padrão baseadas no tipo de licença"""
        if self.license_type == 'free':
            return {
                'admin_panel': True,
                'basic_features': True,
                'theme_system': True,
                'api_access': True,
                'support': False,
                'updates': False,
                'customization': False,
                'priority_support': False,
            }
        else:  # pro
            return {
                'admin_panel': True,
                'basic_features': True,
                'theme_system': True,
                'api_access': True,
                'support': True,
                'updates': True,
                'customization': True,
                'priority_support': True,
                'source_code': True,
                'installation_service': True,
                'database_integration': True,
            }
    
    def is_active(self):
        """Verifica se a licença está ativa"""
        if self.status != 'active':
            return False
        
        if self.expires_at and self.expires_at < timezone.now():
            self.status = 'expired'
            self.save()
            return False
        
        return True
    
    def can_use_feature(self, feature_name):
        """Verifica se a licença permite usar uma funcionalidade específica"""
        if not self.is_active():
            return False
        
        return self.features_enabled.get(feature_name, False)
    
    def activate(self, domain):
        """Ativa a licença para um domínio específico"""
        self.domain = domain
        self.status = 'active'
        self.activated_at = timezone.now()
        self.save()
    
    def deactivate(self):
        """Desativa a licença"""
        self.status = 'suspended'
        self.save()
    
    def reactivate(self):
        """Reativa uma licença suspensa"""
        if self.status == 'suspended':
            self.status = 'active'
            self.save()
    
    def renew(self, days=365):
        """Renova a licença por um número específico de dias"""
        if self.expires_at:
            self.expires_at = self.expires_at + timedelta(days=days)
        else:
            self.expires_at = timezone.now() + timedelta(days=days)
        self.status = 'active'
        self.save()


class LicenseVerification(BaseModel):
    """
    Modelo para registrar verificações de licença
    """
    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        related_name='verifications',
        verbose_name=_("Licença")
    )
    
    verification_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data da Verificação")
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name=_("Endereço IP")
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("User Agent")
    )
    
    success = models.BooleanField(
        verbose_name=_("Verificação Bem-sucedida")
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name=_("Mensagem de Erro")
    )
    
    response_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Tempo de Resposta (ms)")
    )
    
    class Meta:
        verbose_name = _("Verificação de Licença")
        verbose_name_plural = _("Verificações de Licença")
        ordering = ['-verification_date']
    
    def __str__(self):
        return f"Verificação {self.license.domain} - {self.verification_date}"
