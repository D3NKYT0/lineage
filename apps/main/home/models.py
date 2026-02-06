from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
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

    def ensure_email_master_owner(self):
        """Garante que exista um dono registrado para este e-mail e retorna o owner."""
        if not self.email:
            return None

        with transaction.atomic():
            ownership, _ = EmailOwnership.objects.select_for_update().get_or_create(
                email=self.email,
                defaults={'owner': self}
            )
        return ownership.owner

    def get_email_master_owner(self):
        """Retorna o usuário dono do e-mail (ou None se não houver)."""
        if not self.email:
            return None

        ownership = EmailOwnership.objects.filter(email=self.email).select_related('owner').first()
        return ownership.owner if ownership else None

    @property
    def is_email_master_owner(self):
        owner = self.get_email_master_owner()
        return (owner is None) or (owner.pk == self.pk)

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')


class EmailOwnership(BaseModel):
    email = models.EmailField(unique=True, verbose_name=_("E-mail"))
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_emails', verbose_name=_("Conta Mestre"))

    class Meta:
        verbose_name = _("Domínio de E-mail")
        verbose_name_plural = _("Domínios de E-mail")

    def __str__(self):
        return f"{self.email} → {self.owner.username}"


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
    # Chaves = tipos de evento (ex: convite_amizade, admin_doacoes_compras). Valor False = usuário desativou.
    push_preferences = models.JSONField(default=dict, blank=True, verbose_name=_("Preferências de push"))

    def adicionar_xp(self, quantidade):
        self.xp += quantidade
        while self.xp >= self.xp_para_proximo_nivel():
            self.xp -= self.xp_para_proximo_nivel()
            self.level += 1
        self.save()

    def xp_para_proximo_nivel(self):
        return 100 + (self.level - 1) * 25

    def get_patent_level(self):
        """Retorna o nível da patente (limitado a 30)"""
        return min(self.level, 30)

    def pode_receber_bonus_diario(self):
        return self.last_login_reward != date.today()

    def receber_bonus_diario(self):
        if self.pode_receber_bonus_diario():
            self.adicionar_xp(25)
            self.last_login_reward = date.today()
            self.save()
            return True
        return False

    def __str__(self):
        return f"Perfil Gamer de {self.user.username} - Nível {self.level}"


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

    def __str__(self):
        return f"{self.usuario.username} - {self.conquista.nome}"


class PageView(BaseModel):
    """Modelo para rastrear visualizações de páginas pelos usuários"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='page_views',
        verbose_name=_("Usuário"),
        null=True,
        blank=True
    )
    url_path = models.CharField(max_length=500, verbose_name=_("Caminho da URL"))
    url_name = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Nome da URL"))
    view_name = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Nome da View"))
    page_category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Categoria da Página"),
        help_text=_("Categoria da página (ex: tops, heroes, social, etc)")
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Endereço IP"))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_("User Agent"))
    
    class Meta:
        verbose_name = _("Visualização de Página")
        verbose_name_plural = _("Visualizações de Páginas")
        indexes = [
            models.Index(fields=['user', 'url_path', '-created_at']),
            models.Index(fields=['page_category', '-created_at']),
            models.Index(fields=['url_path', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.url_path}"
        return f"Anônimo - {self.url_path}"


class Banner(BaseModel):
    """Modelo para gerenciar banners no index do site"""
    
    POSITION_CHOICES = [
        ('top', _('Topo')),
        ('middle', _('Meio')),
        ('bottom', _('Rodapé')),
    ]
    
    HORIZONTAL_ALIGN_CHOICES = [
        ('left', _('Esquerda')),
        ('center', _('Centro')),
        ('right', _('Direita')),
    ]
    
    SIZE_CHOICES = [
        ('small', _('Pequeno (300x100)')),
        ('medium', _('Médio (600x200)')),
        ('large', _('Grande (1200x400)')),
        ('full-width', _('Largura Total (100%)')),
        ('custom', _('Personalizado')),
    ]
    
    DISPLAY_TYPE_CHOICES = [
        ('normal', _('Normal (na página)')),
        ('popup', _('Pop-up (modal)')),
    ]
    
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Título"))
    image = models.ImageField(upload_to='banners/', verbose_name=_("Imagem"))
    link = models.URLField(blank=True, null=True, verbose_name=_("Link (opcional)"), help_text=_("URL para onde o banner redireciona ao ser clicado"))
    
    # Tipo de exibição
    display_type = models.CharField(
        max_length=20,
        choices=DISPLAY_TYPE_CHOICES,
        default='normal',
        verbose_name=_("Tipo de Exibição"),
        help_text=_("Escolha se o banner aparece na página ou como pop-up")
    )
    
    # Posicionamento
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='middle',
        verbose_name=_("Posição Vertical"),
        help_text=_("Onde o banner será exibido na página")
    )
    horizontal_align = models.CharField(
        max_length=20,
        choices=HORIZONTAL_ALIGN_CHOICES,
        default='center',
        verbose_name=_("Alinhamento Horizontal")
    )
    
    # Tamanho
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        default='medium',
        verbose_name=_("Tamanho")
    )
    custom_width = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Largura Personalizada (px)"),
        help_text=_("Apenas se tamanho for 'Personalizado'")
    )
    custom_height = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Altura Personalizada (px)"),
        help_text=_("Apenas se tamanho for 'Personalizado'")
    )
    
    # Controle de exibição
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordem de Exibição"),
        help_text=_("Banners com menor número aparecem primeiro")
    )
    
    # Configurações de Pop-up
    popup_width = models.PositiveIntegerField(
        default=600,
        verbose_name=_("Largura do Pop-up (px)"),
        help_text=_("Apenas para banners tipo Pop-up")
    )
    popup_height = models.PositiveIntegerField(
        default=400,
        verbose_name=_("Altura do Pop-up (px)"),
        help_text=_("Apenas para banners tipo Pop-up")
    )
    popup_close_button = models.BooleanField(
        default=True,
        verbose_name=_("Mostrar Botão de Fechar"),
        help_text=_("Exibe um botão X para fechar o pop-up")
    )
    popup_auto_close = models.BooleanField(
        default=False,
        verbose_name=_("Fechar Automaticamente"),
        help_text=_("Fecha o pop-up automaticamente após um tempo")
    )
    popup_auto_close_delay = models.PositiveIntegerField(
        default=5,
        verbose_name=_("Tempo para Fechar (segundos)"),
        help_text=_("Tempo em segundos antes de fechar automaticamente")
    )
    popup_show_once_per_session = models.BooleanField(
        default=True,
        verbose_name=_("Mostrar Apenas Uma Vez por Sessão"),
        help_text=_("✓ Marcado: Pop-up aparece apenas 1 vez por sessão (até fechar o navegador). Desmarcado: Pop-up aparece a cada carregamento da página.")
    )
    
    # Datas opcionais
    start_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Data de Início"),
        help_text=_("Data a partir da qual o banner será exibido (opcional)")
    )
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Data de Término"),
        help_text=_("Data até quando o banner será exibido (opcional)")
    )
    
    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['display_order', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'position', 'display_order']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return self.title or f"Banner #{self.pk}"
    
    def is_visible(self):
        """Verifica se o banner deve ser exibido baseado em datas e status ativo"""
        if not self.is_active:
            return False
        
        from django.utils import timezone
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_size_style(self):
        """Retorna o estilo CSS para o tamanho do banner"""
        if self.size == 'custom' and self.custom_width and self.custom_height:
            return f"width: {self.custom_width}px; height: {self.custom_height}px;"
        
        size_map = {
            'small': 'width: 300px; height: 100px;',
            'medium': 'width: 600px; height: 200px;',
            'large': 'width: 1200px; height: 400px;',
            'full-width': 'width: 100%; height: auto;',
        }
        return size_map.get(self.size, size_map['medium'])
    
    def get_position_style(self):
        """Retorna o estilo CSS para posicionamento"""
        styles = []
        
        # Alinhamento horizontal
        if self.horizontal_align == 'left':
            styles.append('margin-left: 0; margin-right: auto;')
        elif self.horizontal_align == 'right':
            styles.append('margin-left: auto; margin-right: 0;')
        else:  # center
            styles.append('margin-left: auto; margin-right: auto;')
        
        return ' '.join(styles)
    
    def get_popup_size_style(self):
        """Retorna o estilo CSS para o tamanho do pop-up"""
        return f"width: {self.popup_width}px; height: {self.popup_height}px; max-width: 90vw; max-height: 90vh;"