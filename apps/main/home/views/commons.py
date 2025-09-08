import logging

from ..models import *
from ..forms import *

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.translation import activate

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import login as otp_login

from utils.render_theme_page import render_theme_page
from utils.dynamic_import import get_query_class

LineageStats = get_query_class("LineageStats")
logger = logging.getLogger(__name__)


def custom_400_view(request, exception):
    return render(request, 'errors/400.html', status=400)


def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)


def empty_view(request):
    return HttpResponse(status=404)


def terms_view(request):
    context = {
        "last_updated": datetime.today().strftime("%d/%m/%Y"),
    }
    return render_theme_page(request, 'public', 'terms.html', context)


def user_agreement_view(request):
    context = {
        "last_updated": datetime.today().strftime("%d/%m/%Y"),
    }
    return render_theme_page(request, 'public', 'user_agreement.html', context)


def privacy_policy_view(request):
    context = {
        "last_updated": datetime.today().strftime("%d/%m/%Y"),
    }
    return render_theme_page(request, 'public', 'privacy_policy.html', context)


def verificar_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])

            # Adiciona XP
            perfil = PerfilGamer.objects.get(user=user)
            perfil.adicionar_xp(40)  # valor de XP por verificar e-mail

            # Opcional: Armazena mensagem para exibir no template
            context = {
                'sucesso': True,
                'xp': 40,
            }
        else:
            # Já verificado anteriormente
            context = {'ja_verificado': True}
    else:
        context = {'erro': True}

    return render_theme_page(request, 'public', 'email_verificado.html', context)


def custom_set_language(request):
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        next_url = request.POST.get('next', '/')

        if lang_code:
            response = HttpResponseRedirect(next_url)
            response.set_cookie('django_language', lang_code)
            activate(lang_code)

            # Verifica se o usuário já trocou de idioma antes
            if request.user.is_authenticated:
                perfil = PerfilGamer.objects.get(user=request.user)
                
                # Usa uma conquista para marcar se já fez isso antes
                if not ConquistaUsuario.objects.filter(usuario=request.user, conquista__codigo='idioma_trocado').exists():
                    perfil.adicionar_xp(20)  # XP por trocar idioma
                    messages.success(request, "Idioma alterado com sucesso! Você ganhou 20 XP.")

            return response

    return redirect('/')


def registration_success_view(request):
    return render(request, 'accounts_custom/registration_success.html')


def verify_2fa_view(request):
    if request.method == 'POST':
        user_id = request.session.get('pre_2fa_user_id')
        if not user_id:
            logger.warning("[verify_2fa_view] Nenhum user_id encontrado na sessão")
            return redirect('login')

        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
            # Define o backend no usuário para que o Django saiba qual backend foi usado
            user.backend = 'core.backends.LicenseBackend'
        except User.DoesNotExist:
            logger.error(f"[verify_2fa_view] Usuário {user_id} não encontrado")
            return redirect('login')
            
        token = request.POST.get('token')
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        
        if device:
            if device.verify_token(token):
                logger.info(f"[verify_2fa_view] 2FA verificado com sucesso para usuário: {user.username}")
                
                # Marca o 2FA como verificado
                request.user = user
                otp_login(request, device)
                
                # Faz o login usando o sistema padrão do Django
                # O LicenseBackend será executado automaticamente
                logger.info(f"[verify_2fa_view] Fazendo login do usuário {user.username}")
                login(request, user)
                
                del request.session['pre_2fa_user_id']
                return redirect('dashboard')
            else:
                logger.warning(f"[verify_2fa_view] Código 2FA inválido para usuário: {user.username}")
                return render(request, 'accounts_custom/verify-2fa.html', {'error': 'Código inválido.', 'user': user})
        else:
            logger.error(f"[verify_2fa_view] Dispositivo 2FA não encontrado para usuário: {user.username}")
            return render(request, 'accounts_custom/verify-2fa.html', {'error': 'Dispositivo 2FA não configurado ou não confirmado.', 'user': user})
    
    return render(request, 'accounts_custom/verify-2fa.html', {'user': request.user})
