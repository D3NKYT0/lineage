from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, UserProfile, Hashtag, Report, ModerationAction, ContentFilter, VerificationRequest
from django.contrib.auth import get_user_model
from utils.media_validators import (
    validate_social_media_image, validate_social_media_video, 
    validate_avatar_image
)


class PostForm(forms.ModelForm):
    """Formulário para criação de posts"""
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('O que você está pensando?'),
            'maxlength': 1000,
            'required': 'required'
        }),
        max_length=1000,
        help_text=_('Máximo 1000 caracteres')
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png,image/webp,image/gif'
        }),
        help_text=_('Imagem opcional (máx. 10MB, formatos: JPEG, PNG, WEBP, GIF)'),
        validators=[validate_social_media_image]
    )
    video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/mp4,video/quicktime,video/x-msvideo,video/webm'
        }),
        help_text=_('Vídeo opcional (máx. 100MB, 5min, formatos: MP4, MOV, AVI, WEBM)'),
        validators=[validate_social_media_video]
    )


    class Meta:
        model = Post
        fields = ['content', 'image', 'video', 'is_public']
        widgets = {
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or content.strip() == '':
            raise forms.ValidationError(_('O conteúdo não pode estar vazio.'))
        return content.strip()

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content', '')
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        
        # Verificar se há pelo menos um tipo de conteúdo
        if not content and not image and not video:
            raise forms.ValidationError(_('O post deve ter pelo menos um conteúdo: texto, imagem ou vídeo.'))
        
        # Não permitir imagem e vídeo ao mesmo tempo
        if image and video:
            raise forms.ValidationError(_('Não é possível anexar imagem e vídeo no mesmo post. Escolha apenas um.'))
        
        return cleaned_data






class CommentForm(forms.ModelForm):
    """Formulário para comentários"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Escreva um comentário...'),
            'maxlength': 500
        }),
        max_length=500,
        help_text=_('Máximo 500 caracteres')
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text=_('Imagem opcional no comentário')
    )

    class Meta:
        model = Comment
        fields = ['content', 'image']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or content.strip() == '':
            raise forms.ValidationError(_('O comentário não pode estar vazio.'))
        return content.strip()




class UserProfileForm(forms.ModelForm):
    """Formulário para edição do perfil social"""
    
    cover_image = forms.ImageField(
        required=False,
        help_text=_('Imagem de capa (máx. 10MB, recomendado: 1200x400px)'),
        validators=[validate_social_media_image]
    )

    class Meta:
        model = UserProfile
        fields = [
            'bio', 'cover_image', 'website', 'location',
            'birth_date', 'phone', 'gender', 'interests',
            'is_private', 'show_email', 'show_phone', 'allow_messages'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Conte um pouco sobre você...'),
                'maxlength': 500
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://seusite.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Sua cidade, país')
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Seu telefone')
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'interests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Seus hobbies e interesses...')
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_phone': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_messages': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'bio': _('Máximo 500 caracteres'),
            'avatar': _('Foto de perfil (JPG, PNG)'),
            'cover_image': _('Imagem de capa (JPG, PNG)'),
            'website': _('Link para seu site pessoal'),
            'interests': _('Conte sobre seus interesses'),
        }






class SearchForm(forms.Form):
    """Formulário de busca"""
    q = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Buscar usuários, posts...'),
            'aria-label': _('Buscar')
        }),
        label=_('Buscar'),
        required=False
    )
    search_type = forms.ChoiceField(
        choices=[
            ('all', _('Tudo')),
            ('users', _('Usuários')),
            ('posts', _('Posts')),
            ('hashtags', _('Hashtags')),
        ],
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    date_filter = forms.ChoiceField(
        choices=[
            ('all', _('Qualquer data')),
            ('today', _('Hoje')),
            ('week', _('Esta semana')),
            ('month', _('Este mês')),
            ('year', _('Este ano')),
        ],
        initial='all',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class ShareForm(forms.Form):
    """Formulário para compartilhamento de posts"""
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Adicione um comentário ao compartilhar...'),
            'maxlength': 500
        }),
        max_length=500,
        help_text=_('Comentário opcional (máx. 500 caracteres)')
    )
    is_public = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text=_('Compartilhar publicamente')
    )


class ReactionForm(forms.Form):
    """Formulário para reações em posts"""
    reaction_type = forms.ChoiceField(
        choices=[
            ('like', '👍 Curtir'),
            ('love', '❤️ Amar'),
            ('haha', '😂 Haha'),
            ('wow', '😮 Uau'),
            ('sad', '😢 Triste'),
            ('angry', '😠 Bravo'),
        ],
        initial='like',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class HashtagForm(forms.ModelForm):
    """Formulário para criação/edição de hashtags"""
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'nome_da_hashtag'
        }),
        help_text=_('Nome da hashtag (sem #)')
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Descrição da hashtag...')
        })
    )

    class Meta:
        model = Hashtag
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Remover # se presente
            name = name.strip().lstrip('#')
            # Validar formato
            if not name.replace('_', '').replace('-', '').isalnum():
                raise forms.ValidationError(_('Nome da hashtag deve conter apenas letras, números, hífens e underscores.'))
        return name


# ============================================================================
# FORMULÁRIOS DE MODERAÇÃO
# ============================================================================

class ReportForm(forms.ModelForm):
    """Formulário para criação de denúncias"""
    report_type = forms.ChoiceField(
        choices=Report.REPORT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'report-type'
        }),
        label=_('Tipo de Denúncia')
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Descreva o problema encontrado...'),
            'maxlength': 1000
        }),
        max_length=1000,
        label=_('Descrição'),
        help_text=_('Máximo 1000 caracteres')
    )

    class Meta:
        model = Report
        fields = ['report_type', 'description']
        exclude = [
            'reporter', 'status', 'reported_post', 'reported_comment',
            'reported_user', 'assigned_moderator', 'moderator_notes',
            'resolved_at', 'priority', 'similar_reports_count'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.content_type = kwargs.pop('content_type', None)
        self.content_id = kwargs.pop('content_id', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        # Verificar se o usuário já denunciou este conteúdo
        if self.user and self.content_type and self.content_id:
            # Verificar se há denúncias pendentes ou em revisão
            existing_report = Report.objects.filter(
                reporter=self.user,
                status__in=['pending', 'reviewing']
            )
            
            if self.content_type == 'post':
                existing_report = existing_report.filter(reported_post_id=self.content_id)
            elif self.content_type == 'comment':
                existing_report = existing_report.filter(reported_comment_id=self.content_id)
            elif self.content_type == 'user':
                existing_report = existing_report.filter(reported_user_id=self.content_id)
            
            if existing_report.exists():
                raise forms.ValidationError(
                    _('Você já denunciou este conteúdo. Aguarde nossa equipe analisar sua denúncia anterior.')
                )
            
            # Verificar limite de 3 denúncias globais por conteúdo
            can_report, current_count = Report.can_user_report_content(
                self.user, self.content_type, self.content_id, max_reports=3
            )
            
            if not can_report:
                raise forms.ValidationError(
                    _('Você já denunciou este conteúdo {} vezes. O limite máximo é de 3 denúncias por conteúdo.').format(current_count)
                )
        
        return cleaned_data

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or description.strip() == '':
            raise forms.ValidationError(_('A descrição é obrigatória.'))
        return description.strip()


class ModerationActionForm(forms.ModelForm):
    """Formulário para ações de moderação"""
    action_type = forms.ChoiceField(
        choices=ModerationAction.ACTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_action_type'
        }),
        label=_('Tipo de Ação')
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Justificativa para a ação...'),
            'maxlength': 500
        }),
        max_length=500,
        label=_('Motivo'),
        help_text=_('Máximo 500 caracteres')
    )

    # Campos condicionais para suspensões
    suspension_duration = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '7 (dias) ou 24:00:00 (horas:min:seg)',
            'id': 'id_suspension_duration'
        }),
        label=_('Duração da Suspensão'),
        help_text=_('Ex: 7 (para 7 dias) ou 24:00:00 (para 24 horas)')
    )
    suspension_type = forms.ChoiceField(
        choices=ModerationAction.SUSPENSION_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_suspension_type'
        }),
        label=_('Tipo de Suspensão')
    )
    
    # Campo para ações que precisam de usuário específico
    target_username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite o nome do usuário'),
            'id': 'id_target_username'
        }),
        label=_('Usuário Alvo'),
        help_text=_('Nome do usuário para aplicar a ação')
    )
    
    # Campo para prazo de suspensão específico
    custom_expiry_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'id': 'id_custom_expiry_date'
        }),
        label=_('Data de Expiração'),
        help_text=_('Data específica para expiração da ação')
    )
    
    # Campo para motivo público (visível ao usuário)
    public_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Motivo que será mostrado ao usuário'),
            'id': 'id_public_reason'
        }),
        label=_('Motivo Público'),
        help_text=_('Motivo que será exibido para o usuário afetado')
    )

    # Notificação
    notify_user = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'notify-user'
        }),
        label=_('Notificar Usuário')
    )
    notification_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Mensagem personalizada para o usuário...'),
            'maxlength': 500,
            'id': 'notification-message'
        }),
        max_length=500,
        label=_('Mensagem de Notificação'),
        help_text=_('Mensagem opcional para o usuário (máx. 500 caracteres)')
    )

    class Meta:
        model = ModerationAction
        fields = [
            'action_type', 'reason', 'suspension_duration', 'suspension_type',
            'target_username', 'custom_expiry_date', 'public_reason',
            'notify_user', 'notification_message'
        ]
        exclude = [
            'moderator', 'target_post', 'target_comment', 'target_user',
            'suspension_end_date', 'is_active', 'expires_at'
        ]

    def clean_suspension_duration(self):
        """Converte string em timedelta"""
        duration_str = self.cleaned_data.get('suspension_duration')
        if not duration_str:
            return None
            
        try:
            # Se for apenas um número, assumir dias
            if duration_str.isdigit():
                from datetime import timedelta
                return timedelta(days=int(duration_str))
            
            # Se for formato HH:MM:SS, converter
            if ':' in duration_str:
                from datetime import timedelta
                parts = duration_str.split(':')
                if len(parts) == 3:
                    hours, minutes, seconds = map(int, parts)
                    return timedelta(hours=hours, minutes=minutes, seconds=seconds)
                elif len(parts) == 2:
                    hours, minutes = map(int, parts)
                    return timedelta(hours=hours, minutes=minutes)
            
            # Tentar parsing padrão do Django
            from django.utils.dateparse import parse_duration
            parsed = parse_duration(duration_str)
            if parsed:
                return parsed
                
            raise ValueError("Formato inválido")
            
        except (ValueError, TypeError):
            raise forms.ValidationError(_('Formato inválido. Use: 7 (dias) ou 24:00:00 (horas:min:seg)'))

    def clean(self):
        cleaned_data = super().clean()
        action_type = cleaned_data.get('action_type')
        suspension_duration = cleaned_data.get('suspension_duration')
        suspension_type = cleaned_data.get('suspension_type')
        target_username = cleaned_data.get('target_username')
        public_reason = cleaned_data.get('public_reason')

        # Debug: Log dos dados limpos
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Validando formulário - action_type: {action_type}")

        # Validar campos específicos por tipo de ação
        if action_type in ['suspend_user', 'restrict_user', 'ban_user']:
            # Ações de suspensão/banimento precisam de duração e tipo
            if not suspension_duration:
                self.add_error('suspension_duration', _('Duração é obrigatória para ações de suspensão/banimento.'))
            if not suspension_type:
                self.add_error('suspension_type', _('Tipo de suspensão é obrigatório.'))
        
        # Ações que afetam usuários específicos precisam de motivo público
        if action_type in ['suspend_user', 'ban_user', 'warn']:
            if not public_reason:
                self.add_error('public_reason', _('Motivo público é obrigatório para ações que afetam usuários.'))
        
        # Validar se há conteúdo suficiente para aplicar a ação
        if action_type in ['hide_content', 'delete_content', 'approve_content', 'feature_content']:
            # Essas ações serão validadas na view pois dependem do contexto do report
            pass

        return cleaned_data


class ContentFilterForm(forms.ModelForm):
    """Formulário para filtros de conteúdo"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nome do filtro')
        }),
        label=_('Nome do Filtro')
    )
    filter_type = forms.ChoiceField(
        choices=ContentFilter.FILTER_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'filter-type'
        }),
        label=_('Tipo de Filtro')
    )
    pattern = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Padrão a ser filtrado...'),
            'id': 'filter-pattern'
        }),
        label=_('Padrão'),
        help_text=_('Palavra-chave, regex ou padrão a ser filtrado')
    )
    action = forms.ChoiceField(
        choices=ContentFilter.ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'filter-action'
        }),
        label=_('Ação')
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Descrição do filtro...')
        }),
        label=_('Descrição')
    )

    # Campos de controle
    case_sensitive = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Sensível a Maiúsculas/Minúsculas')
    )
    apply_to_posts = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Aplicar a Posts')
    )
    apply_to_comments = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Aplicar a Comentários')
    )
    apply_to_usernames = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Aplicar a Nomes de Usuário')
    )

    class Meta:
        model = ContentFilter
        fields = [
            'name', 'filter_type', 'pattern', 'action', 'description',
            'case_sensitive', 'apply_to_posts', 'apply_to_comments', 'apply_to_usernames'
        ]
        exclude = ['is_active', 'matches_count', 'last_matched']

    def clean_pattern(self):
        pattern = self.cleaned_data.get('pattern')
        filter_type = self.cleaned_data.get('filter_type')

        if not pattern or pattern.strip() == '':
            raise forms.ValidationError(_('O padrão é obrigatório.'))

        # Validar regex se for do tipo regex
        if filter_type == 'regex':
            import re
            try:
                re.compile(pattern)
            except re.error as e:
                raise forms.ValidationError(_(f'Expressão regular inválida: {e}'))

        return pattern.strip()

    def clean(self):
        cleaned_data = super().clean()
        apply_to_posts = cleaned_data.get('apply_to_posts')
        apply_to_comments = cleaned_data.get('apply_to_comments')
        apply_to_usernames = cleaned_data.get('apply_to_usernames')

        # Pelo menos um tipo de conteúdo deve ser selecionado
        if not any([apply_to_posts, apply_to_comments, apply_to_usernames]):
            raise forms.ValidationError(_('Selecione pelo menos um tipo de conteúdo para aplicar o filtro.'))

        return cleaned_data


class SearchReportForm(forms.Form):
    """Formulário para busca de denúncias"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Buscar denúncias...'),
            'autocomplete': 'off'
        }),
        label=_('Buscar')
    )
    report_type = forms.ChoiceField(
        choices=[('', _('Todos os tipos'))] + Report.REPORT_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Tipo de Denúncia')
    )
    status = forms.ChoiceField(
        choices=[('', _('Todos os status'))] + Report.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Status')
    )
    priority = forms.ChoiceField(
        choices=[
            ('', _('Todas as prioridades')),
            ('low', _('Baixa')),
            ('medium', _('Média')),
            ('high', _('Alta')),
            ('urgent', _('Urgente')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Prioridade')
    )
    assigned_moderator = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(is_staff=True),
        required=False,
        empty_label=_('Todos os moderadores'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Moderador Responsável')
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label=_('Data Inicial')
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label=_('Data Final')
    )


class BulkModerationForm(forms.Form):
    """Formulário para ações em massa de moderação"""
    action_type = forms.ChoiceField(
        choices=[
            ('', _('Selecione uma ação')),
            ('hide_content', _('Ocultar Conteúdo')),
            ('delete_content', _('Deletar Conteúdo')),
            ('warn', _('Enviar Advertência')),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'bulk-action-type'
        }),
        label=_('Ação em Massa')
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Motivo para a ação em massa...'),
            'maxlength': 500
        }),
        max_length=500,
        label=_('Motivo'),
        help_text=_('Motivo opcional para a ação (máx. 500 caracteres)')
    )
    assigned_moderator = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(is_staff=True),
        required=False,
        empty_label=_('Selecione um moderador'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label=_('Atribuir a Moderador')
    )

    def clean(self):
        cleaned_data = super().clean()
        # Validações podem ser adicionadas aqui conforme necessário
        return cleaned_data


class VerificationRequestForm(forms.ModelForm):
    """Formulário para solicitação de verificação de conta"""
    
    # Campos com validação adicional
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'data-mask': '000.000.000-00'
        }),
        help_text=_('Digite seu CPF válido')
    )
    
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000',
            'data-mask': '(00) 00000-0000'
        }),
        help_text=_('Digite seu número de telefone')
    )
    
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text=_('Selecione sua data de nascimento')
    )
    
    identity_document = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text=_('Envie uma foto do seu RG, CNH ou outro documento oficial com foto (máx. 5MB)')
    )
    
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Explique por que você deseja ter sua conta verificada...')
        }),
        max_length=1000,
        help_text=_('Máximo 1000 caracteres')
    )
    
    class Meta:
        model = VerificationRequest
        fields = [
            'cpf', 'full_name', 'birth_date', 'phone_number',
            'identity_document', 'reason'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nome completo como aparece no documento')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Se o usuário já tem CPF, pré-preencher
        if self.user and self.user.cpf:
            self.fields['cpf'].initial = self.user.cpf
            self.fields['cpf'].widget.attrs['readonly'] = 'readonly'
            self.fields['cpf'].help_text = _('CPF já cadastrado e não pode ser alterado')
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            from .utils import validate_cpf, remove_cpf_mask
            cpf_clean = remove_cpf_mask(cpf)
            
            if not validate_cpf(cpf_clean):
                raise forms.ValidationError(_('CPF inválido. Verifique os números digitados.'))
            
            return cpf_clean
        return cpf
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            from .utils import validate_phone_number, remove_cpf_mask
            phone_clean = remove_cpf_mask(phone)  # Reutilizando a função para remover máscara
            
            if not validate_phone_number(phone_clean):
                raise forms.ValidationError(_('Número de telefone inválido. Verifique o DDD e o número.'))
            
            return phone_clean
        return phone
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            from datetime import date
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 18:
                raise forms.ValidationError(_('Você deve ter pelo menos 18 anos para solicitar verificação.'))
            
            if age > 120:
                raise forms.ValidationError(_('Data de nascimento inválida.'))
        
        return birth_date
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Verificar se o usuário atende aos requisitos
        if self.user:
            from .utils import can_request_verification
            
            if not can_request_verification(self.user):
                raise forms.ValidationError(_('Você não atende aos requisitos para solicitar verificação. Verifique se: e-mail está verificado, 2FA está habilitado, conta tem pelo menos 30 dias e você tem pelo menos 10 posts.'))
        
        return cleaned_data


class VerificationRequestAdminForm(forms.ModelForm):
    """Formulário administrativo para revisão de solicitações"""
    
    class Meta:
        model = VerificationRequest
        fields = ['status', 'rejection_reason', 'admin_notes']
        widgets = {
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Observações internas sobre a solicitação...')
            }),
            'rejection_reason': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        # Se foi rejeitada, deve ter motivo
        if status == 'rejected' and not rejection_reason:
            raise forms.ValidationError(_('É necessário informar o motivo da rejeição.'))
        
        # Se foi aprovada, não deve ter motivo de rejeição
        if status == 'approved' and rejection_reason:
            cleaned_data['rejection_reason'] = None
        
        return cleaned_data
