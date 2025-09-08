import json, base64, logging, pyotp, os

from ..models import *
from ..forms import *
from ..resource.twofa import gerar_qr_png

from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import get_language
from django.utils import translation
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.lineage.server.utils.crest import attach_crests_to_clans
from apps.main.home.decorator import conditional_otp_required
from apps.lineage.server.models import IndexConfig, Apoiador
from apps.lineage.wallet.models import Wallet
from apps.lineage.inventory.models import Inventory
from apps.lineage.auction.models import Auction
from apps.lineage.games.utils import verificar_recompensas_por_nivel
from apps.main.news.models import News

from utils.render_theme_page import render_theme_page
from utils.services import verificar_conquistas
from utils.dynamic_import import get_query_class
from apps.main.home.tasks import send_email_task
from utils.fake_players import apply_fake_players
from utils.server_status import check_server_status

LineageStats = get_query_class("LineageStats")
logger = logging.getLogger(__name__)


with open('utils/data/index.json', 'r', encoding='utf-8') as file:
        data_index = json.load(file)


def index(request):
    # Pega os clãs mais bem posicionados
    clanes = LineageStats.top_clans(limit=10) or []

    # Aplica a lógica das crests usando a função já existente
    clanes = attach_crests_to_clans(clanes)

    # Pega os jogadores online
    online = LineageStats.players_online() or []

    # Pega a configuração do índice (ex: nome do servidor)
    config = IndexConfig.objects.first()

    # Contagem de jogadores online
    online_count = online[0]['quant'] if online and isinstance(online, list) and 'quant' in online[0] else 0
    online_count = apply_fake_players(online_count)
    current_lang = get_language()

    # Pega a tradução configurada
    translation = None
    if config:
        translation = config.translations.filter(language=current_lang).first()

    # Caso não exista o registro de configuração ou tradução, usa valores padrões
    nome_servidor = "Lineage 2 PDL"
    descricao_servidor = "Onde Lendas Nascem, Heróis Lutam e a Glória É Eterna."
    jogadores_online_texto = "Jogadores online Agora"

    if config:
        nome_servidor = translation.nome_servidor if translation else config.nome_servidor
        descricao_servidor = translation.descricao_servidor if translation else config.descricao_servidor
        jogadores_online_texto = translation.jogadores_online_texto if translation else config.jogadores_online_texto

    # Classes info (ajustando a descrição conforme a linguagem)
    classes_info = []
    for c in data_index.get('classes', []):
        descricao = c['descricao'].get(current_lang, c['descricao'].get('pt'))  # fallback para 'pt'
        classes_info.append({
            'name': c['name'],
            'descricao': descricao
        })

    # Buscar apoiadores ativos e aprovados
    apoiadores = Apoiador.objects.filter(ativo=True, status='aprovado')

    # Buscar notícias públicas para o tema
    latest_news_list = []
    if hasattr(request, 'theme') and request.theme:
        # Busca notícias públicas para o tema
        all_news = News.objects.filter(is_published=True, is_private=False).order_by('-pub_date')[:10]
        
        for news in all_news:
            translation = news.translations.filter(language=current_lang).first()
            if translation:
                latest_news_list.append({
                    'news': news,
                    'translation': translation
                })

    # Verificar status do servidor
    server_status = check_server_status()

    # Verificar se deve mostrar jogadores online
    show_players_online = getattr(settings, 'SHOW_PLAYERS_ONLINE', True)

    context = {
        'clanes': clanes,
        'classes_info': classes_info,
        'online': online_count,
        'show_players_online': show_players_online,
        'configuracao': config,
        'nome_servidor': nome_servidor,
        'descricao_servidor': descricao_servidor,
        'jogadores_online_texto': jogadores_online_texto,
        'apoiadores': apoiadores,
        'latest_news_list': latest_news_list,
        'server_status': server_status,
    }

    return render_theme_page(request, 'public', 'index.html', context)


@conditional_otp_required
def profile(request):
    context = {
        'segment': 'profile',
        'parent': 'home',
    }
    return render(request, 'pages/profile.html', context)


@conditional_otp_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Verifica se o perfil estava incompleto antes da edição
            perfil_incompleto_antes = not (request.user.first_name and request.user.last_name and request.user.bio)
            
            form.save()
            
            # Verifica se o perfil ficou completo após a edição
            if perfil_incompleto_antes and (request.user.first_name and request.user.last_name and request.user.bio):
                # Dá XP por completar o perfil
                perfil = PerfilGamer.objects.get(user=request.user)
                perfil.adicionar_xp(50)  # 50 XP por completar o perfil
                messages.success(request, "🎉 Perfil completo! Você ganhou 50 XP por completar suas informações pessoais!")
            else:
                messages.success(request, "Perfil atualizado com sucesso!")
                
            return redirect('profile')  # Redireciona para a página de perfil do usuário
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'segment': 'edit-profile',
        'parent': 'home',
        'form': form
    }
    
    return render(request, 'pages/edit_profile.html', context)


@conditional_otp_required
def edit_avatar(request):
    if request.method == 'POST':
        # Verifica se é para remover o avatar
        if request.POST.get('remove_avatar'):
            if request.user.avatar:
                # Remove o arquivo físico se existir
                try:
                    if os.path.exists(request.user.avatar.path):
                        os.remove(request.user.avatar.path)
                except:
                    pass  # Ignora erros de arquivo não encontrado
                request.user.avatar = None
                request.user.save()
                
                messages.success(request, "Avatar removido com sucesso!")
                return redirect('profile')
        
        # Processa upload normal
        form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Avatar atualizado com sucesso!")
            return redirect('edit_avatar')
    else:
        form = AvatarForm(instance=request.user)

    context = {
        'segment': 'avatar',
        'parent': 'home',
        'form': form,
    }
    
    return render(request, 'pages/edit_avatar.html', context)


@conditional_otp_required
def add_or_edit_address(request):
    # Verifica se o usuário já tem um endereço
    address = AddressUser.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = AddressUserForm(request.POST, instance=address)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()

            # Dá XP por cadastrar ou atualizar o endereço
            perfil = PerfilGamer.objects.get(user=request.user)
            perfil.adicionar_xp(30)  # Altere o valor conforme achar adequado

            messages.success(request, "Endereço salvo com sucesso! Você ganhou 30 XP.")
            return redirect('profile')
    else:
        form = AddressUserForm(instance=address)

    context = {
        'segment': 'address',
        'parent': 'home',
        'form': form
    }

    return render(request, 'pages/address_form.html', context)


@staff_member_required
def log_info_dashboard(request):
    log_file_path = 'logs/info.log'  # Caminho para o arquivo de log
    logs_per_page = 20  # Quantidade de logs por página

    try:
        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()
    except FileNotFoundError:
        logs = ['Arquivo de log não encontrado. Verifique a configuração.']

    paginator = Paginator(logs, logs_per_page)
    page_number = request.GET.get('page')
    page_logs = paginator.get_page(page_number)
    context = {
        'segment': 'logs',
        'parent': 'system',
        'page_logs': page_logs
    }

    return render(request, 'pages/logs_info.html', context)


@staff_member_required
def log_error_dashboard(request):
    log_file_path = 'logs/error.log'  # Caminho para o arquivo de log
    logs_per_page = 20  # Quantidade de logs por página

    try:
        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()
    except FileNotFoundError:
        logs = ['Arquivo de log não encontrado. Verifique a configuração.']

    paginator = Paginator(logs, logs_per_page)
    page_number = request.GET.get('page')
    page_logs = paginator.get_page(page_number)
    context = {
        'segment': 'logs',
        'parent': 'system',
        'page_logs': page_logs
    }

    return render(request, 'pages/logs_error.html', context)


@conditional_otp_required
def lock(request):
    error = None
    request.session['is_locked'] = True

    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        authenticated_user = authenticate(request, username=user.username, password=password)
        if authenticated_user:
            # Senha correta: remove o bloqueio
            request.session['is_locked'] = False
            
            # Debug da sessão
            logger.info(f"Lock - Session contents before redirect: {dict(request.session)}")
            
            # Pega a URL de retorno da sessão ou usa dashboard como fallback
            next_url = request.session.get('next', 'dashboard')
            logger.info(f"Lock - Next URL from session: {next_url}")
            
            # Limpa a URL da sessão após usar
            if 'next' in request.session:
                del request.session['next']
                logger.info("Lock - Removed 'next' from session")
            
            logger.info(f"Lock - Redirecting to: {next_url}")
            return redirect(next_url)
        else:
            error = "Senha incorreta. Tente novamente."
            logger.info("Lock - Authentication failed")

    return render(request, 'accounts_custom/lock.html', {
        'error': error,
        'user': request.user,
    })


@conditional_otp_required
def activate_lock(request):
    """
    View para ativar o bloqueio da tela manualmente.
    """
    # Salva a URL atual para retornar após desbloquear
    referer = request.META.get('HTTP_REFERER', 'dashboard')
    logger.info(f"Activate Lock - Referer URL: {referer}")
    request.session['next'] = referer
    request.session['is_locked'] = True
    return redirect('lock')


@conditional_otp_required
def dashboard(request):
    if request.user.is_authenticated:
        language = translation.get_language()
        dashboard = DashboardContent.objects.filter(is_active=True).first()

        translation_obj = None
        if dashboard:
            translation_obj = dashboard.translations.filter(language=language).first() or dashboard.translations.filter(language='pt').first()

        wallet = Wallet.objects.filter(usuario=request.user).first()
        inventories = Inventory.objects.filter(user=request.user)

        # Verificar se o usuário é um apoiador
        try:
            apoiador = Apoiador.objects.get(user=request.user)
            is_apoiador = True
            image = apoiador.imagem.url if apoiador.imagem else None
            status = apoiador.status
        except Apoiador.DoesNotExist:
            is_apoiador = False
            image = None
            status = None

        # Contagem de leilões do usuário
        leiloes_user = Auction.objects.filter(seller=request.user).count()

        perfil, created = PerfilGamer.objects.get_or_create(user=request.user)
        ganhou_bonus = False
        if perfil.pode_receber_bonus_diario():
            ganhou_bonus = perfil.receber_bonus_diario()

        # Verifica conquistas
        conquistas_desbloqueadas = verificar_conquistas(request.user, request=request)
        if conquistas_desbloqueadas:
            for conquista in conquistas_desbloqueadas:
                messages.success(request, f"🏆 Você desbloqueou a conquista: {conquista.nome}!")

        # Todas as conquistas disponíveis
        todas_conquistas = Conquista.objects.all()

        # IDs das conquistas do usuário
        conquistas_usuario_ids = set(
            ConquistaUsuario.objects.filter(usuario=request.user).values_list('conquista_id', flat=True)
        )

        # Lista de conquistas com flag "desbloqueada"
        conquistas = [
            {
                'conquista': conquista,
                'desbloqueada': conquista.id in conquistas_usuario_ids
            }
            for conquista in todas_conquistas
        ]

        # Paginação
        page_number = request.GET.get('page', 1)
        paginator = Paginator(conquistas, 12)  # 12 conquistas por página
        page_obj = paginator.get_page(page_number)

        verificar_recompensas_por_nivel(request.user, perfil.level, request)

        context = {
            'segment': 'dashboard',
            'dashboard': dashboard,
            'translation': translation_obj,
            'wallet': wallet,
            'inventories': inventories,
            'is_apoiador': is_apoiador,
            'image': image,
            'status': status,
            'leiloes_user': leiloes_user,
            'perfil': perfil,
            'ganhou_bonus': ganhou_bonus,
            'xp_percent': int((perfil.xp / perfil.xp_para_proximo_nivel()) * 100),
            'conquistas': page_obj.object_list,
            'page_obj': page_obj,
            'debug': settings.DEBUG,
        }
        return render(request, 'dashboard_custom/dashboard.html', context)
    else:
        return redirect('/')


@conditional_otp_required
def reenviar_verificacao_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            if user.is_email_verified:
                messages.info(request, 'Seu email já está verificado.')
                return redirect('dashboard')

            # Gera novo link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verificar_email', args=[uid, token])
            )

            # Envia o e-mail
            try:
                send_email_task.delay(
                    'Reenvio de verificação de e-mail',
                    f'Olá {user.username},\n\nAqui está seu novo link de verificação:\n\n{verification_link}\n\nSe você não solicitou isso, ignore este e-mail.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                messages.success(request, 'Um novo e-mail de verificação foi enviado.')
            except Exception as e:
                logger.error(f"Erro ao enviar email: {str(e)}")
                messages.error(request, 'Não foi possível enviar o e-mail no momento. Tente novamente mais tarde.')

            return redirect('dashboard')

        except User.DoesNotExist:
            messages.error(request, 'Nenhuma conta foi encontrada com este e-mail.')

    return render(request, 'verify/reenviar_verificacao.html')


@conditional_otp_required
def ativar_2fa(request):
    user = request.user

    # Verifica se já existe um dispositivo 2FA confirmado
    if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
        messages.info(request, "A autenticação em 2 etapas já está ativada.")
        return redirect('dashboard')

    # Cria ou reutiliza um dispositivo ainda não confirmado
    device, created = TOTPDevice.objects.get_or_create(user=user, confirmed=False)

    # Converte a chave hex para base32 (como o pyotp espera)
    base32_key = base64.b32encode(bytes.fromhex(device.key)).decode('utf-8')

    # Gera o QR Code em PNG (base64) para exibir na página
    qr_png = gerar_qr_png(user.email, base32_key)

    if request.method == "POST":
        token = request.POST.get("token")
        totp = pyotp.TOTP(base32_key)

        if totp.verify(token):
            device.confirmed = True
            device.save()

            user.is_2fa_enabled = True
            user.save()

            # Dá XP pela ativação
            perfil = PerfilGamer.objects.get(user=user)
            perfil.adicionar_xp(60)

            messages.success(request, "Autenticação em 2 etapas ativada com sucesso! Você ganhou 60 XP.")
            return redirect('dashboard')
        else:
            messages.error(request, "Código inválido. Tente novamente.")

    return render(request, 'accounts_custom/ativar-2fa.html', {
        'qr_png': qr_png,
        'otp_secret': base32_key,
    })


@conditional_otp_required
def desativar_2fa(request):
    user = request.user

    if request.method != "POST":
        messages.warning(request, "Requisição inválida.")
        return redirect('administrator:security_settings')

    # Remove dispositivos TOTP confirmados
    devices = TOTPDevice.objects.filter(user=user, confirmed=True)
    if not devices.exists():
        messages.info(request, "Você não possui autenticação em duas etapas ativada.")
        return redirect('administrator:security_settings')

    devices.delete()

    # Atualiza o campo de status no usuário, se houver
    if hasattr(user, 'is_2fa_enabled'):
        user.is_2fa_enabled = False
        user.save()

    messages.success(request, "Autenticação em duas etapas desativada com sucesso.")
    return redirect('administrator:security_settings')
