from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel, BaseModelAbstract
from .utils import validate_cpf, remove_cpf_mask
from encrypted_fields.encrypted_fields import *
from encrypted_fields.encrypted_files import *
from utils.choices import *
from django.core.validators import validate_email
from .validators import validate_ascii_username
from django_ckeditor_5.fields import CKEditor5Field
from datetime import date
from django.utils.translation import gettext_lazy as _


class User(BaseModel, AbstractUser):
    username = models.CharField(
        max_length=16,
        unique=True,
        verbose_name=_("Nome de usuário"),
        validators=[validate_ascii_username],
        help_text=_("Use apenas letras e números. Sem espaços ou símbolos.")
    )

    email = models.EmailField(
        unique=True,
        verbose_name=_("E-mail"),
        validators=[validate_email]
    )

    avatar = EncryptedImageField(upload_to="avatars", verbose_name=_("Foto de perfil"), null=True, blank=True)
    bio = EncryptedTextField(verbose_name=_('Biografia'), blank=True, null=True, max_length=500)
    cpf = EncryptedCharField(verbose_name=_('CPF'), max_length=14, blank=True, null=True, validators=[validate_cpf])
    gender = EncryptedCharField(verbose_name=_('Gênero'), max_length=50, choices=GENDER_CHOICES, blank=True, null=True)
    website = models.URLField(verbose_name=_('Website'), blank=True, help_text=_('Link para seu site pessoal'))
    
    is_email_verified = models.BooleanField(default=False, verbose_name=_("E-mail verificado"))
    is_2fa_enabled = models.BooleanField(default=False, verbose_name=_("2FA habilitado"))
    is_verified_account = models.BooleanField(default=False, verbose_name=_("Conta verificada"), help_text=_("Indica se a conta foi verificada pela equipe"))
    social_verified = models.BooleanField(default=False, verbose_name=_("Verificado na rede social"), help_text=_("Indica se o usuário é verificado na rede social"))

    # Tipos de perfil
    is_superadmin = models.BooleanField(default=False, verbose_name=_("Super Administrador"), help_text=_("Acesso total ao sistema"))
    is_staff_member = models.BooleanField(default=False, verbose_name=_("Membro da Equipe"), help_text=_("Acesso administrativo limitado"))
    is_moderator = models.BooleanField(default=False, verbose_name=_("Moderador"), help_text=_("Pode acessar o painel de moderação do social"))
    is_verified_user = models.BooleanField(default=False, verbose_name=_("Usuário Verificado"), help_text=_("Perfil com destaque azul"))
    is_apoiador = models.BooleanField(default=False, verbose_name=_("Apoiador"), help_text=_("Perfil com destaque vermelho"))

    # game
    fichas = models.PositiveIntegerField(default=0, verbose_name=_("Fichas"))

    def save(self, *args, **kwargs):
        # Remove a máscara do CPF antes de salvar no banco
        if self.cpf:
            self.cpf = remove_cpf_mask(self.cpf)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    @property
    def profile_type(self):
        """Retorna o tipo de perfil do usuário"""
        if self.is_superadmin:
            return 'superadmin'
        elif self.is_staff_member:
            return 'staff'
        elif self.is_moderator:
            return 'moderator'
        elif self.is_verified_user:
            return 'verified'
        elif self.is_apoiador:
            return 'supporter'
        else:
            return 'regular'

    @property
    def profile_display_name(self):
        """Retorna o nome de exibição do tipo de perfil"""
        profile_names = {
            'superadmin': 'Imperador Supremo',
            'staff': 'Guardião do Sistema',
            'moderator': 'Vigilante da Comunidade',
            'verified': 'Membro Verificado',
            'supporter': 'Apoiador',
            'regular': 'Membro'
        }
        return profile_names.get(self.profile_type, 'Membro')

    @property
    def profile_color_class(self):
        """Retorna a classe CSS para cor do perfil"""
        color_classes = {
            'superadmin': 'profile-superadmin',
            'staff': 'profile-staff',
            'moderator': 'profile-moderator',
            'verified': 'profile-verified',
            'supporter': 'profile-supporter',
            'regular': 'profile-regular'
        }
        return color_classes.get(self.profile_type, 'profile-regular')

    @property
    def profile_icon(self):
        """Retorna o ícone do tipo de perfil"""
        icons = {
            'superadmin': 'bi-crown-fill',
            'staff': 'bi-shield-fill',
            'moderator': 'bi-shield-check',
            'verified': 'bi-patch-check-fill',
            'supporter': 'bi-heart-fill',
            'regular': 'bi-person'
        }
        return icons.get(self.profile_type, 'bi-person')

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')


class AddressUser(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name=_("Usuário"))
    street = EncryptedCharField(max_length=255, verbose_name=_("Rua"))
    number = EncryptedCharField(max_length=10, blank=True, verbose_name=_("Número"))
    complement = EncryptedCharField(max_length=100, blank=True, verbose_name=_("Complemento"))
    neighborhood = EncryptedCharField(max_length=100, blank=True, verbose_name=_("Bairro"))
    city = EncryptedCharField(max_length=100, verbose_name=_("Cidade"))
    state = EncryptedCharField(max_length=100, verbose_name=_("Estado"))
    postal_code = EncryptedCharField(max_length=20, verbose_name=_("CEP"))

    class Meta:
        verbose_name = _('Endereço de Usuário')
        verbose_name_plural = _('Endereços de Usuários')

    def __str__(self):
        return f'{self.street}, {self.number}, {self.complement}, {self.neighborhood}, {self.city}, {self.state}, {self.postal_code}'


class State(BaseModelAbstract):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    abbreviation = models.CharField(max_length=2, unique=True, verbose_name=_("Abreviação"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Estado')
        verbose_name_plural = _('Estados')


class City(BaseModelAbstract):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name=_("Estado"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Cidade')
        verbose_name_plural = _('Cidades')


class DashboardContent(BaseModel):
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name=_("Slug"))
    is_active = models.BooleanField(default=False, verbose_name=_("Ativo"))
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Autor"))

    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboards')

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"Dashboard {self.pk}"


class DashboardContentTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Português')),
        ('en', _('Inglês')),
        ('es', _('Espanhol')),
    ]

    dashboard = models.ForeignKey(DashboardContent, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Dashboard"))
    language = models.CharField(max_length=5, choices=LANGUAGES, verbose_name=_("Idioma"))
    title = models.CharField(max_length=200, verbose_name=_("Título"))
    content = CKEditor5Field(verbose_name=_("Conteúdo"), config_name='extends')

    class Meta:
        unique_together = ('dashboard', 'language')
        verbose_name = _('Tradução de Dashboard')
        verbose_name_plural = _('Traduções de Dashboards')

    def __str__(self):
        return f"{self.title} ({self.language})"


class SiteLogo(BaseModel):
    name = models.CharField(max_length=100, default="Logo Principal", verbose_name=_("Nome"))
    image = models.ImageField(upload_to='logos/', verbose_name=_("Imagem"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))

    def __str__(self):
        return self.name


class PerfilGamer(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("Usuário"))
    xp = models.PositiveIntegerField(default=0, verbose_name=_("XP"))
    level = models.PositiveIntegerField(default=1, verbose_name=_("Nível"))
    last_login_reward = models.DateField(null=True, blank=True, verbose_name=_("Último bônus de login"))

    def adicionar_xp(self, quantidade):
        self.xp += quantidade
        while self.xp >= self.xp_para_proximo_nivel():
            self.xp -= self.xp_para_proximo_nivel()
            self.level += 1
        self.save()

    def xp_para_proximo_nivel(self):
        return 100 + (self.level - 1) * 25

    def pode_receber_bonus_diario(self):
        return self.last_login_reward != date.today()

    def receber_bonus_diario(self):
        if self.pode_receber_bonus_diario():
            self.adicionar_xp(25)
            self.last_login_reward = date.today()
            self.save()
            return True
        return False


class Conquista(BaseModel):
    nome = models.CharField(max_length=100, verbose_name=_("Nome"))
    descricao = models.TextField(verbose_name=_("Descrição"))
    icone = models.ImageField(upload_to='conquistas/', null=True, blank=True, verbose_name=_("Ícone"))
    codigo = models.CharField(max_length=50, unique=True, verbose_name=_("Código"))

    class Meta:
        verbose_name = _('Conquista')
        verbose_name_plural = _('Conquistas')

    def __str__(self):
        return self.nome


class ConquistaUsuario(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Usuário"))
    conquista = models.ForeignKey(Conquista, on_delete=models.CASCADE, verbose_name=_("Conquista"))
    data_conquista = models.DateTimeField(auto_now_add=True, verbose_name=_("Data da Conquista"))

    class Meta:
        unique_together = ('usuario', 'conquista')
        verbose_name = _('Conquista de Usuário')
        verbose_name_plural = _('Conquistas de Usuários')
