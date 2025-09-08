from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import *
from core.admin import BaseModelAdmin, BaseModelAdminAbstratic, BaseInlineAdmin
from .forms import DashboardContentForm, DashboardContentTranslationForm, CustomUserChangeForm, CustomUserCreationForm


@admin.register(User)
class UserAdmin(BaseModelAdmin, DefaultUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = (
        'username', 'email', 'display_groups', 'cpf', 'gender', 'fichas',
        'is_email_verified', 'is_2fa_enabled', 'is_verified_account', 'social_verified',
        'is_superadmin', 'is_staff_member', 'is_moderator', 'is_verified_user', 'is_apoiador', 'created_at', 'updated_at'
    )
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by', 'uuid')
    
    list_filter = (
        'is_email_verified', 'is_2fa_enabled', 'is_verified_account', 'social_verified',
        'is_superadmin', 'is_staff_member', 'is_moderator', 'is_verified_user', 'is_apoiador',
        'is_active', 'is_staff', 'is_superuser', 'gender', 'created_at', 'groups'
    )
    
    search_fields = (
        'username', 'email', 'first_name', 'last_name', 'cpf'
    )
    
    ordering = ('-created_at', 'username')
    
    fieldsets = (
        (_('Informações de Acesso'), {
            'fields': ('username', 'password', 'uuid'),
            'description': _('Credenciais de acesso do usuário')
        }),
        (_('Informações Pessoais'), {
            'fields': ('email', 'avatar', 'bio', 'cpf', 'gender', 'first_name', 'last_name'),
            'description': _('Dados pessoais e de contato')
        }),
        (_('Verificação e Segurança'), {
            'fields': ('is_email_verified', 'is_2fa_enabled', 'is_verified_account', 'social_verified'),
            'description': _('Status de verificação e configurações de segurança')
        }),
        (_('Tipos de Perfil'), {
            'fields': ('is_superadmin', 'is_staff_member', 'is_moderator', 'is_verified_user', 'is_apoiador'),
            'description': _('Defina o tipo de perfil do usuário para diferenciação visual')
        }),
        (_('Permissões do Sistema'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': _('Controle de acesso e permissões do Django')
        }),
        (_('Datas e Metadados'), {
            'fields': ('last_login', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
            'description': _('Informações de auditoria e controle')
        }),
    )

    add_fieldsets = (
        (_('Informações Básicas'), {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'avatar', 'bio', 'cpf', 'gender',
            ),
        }),
        (_('Configurações de Verificação'), {
            'fields': (
                'is_email_verified', 'is_2fa_enabled', 'is_verified_account', 'social_verified',
            ),
        }),
        (_('Tipos de Perfil'), {
            'fields': (
                'is_superadmin', 'is_staff_member', 'is_moderator', 'is_verified_user', 'is_apoiador'
            ),
        }),
    )

    actions = ['verify_email_users', 'enable_2fa_users', 'mark_as_verified', 'deactivate_users']

    def display_groups(self, obj):
        groups = obj.groups.all()
        if groups:
            return format_html(
                '<span style="background: #e3f2fd; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                ", ".join([group.name for group in groups])
            )
        return _('Sem grupos')
    display_groups.short_description = _("Grupos")

    def verify_email_users(self, request, queryset):
        updated = queryset.update(is_email_verified=True)
        self.message_user(request, _('{} usuários tiveram o email verificado.').format(updated))
    verify_email_users.short_description = _('Verificar email dos usuários selecionados')

    def enable_2fa_users(self, request, queryset):
        updated = queryset.update(is_2fa_enabled=True)
        self.message_user(request, _('{} usuários tiveram 2FA habilitado.').format(updated))
    enable_2fa_users.short_description = _('Habilitar 2FA para usuários selecionados')

    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified_account=True)
        self.message_user(request, _('{} usuários foram marcados como verificados.').format(updated))
    mark_as_verified.short_description = _('Marcar usuários como verificados')

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _('{} usuários foram desativados.').format(updated))
    deactivate_users.short_description = _('Desativar usuários selecionados')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        js = ('js/mask-cpf.js',)


@admin.register(AddressUser)
class AddressAdmin(BaseModelAdmin):
    list_display = ('user', 'street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code')
    search_fields = ('user__username', 'street', 'city', 'state', 'postal_code', 'neighborhood')
    list_filter = ('state', 'neighborhood', 'city')
    ordering = ('user__username', 'state', 'city')

    fieldsets = (
        (_('Usuário'), {
            'fields': ('user',)
        }),
        (_('Endereço'), {
            'fields': ('street', 'number', 'complement', 'neighborhood')
        }),
        (_('Localização'), {
            'fields': ('city', 'state', 'postal_code')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
    

@admin.register(State)
class StateAdmin(BaseModelAdminAbstratic):
    list_display = ('name', 'abbreviation')
    search_fields = ('name', 'abbreviation')
    ordering = ('name',)
    list_filter = ('abbreviation',)
    
    fieldsets = (
        (_('Informações do Estado'), {
            'fields': ('name', 'abbreviation')
        }),
    )


@admin.register(City)
class CityAdmin(BaseModelAdminAbstratic):
    list_display = ('name', 'state')
    search_fields = ('name', 'state__name', 'state__abbreviation')
    ordering = ('state__name', 'name')
    list_filter = ('state',)
    
    fieldsets = (
        (_('Informações da Cidade'), {
            'fields': ('name', 'state')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('state')


class DashboardContentTranslationInline(BaseInlineAdmin):
    model = DashboardContentTranslation
    form = DashboardContentTranslationForm
    fields = ['language', 'title', 'content']
    verbose_name = _('Tradução')
    verbose_name_plural = _('Traduções')
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['language'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width: 200px;'
        })
        formset.form.base_fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Título da tradução')
        })
        return formset

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.dashboard = form.instance
            instance.save()
        formset.save_m2m()


@admin.register(DashboardContent)
class DashboardContentAdmin(BaseModelAdmin):
    form = DashboardContentForm
    inlines = [DashboardContentTranslationInline]

    list_display = ('get_title', 'slug', 'is_active', 'author', 'created_at')
    list_filter = ('is_active', 'created_at', 'author')
    search_fields = ('slug', 'translations__title', 'translations__content', 'author__username')
    ordering = ('-created_at',)
    exclude = ('author',)

    fieldsets = (
        (_('Configurações Básicas'), {
            'fields': ('slug', 'is_active'),
            'description': _('Configurações básicas do dashboard')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change or not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_title(self, obj):
        pt_translation = obj.translations.filter(language='pt').first()
        if pt_translation:
            return pt_translation.title
        first_translation = obj.translations.first()
        if first_translation:
            return format_html(
                '<span style="color: #666;">[{}] {}</span>',
                first_translation.language.upper(),
                first_translation.title
            )
        return _('Sem tradução')
    get_title.short_description = _('Título')
    get_title.admin_order_field = 'translations__title'

    actions = ['activate_dashboards', 'deactivate_dashboards']

    def activate_dashboards(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _('{} dashboards foram ativados.').format(updated))
    activate_dashboards.short_description = _('Ativar dashboards selecionados')

    def deactivate_dashboards(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _('{} dashboards foram desativados.').format(updated))
    deactivate_dashboards.short_description = _('Desativar dashboards selecionados')


@admin.register(SiteLogo)
class SiteLogoAdmin(BaseModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Informações do Logo'), {
            'fields': ('name', 'is_active')
        }),
    )


@admin.register(Conquista)
class ConquistaAdmin(BaseModelAdmin):
    list_display = ('nome', 'codigo', 'descricao', 'created_at')
    search_fields = ('nome', 'codigo', 'descricao')
    list_filter = ('codigo', 'created_at')
    readonly_fields = ('codigo',)
    ordering = ('nome',)
    
    fieldsets = (
        (_('Informações da Conquista'), {
            'fields': ('nome', 'codigo', 'descricao')
        }),
    )


@admin.register(ConquistaUsuario)
class ConquistaUsuarioAdmin(BaseModelAdmin):
    list_display = ('usuario', 'conquista', 'data_conquista')
    search_fields = ('usuario__username', 'conquista__nome')
    list_filter = ('conquista', 'data_conquista')
    ordering = ('-data_conquista',)
    readonly_fields = ('data_conquista',)
    
    fieldsets = (
        (_('Usuário e Conquista'), {
            'fields': ('usuario', 'conquista')
        }),
        (_('Informações da Conquista'), {
            'fields': ('data_conquista',),
            'description': _('Data automaticamente definida quando a conquista é atribuída'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PerfilGamer)
class PerfilGamerAdmin(BaseModelAdmin):
    list_display = ('user', 'level', 'xp', 'last_login_reward', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('level', 'last_login_reward', 'created_at')
    readonly_fields = ('xp', 'level', 'last_login_reward')
    ordering = ('-level', '-xp')
    
    fieldsets = (
        (_('Usuário'), {
            'fields': ('user',)
        }),
        (_('Progresso'), {
            'fields': ('level', 'xp', 'last_login_reward'),
            'description': _('Informações de progresso do jogador')
        }),
    )
