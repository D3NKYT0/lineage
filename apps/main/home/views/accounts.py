import requests, logging

from ..models import *
from ..forms import *
from ..utils import resolve_templated_path

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.utils.translation import gettext as _
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from utils.notifications import send_notification
from utils.dynamic_import import get_query_class
from apps.main.home.tasks import send_email_task

LineageStats = get_query_class("LineageStats")
logger = logging.getLogger(__name__)


from utils.hcaptcha import verify_hcaptcha


def verificar_hcaptcha(token):
    """
    Wrapper function for hCaptcha verification.
    Maintains backward compatibility with existing code.
    """
    return verify_hcaptcha(token)


def logout_view(request):
  logout(request)
  return redirect('/')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        hcaptcha_token = request.POST.get('h-captcha-response')
        hcaptcha_ok = verificar_hcaptcha(hcaptcha_token)

        # Verifica termos + captcha + formulário
        if not request.POST.get('terms'):
            form.add_error(None, 'Você precisa aceitar os termos e condições para se registrar.')

        elif not hcaptcha_ok:
            form.add_error(None, 'Verificação do hCaptcha falhou. Tente novamente.')

        elif form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verificar_email', args=[uid, token])
            )

            try:
                send_email_task.delay(
                    'Verifique seu e-mail',
                    f'Olá {user.username}, clique no link para verificar sua conta: {verification_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
            except Exception as e:
                logger.error(f"Erro ao enviar email: {str(e)}")

            try:
                send_notification(
                    user=None,
                    notification_type='staff',
                    message=f'Usuário {user.username} de email {user.email} cadastrado com sucesso!',
                    created_by=None
                )
            except Exception as e:
                logger.error(f"Erro ao criar notificação: {str(e)}")

            return redirect('registration_success')
        else:
            print(_("Registration failed!"))
    else:
        form = RegistrationForm()

    context = {'form': form, 'hcaptcha_site_key': settings.HCAPTCHA_SITE_KEY}
    return render(request, 'accounts_custom/sign-up.html', context)


class UserLoginView(LoginView):
    form_class = LoginForm

    def get_template_names(self):
        # Aqui você retorna o caminho do template com base no tema ativo
        return [resolve_templated_path(self.request, 'accounts_custom', 'sign-in.html')]
    
    def get_form_kwargs(self):
        """Adiciona o request ao formulário para verificar captcha"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Adiciona informações do captcha ao contexto"""
        context = super().get_context_data(**kwargs)
        
        # Verifica se o captcha é necessário
        from middlewares.login_attempts import LoginAttemptsMiddleware
        requires_captcha = LoginAttemptsMiddleware.requires_captcha(self.request)
        
        if requires_captcha:
            context['hcaptcha_site_key'] = settings.HCAPTCHA_SITE_KEY
            context['requires_captcha'] = True
            context['login_attempts'] = LoginAttemptsMiddleware.get_login_attempts(self.request)
            context['max_attempts'] = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 3)
        
        return context

    def form_valid(self, form):
        """
        Processa o login usando o sistema padrão do Django
        O LicenseBackend será executado automaticamente primeiro
        """
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        logger.info(f"[UserLoginView] Tentativa de login para usuário: {username}")
        logger.info(f"[UserLoginView] Dados do formulário: {list(form.cleaned_data.keys())}")
        logger.info(f"[UserLoginView] Dados POST: {list(self.request.POST.keys())}")
        
        # Log para debug do captcha
        from middlewares.login_attempts import LoginAttemptsMiddleware
        requires_captcha = LoginAttemptsMiddleware.requires_captcha(self.request)
        if requires_captcha:
            captcha_token = form.cleaned_data.get('captcha_token')
            logger.info(f"[UserLoginView] Captcha necessário. Token recebido: {captcha_token[:10] if captcha_token else 'None'}...")
        
        # Primeiro, tenta autenticar o usuário para verificar se é superusuário
        from django.contrib.auth import authenticate
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = authenticate(username=username, password=password)
        
        if not user:
            logger.warning(f"[UserLoginView] Falha na autenticação para usuário: {username}")
            
            # Verifica se a falha foi devido à licença inválida
            from utils.license_manager import check_license_status
            if not check_license_status():
                logger.warning(f"[UserLoginView] Login bloqueado devido à licença inválida para usuário: {username}")
                
                # Como não conseguimos autenticar, não sabemos se é superusuário
                # Vamos redirecionar para manutenção por padrão
                return redirect('maintenance')
            
            # Verifica se o usuário existe mas está inativo
            try:
                inactive_user = User.objects.get(username=username)
                logger.info(f"[UserLoginView] Usuário {username} encontrado: is_active={inactive_user.is_active}")
                
                if not inactive_user.is_active:
                    logger.warning(f"[UserLoginView] Usuário {username} existe mas está inativo")
                    
                    # Obtém informações sobre a suspensão
                    suspension_info = get_user_suspension_info(inactive_user)
                    
                    if suspension_info:
                        # Cria uma mensagem detalhada sobre a suspensão
                        if suspension_info['is_permanent']:
                            message = f"🔴 {suspension_info['message']}\n\n"
                            message += f"📋 Motivo: {suspension_info['public_reason']}\n"
                            message += f"👤 Moderador: {suspension_info['moderator']}\n"
                            message += f"📅 Data: {suspension_info['created_at']}\n\n"
                            message += f"ℹ️ Esta ação é permanente. Entre em contato com o suporte se acredita que isso foi um erro."
                        else:
                            message = f"🟡 {suspension_info['message']}\n\n"
                            message += f"📋 Motivo: {suspension_info['public_reason']}\n"
                            message += f"👤 Moderador: {suspension_info['moderator']}\n"
                            message += f"📅 Suspenso em: {suspension_info['created_at']}\n"
                            
                            if suspension_info['is_expired']:
                                message += f"✅ Status: Suspensão expirada\n\n"
                                message += f"ℹ️ Sua suspensão já expirou, mas sua conta ainda não foi reativada automaticamente. Entre em contato com o suporte."
                            elif suspension_info['end_date']:
                                message += f"⏰ Válida até: {suspension_info['end_date']}\n\n"
                                message += f"ℹ️ Sua conta será reativada automaticamente após esta data."
                            else:
                                message += f"ℹ️ Entre em contato com o suporte para mais informações."
                        
                        # Adiciona a mensagem de erro ao formulário
                        form.add_error(None, message)
                        return self.form_invalid(form)
                    else:
                        # Fallback para usuários inativos sem registro de suspensão
                        form.add_error(None, _("Sua conta foi desativada. Entre em contato com o suporte para mais informações."))
                        return self.form_invalid(form)
            except User.DoesNotExist:
                # Usuário não existe, credenciais inválidas
                pass
            
            form.add_error(None, _("Credenciais inválidas. Tente novamente."))
            return self.form_invalid(form)
        
        # Se chegou aqui, o usuário foi autenticado com sucesso
        logger.info(f"[UserLoginView] Usuário autenticado com sucesso: {user.username} (is_superuser: {user.is_superuser})")
        
        # Verifica se o usuário está ativo (pode ter sido autenticado mas estar suspenso)
        if not user.is_active or hasattr(user, '_is_inactive_for_suspension'):
            logger.warning(f"[UserLoginView] Usuário {user.username} autenticado mas está inativo - verificando motivo")
            
            # Obtém informações sobre a suspensão
            suspension_info = get_user_suspension_info(user)
            
            if suspension_info:
                # Cria uma mensagem detalhada sobre a suspensão
                if suspension_info['is_permanent']:
                    message = f"🔴 {suspension_info['message']}\n\n"
                    message += f"📋 **Motivo:** {suspension_info['public_reason']}\n"
                    message += f"👤 **Moderador:** {suspension_info['moderator']}\n"
                    message += f"📅 **Data:** {suspension_info['created_at']}\n\n"
                    message += f"ℹ️ Esta ação é permanente. Entre em contato com o suporte se acredita que isso foi um erro."
                else:
                    message = f"🟡 {suspension_info['message']}\n\n"
                    message += f"📋 **Motivo:** {suspension_info['public_reason']}\n"
                    message += f"👤 **Moderador:** {suspension_info['moderator']}\n"
                    message += f"📅 **Suspenso em:** {suspension_info['created_at']}\n"
                    
                    if suspension_info['is_expired']:
                        message += f"✅ **Status:** Suspensão expirada\n\n"
                        message += f"ℹ️ Sua suspensão já expirou, mas sua conta ainda não foi reativada automaticamente. Entre em contato com o suporte."
                    elif suspension_info['end_date']:
                        message += f"⏰ **Válida até:** {suspension_info['end_date']}\n\n"
                        message += f"ℹ️ Sua conta será reativada automaticamente após esta data."
                    else:
                        message += f"ℹ️ Entre em contato com o suporte para mais informações."
                
                # Adiciona a mensagem de erro ao formulário
                form.add_error(None, message)
                return self.form_invalid(form)
            else:
                # Fallback para usuários inativos sem registro de suspensão
                form.add_error(None, _("Sua conta foi desativada. Entre em contato com o suporte para mais informações."))
                return self.form_invalid(form)
        
        # Verifica se o usuário tem 2FA configurado
        totp_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if totp_device:
            logger.info(f"[UserLoginView] Usuário {user.username} tem 2FA ativo - redirecionando para verificação")
            # Salva o user_id temporariamente na sessão para validar o TOTP depois
            self.request.session['pre_2fa_user_id'] = user.pk
            # Salva o estado da requisição para processar a verificação do OTP
            return redirect('verify_2fa')  # Redireciona para a view de verificação do token

        # Se não tiver 2FA configurado, faz o login normalmente
        logger.info(f"[UserLoginView] Fazendo login do usuário {user.username}")
        
        # Reseta as tentativas de login após sucesso
        LoginAttemptsMiddleware.reset_attempts(self.request)
        
        login(self.request, user)
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        return super().form_invalid(form)
       

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts_custom/password-change.html'
    form_class = UserPasswordChangeForm

    def form_valid(self, form):
        print(_("Password changed successfully!"))
        return super().form_valid(form)

    def form_invalid(self, form):
        print(_("Password change failed!"))
        return super().form_invalid(form)
    

class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts_custom/forgot-password.html'
    form_class = UserPasswordResetForm

    def form_valid(self, form):
        print(_("Password reset email sent! (async)"))
        return super().form_valid(form)

    def form_invalid(self, form):
        print(_("Failed to send password reset email!"))
        return super().form_invalid(form)
    

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts_custom/reset-password.html'
    form_class = UserSetPasswordForm

    def form_valid(self, form):
        # Apenas atualiza a senha sem mexer em outros campos do modelo
        form.user.set_password(form.cleaned_data['new_password1'])
        form.user.save(update_fields=["password"])  # Evita save completo que pode tentar mexer no avatar
        print(_("Password has been reset!"))
        return super(PasswordResetConfirmView, self).form_valid(form)

    def form_invalid(self, form):
        print(_("Password reset failed!"))
        return super().form_invalid(form)


def get_user_suspension_info(user):
    """
    Verifica se o usuário está suspenso e retorna informações sobre a suspensão
    """
    if not user or user.is_active:
        return None
    
    try:
        from apps.main.social.models import ModerationAction
        
        # Busca a ação de moderação mais recente que suspendeu o usuário
        suspension_action = ModerationAction.objects.filter(
            target_user=user,
            action_type__in=['suspend_user', 'ban_user'],
            is_active=True
        ).order_by('-created_at').first()
        
        if not suspension_action:
            return {
                'type': 'unknown',
                'message': _('Sua conta foi desativada por um administrador.'),
                'reason': _('Motivo não especificado'),
                'moderator': None,
                'created_at': None,
                'end_date': None,
                'is_permanent': True
            }
        
        # Determina o tipo de suspensão
        if suspension_action.action_type == 'ban_user':
            suspension_type = 'permanent'
            type_message = _('Sua conta foi permanentemente banida.')
        else:
            suspension_type = 'temporary'
            type_message = _('Sua conta foi temporariamente suspensa.')
        
        # Verifica se a suspensão temporária já expirou
        is_expired = False
        if suspension_action.suspension_end_date and suspension_action.suspension_end_date < timezone.now():
            is_expired = True
            type_message = _('Sua suspensão expirou, mas sua conta ainda não foi reativada.')
        
        # Formata a data de fim
        end_date_str = None
        if suspension_action.suspension_end_date:
            end_date_str = suspension_action.suspension_end_date.strftime('%d/%m/%Y às %H:%M')
        
        return {
            'type': suspension_type,
            'message': type_message,
            'reason': suspension_action.reason or _('Motivo não especificado'),
            'public_reason': suspension_action.reason or _('Motivo não especificado'),
            'moderator': suspension_action.moderator.username if suspension_action.moderator else _('Sistema'),
            'created_at': suspension_action.created_at.strftime('%d/%m/%Y às %H:%M'),
            'end_date': end_date_str,
            'is_permanent': suspension_action.action_type == 'ban_user',
            'is_expired': is_expired,
            'action': suspension_action
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar suspensão do usuário {user.username}: {e}")
        return {
            'type': 'error',
            'message': _('Erro ao verificar status da conta.'),
            'reason': _('Entre em contato com o suporte.'),
            'moderator': None,
            'created_at': None,
            'end_date': None,
            'is_permanent': True
        }  