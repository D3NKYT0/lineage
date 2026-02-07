import logging
from datetime import datetime, timedelta

from ..models import *
from ..forms import *
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.translation import activate, gettext as _

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
            perfil, _ = PerfilGamer.objects.get_or_create(user=user)
            perfil.adicionar_xp(40)  # valor de XP por verificar e-mail

            # Define a conta mestre do e-mail (primeira verificação vira dona)
            user.ensure_email_master_owner()

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
                perfil, _ = PerfilGamer.objects.get_or_create(user=request.user)
                
                # Usa uma conquista para marcar se já fez isso antes
                if not ConquistaUsuario.objects.filter(usuario=request.user, conquista__codigo='idioma_trocado').exists():
                    perfil.adicionar_xp(20)  # XP por trocar idioma
                    messages.success(request, "Idioma alterado com sucesso! Você ganhou 20 XP.")

            return response

    return redirect('/')


def registration_success_view(request):
    return render_theme_page(request, 'accounts_custom', 'registration_success.html', {})


def verify_2fa_view(request):
    # Pega a URL de retorno (next) se existir
    next_url = request.GET.get('next', 'dashboard')
    
    if request.method == 'POST':
        # Tenta pegar o usuário de duas formas:
        # 1. Se já estiver autenticado (caso do decorator)
        # 2. Se tiver pre_2fa_user_id na sessão (caso do login inicial)
        if request.user.is_authenticated:
            user = request.user
            logger.info(f"[verify_2fa_view] Usuário já autenticado: {user.username}")
        else:
            user_id = request.session.get('pre_2fa_user_id')
            if not user_id:
                logger.warning("[verify_2fa_view] Nenhum user_id encontrado na sessão e usuário não autenticado")
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
                
                # Marca o 2FA como verificado usando otp_login
                otp_login(request, device)
                
                # Se o usuário não estava autenticado, faz o login
                if not request.user.is_authenticated:
                    logger.info(f"[verify_2fa_view] Fazendo login do usuário {user.username}")
                    login(request, user)
                    if 'pre_2fa_user_id' in request.session:
                        del request.session['pre_2fa_user_id']
                
                # Redireciona para a URL de retorno ou dashboard
                logger.info(f"[verify_2fa_view] Redirecionando para: {next_url}")
                return redirect(next_url)
            else:
                logger.warning(f"[verify_2fa_view] Código 2FA inválido para usuário: {user.username}")
                context = {'error': 'Código inválido.', 'user': user, 'next': next_url}
                return render_theme_page(request, 'accounts_custom', 'verify-2fa.html', context)
        else:
            logger.error(f"[verify_2fa_view] Dispositivo 2FA não encontrado para usuário: {user.username}")
            context = {'error': 'Dispositivo 2FA não configurado ou não confirmado.', 'user': user, 'next': next_url}
            return render_theme_page(request, 'accounts_custom', 'verify-2fa.html', context)
    
    # GET request - mostra o formulário
    user = request.user if request.user.is_authenticated else None
    context = {'user': user, 'next': next_url}
    return render_theme_page(request, 'accounts_custom', 'verify-2fa.html', context)


@staff_member_required
@require_http_methods(["GET", "POST"])
def coming_soon_config_view(request):
    """Página para editar Coming Soon a partir da Central de Configurações."""
    from apps.lineage.server.models import ComingSoonConfig
    from ..forms import ComingSoonConfigForm

    config = ComingSoonConfig.objects.first()
    if config is None:
        config = ComingSoonConfig(
            title=_('Em Breve'),
            subtitle=_('Algo incrível está por vir. Fique ligado!'),
            countdown_date=timezone.now() + timedelta(days=7),
        )
        config.save()

    if request.method == 'POST':
        form = ComingSoonConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, _('Coming Soon atualizado com sucesso.'))
            return redirect('config_hub')
        messages.error(request, _('Corrija os erros abaixo.'))
    else:
        form = ComingSoonConfigForm(instance=config)

    return render(request, 'config/coming_soon.html', {
        'form': form,
        'config': config,
    })


def config_hub_view(request):
    # Centralizar links de configuração em uma única tela, organizados por categorias
    categories = [
        {
            'name': _('Sistema & API'),
            'icon': 'bi-server',
            'color': 'primary',
            'entries': [
                { 'title': _('API'), 'url_name': 'api:api_config_panel', 'icon': 'bi-hdd-network', 'description': _('Configurar chaves e permissões da API') },
                { 'title': _('Recursos'), 'url_name': 'resources:dashboard', 'icon': 'bi-archive', 'description': _('Gerenciar recursos do sistema') },
            ]
        },
        {
            'name': _('Financeiro'),
            'icon': 'bi-wallet2',
            'color': 'success',
            'entries': [
                { 'title': _('Moedas'), 'url_name': 'wallet:coin_config_panel', 'icon': 'bi-coin', 'description': _('Configurar moedas e taxas') },
                { 'title': _('Shop'), 'url_name': 'shop:dashboard', 'icon': 'bi-bag-check', 'description': _('Gerenciar loja e produtos') },
            ]
        },
        {
            'name': _('Jogos'),
            'icon': 'bi-controller',
            'color': 'warning',
            'entries': [
                { 'title': _('Box Manager'), 'url_name': 'games:box_manager_dashboard', 'icon': 'bi-box-seam', 'description': _('Configurar caixas e itens') },
                { 'title': _('Daily Bonus Manager'), 'url_name': 'games:daily_bonus_manager', 'icon': 'bi-calendar-week', 'description': _('Gerenciar bônus diários') },
                { 'title': _('Roulette Manager'), 'url_name': 'games:roulette_manager', 'icon': 'bi-shuffle', 'description': _('Configurar roleta e prêmios') },
                { 'title': _('Economy Manager'), 'url_name': 'games:economy_manager', 'icon': 'bi-lightning-charge', 'description': _('Gerenciar economia do jogo') },
                { 'title': _('Battle Pass Manager'), 'url_name': 'games:battle_pass_manager', 'icon': 'bi-trophy', 'description': _('Configurar temporadas e recompensas') },
                { 'title': _('Achievement Rewards Manager'), 'url_name': 'games:achievement_rewards_manager', 'icon': 'bi-award', 'description': _('Premiações de conquistas') },
                { 'title': _('Level Rewards Manager'), 'url_name': 'games:level_rewards_manager', 'icon': 'bi-star', 'description': _('Recompensas por nível') },
                { 'title': _('Slot Machine Manager'), 'url_name': 'games:slot_machine_manager', 'icon': 'bi-dice-6', 'description': _('Configurar máquina de slots') },
                { 'title': _('Dice Game Manager'), 'url_name': 'games:dice_game_manager', 'icon': 'bi-dice-5', 'description': _('Gerenciar jogo de dados') },
                { 'title': _('Fishing Game Manager'), 'url_name': 'games:fishing_game_manager', 'icon': 'bi-water', 'description': _('Configurar pescaria e recompensas') },
            ]
        },
        {
            'name': _('Conteúdo'),
            'icon': 'bi-file-text',
            'color': 'info',
            'entries': [
                { 'title': _('Coming Soon'), 'url_name': 'config_coming_soon', 'icon': 'bi-hourglass-split', 'is_new': True, 'description': _('Contagem regressiva na página inicial') },
                { 'title': _('Calendar Manager'), 'url_name': 'calendary:manager_dashboard', 'icon': 'bi-calendar-event', 'description': _('Gerenciar eventos do calendário') },
                { 'title': _('Roadmap Manager'), 'url_name': 'roadmap:manager_dashboard', 'icon': 'bi-diagram-3', 'description': _('Planejamento e atualizações') },
            ]
        },
        {
            'name': _('Servidor'),
            'icon': 'bi-hdd-stack',
            'color': 'secondary',
            'entries': [
                { 'title': _('Services'), 'url_name': 'server:configure_service_prices', 'icon': 'bi-gear', 'description': _('Preços de serviços do servidor') },
                { 'title': _('Apoiadores'), 'url_name': 'server:painel_staff', 'icon': 'bi-people', 'description': _('Gerenciar apoiadores e staff') },
            ]
        },
        {
            'name': _('Administração'),
            'icon': 'bi-shield-check',
            'color': 'danger',
            'entries': [
                { 'title': _('Licenças'), 'url_name': 'licence:dashboard', 'icon': 'bi-patch-check', 'description': _('Gerenciar licenças do sistema') },
                { 'title': _('Gerenciador de Notificações'), 'url_name': 'notification:manager_dashboard', 'icon': 'bi-bell', 'description': _('Criar e gerenciar notificações com prêmios') },
                { 'title': _('Enviar Push'), 'url_name': 'notification:send_push', 'icon': 'bi-bell-fill', 'description': _('Enviar notificações push') },
                { 'title': _('Verificações'), 'url_name': 'social:verification_admin_list', 'icon': 'bi-shield-check', 'description': _('Aprovar verificações de usuários') },
            ]
        },
    ]
    return render(request, 'config/hub.html', { 'categories': categories })


def accept_cookies_view(request):
    """View para aceitar cookies - salva o consentimento em cookie"""
    response = JsonResponse({'status': 'success'})
    # Cookie válido por 1 ano
    expires = datetime.now() + timedelta(days=365)
    response.set_cookie(
        'cookie_consent',
        'accepted',
        expires=expires,
        httponly=False,  # Precisa ser acessível via JavaScript
        samesite='Lax'
    )
    return response
