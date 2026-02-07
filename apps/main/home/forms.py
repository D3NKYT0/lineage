from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from .models import *
from apps.lineage.server.models import ComingSoonConfig
from apps.main.home.tasks import send_email_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'cpf', 'gender', 'website')
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
            'bio': _('Biography'),
            'cpf': _('CPF'),
            'gender': _('Gender'),
            'website': _('Website'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['first_name', 'last_name', 'email', 'bio', 'gender', 'website']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})
        self.fields['cpf'].widget.attrs.update({'class': 'form-control', 'id': 'cpf'})
        self.fields['website'].widget.attrs.update({'placeholder': 'https://seusite.com'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Não validamos mais a unicidade do email, pois permitimos múltiplos usuários
        # com o mesmo email (sistema de conta mestre)
        return email


class AvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
        labels = {
            'avatar': _('Profile Picture'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control-file'})


class AddressUserForm(forms.ModelForm):
    class Meta:
        model = AddressUser
        fields = ['street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code']
        labels = {
            'street': _('Street'),
            'number': _('Number'),
            'complement': _('Complement'),
            'neighborhood': _('Neighborhood'),
            'city': _('City'),
            'state': _('State'),
            'postal_code': _('Postal Code'),
        }
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'complement': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username')})
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('example@company.com')})
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Password')})
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm Password')})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Your Username"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Username")})
    )
    password = forms.CharField(
        label=_("Your Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Password")}),
    )
    captcha_token = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=_("Captcha")
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Adiciona campo de captcha se necessário
        if self.request:
            from middlewares.login_attempts import LoginAttemptsMiddleware
            requires_captcha = LoginAttemptsMiddleware.requires_captcha(self.request)
            if requires_captcha:
                self.fields['captcha_token'].required = True
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[LoginForm] Captcha configurado como obrigatório")
    
    def clean(self):
        """Validação customizada do formulário"""
        # Validação básica dos campos (sem autenticação)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Se o captcha é necessário, verifica se foi fornecido
            if self.request:
                from middlewares.login_attempts import LoginAttemptsMiddleware
                requires_captcha = LoginAttemptsMiddleware.requires_captcha(self.request)
                
                if requires_captcha:
                    captcha_token = self.cleaned_data.get('captcha_token')
                    if not captcha_token:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"[LoginForm] Captcha é obrigatório mas não foi fornecido")
                        raise forms.ValidationError(_("Verificação do captcha é obrigatória após múltiplas tentativas."))
                    
                    # Valida o captcha
                    from utils.hcaptcha import verify_hcaptcha
                    import logging
                    
                    logger = logging.getLogger(__name__)
                    
                    captcha_valid = verify_hcaptcha(captcha_token)
                    
                    if not captcha_valid:
                        logger.warning(f"[LoginForm] Captcha falhou na validação")
                        raise forms.ValidationError(_("Verificação do captcha falhou. Tente novamente."))
            
            # Agora vamos fazer nossa própria autenticação para tratar usuários suspensos
            from django.contrib.auth import authenticate, get_user_model
            User = get_user_model()
            
            # Tenta autenticar usando nossos backends
            user = authenticate(self.request, username=username, password=password)
            
            if not user:
                # Verifica se o usuário existe mas está inativo
                try:
                    inactive_user = User.objects.get(username=username)
                    
                    if not inactive_user.is_active:
                        # Se o usuário está inativo, não invalida o formulário
                        # Deixa a view tratar a suspensão
                        print(f"🔍 [LoginForm] Usuário {username} está inativo - permitindo que a view trate")
                        return self.cleaned_data
                except User.DoesNotExist:
                    # Usuário não existe, credenciais inválidas
                    pass
            
            # Se chegou aqui, o usuário foi autenticado com sucesso
            # Verifica se está inativo (pode ter sido autenticado mas estar suspenso)
            elif not user.is_active or hasattr(user, '_is_inactive_for_suspension'):
                # Se o usuário está inativo, não invalida o formulário
                # Deixa a view tratar a suspensão
                print(f"🔍 [LoginForm] Usuário {user.username} autenticado mas está inativo - permitindo que a view trate")
                return self.cleaned_data
        
        return self.cleaned_data


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email')
        })
    )


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        max_length=50,
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('New Password')
        })
    )
    new_password2 = forms.CharField(
        max_length=50,
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm New Password')
        })
    )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        max_length=50,
        label=_("Old Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Old Password')
        })
    )
    new_password1 = forms.CharField(
        max_length=50,
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('New Password')
        })
    )
    new_password2 = forms.CharField(
        max_length=50,
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm New Password')
        })
    )


class DashboardContentForm(forms.ModelForm):
    class Meta:
        model = DashboardContent
        fields = ['slug', 'is_active']
        labels = {
            'slug': _('Slug'),
            'is_active': _('Active'),
        }
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DashboardContentTranslationForm(forms.ModelForm):
    class Meta:
        model = DashboardContentTranslation
        fields = ['language', 'title', 'content']
        labels = {
            'language': _('Language'),
            'title': _('Title'),
            'content': _('Content'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name="extends"),
        }

    def __init__(self, *args, **kwargs):
        language = kwargs.pop('language', None)
        super().__init__(*args, **kwargs)
        if language:
            self.fields['language'].initial = language


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'is_active': _('Active'),
            'is_staff': _('Staff Status'),
            'is_superuser': _('Superuser Status'),
            'groups': _('Groups'),
            'user_permissions': _('User Permissions'),
            'password': _('Password'),
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password1', 'password2',
            'avatar', 'bio', 'cpf', 'gender', 'website',
            'is_email_verified', 'is_2fa_enabled', 'fichas',
        )
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'password1': _('Password'),
            'password2': _('Confirm Password'),
            'avatar': _('Profile Picture'),
            'bio': _('Biography'),
            'cpf': _('CPF'),
            'gender': _('Gender'),
            'website': _('Website'),
            'is_email_verified': _('Email Verified'),
            'is_2fa_enabled': _('2FA Enabled'),
            'fichas': _('Credits'),
        }


class ComingSoonConfigForm(forms.ModelForm):
    """Formulário para editar Coming Soon na Central de Configurações."""
    class Meta:
        model = ComingSoonConfig
        fields = (
            'is_active', 'staff_only_login',
            'title', 'subtitle', 'countdown_date',
            'background_image', 'overlay_opacity',
            'primary_color', 'secondary_color',
            'show_seconds',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Em Breve')}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Algo incrível está por vir. Fique ligado!')}),
            'countdown_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'overlay_opacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 1, 'step': 0.1}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'style': 'height: 42px; cursor: pointer;'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'style': 'height: 42px; cursor: pointer;'}),
        }
        labels = {
            'is_active': _('Ativar Coming Soon na página inicial'),
            'staff_only_login': _('Apenas staff pode fazer login (quando ativo)'),
            'title': _('Título principal'),
            'subtitle': _('Subtítulo'),
            'countdown_date': _('Data e hora da contagem regressiva'),
            'background_image': _('Imagem de fundo'),
            'overlay_opacity': _('Opacidade do overlay (0–1)'),
            'primary_color': _('Cor primária'),
            'secondary_color': _('Cor secundária'),
            'show_seconds': _('Mostrar segundos na contagem'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['countdown_date'].input_formats = [
            '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M'
        ]
