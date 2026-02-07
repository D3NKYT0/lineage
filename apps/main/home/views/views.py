import json, base64, logging, pyotp, os, re
import requests
from datetime import datetime
from django.db.models import Q

from ..models import *
from ..forms import *
from ..resource.twofa import gerar_qr_png
from ..services.profile_rewards import build_profile_rewards_context

from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import get_language, gettext_lazy as _
from django.utils import translation
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.lineage.server.utils.crest import attach_crests_to_clans
from apps.main.home.decorator import conditional_otp_required
from apps.lineage.server.models import IndexConfig, Apoiador, ComingSoonConfig
from apps.lineage.wallet.models import Wallet
from apps.lineage.inventory.models import Inventory
from apps.lineage.auction.models import Auction
from apps.lineage.games.utils import verificar_recompensas_por_nivel
from utils.render_theme_page import render_theme_page
from apps.main.news.models import News
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
    from django.core.cache import cache
    import time

    # Coming Soon: quando ativo, exibe a tela de contagem regressiva no lugar da index
    coming_soon = ComingSoonConfig.objects.first()
    if coming_soon and coming_soon.is_active:
        context = {
            'config': coming_soon,
            'countdown_iso': coming_soon.countdown_date.isoformat() if coming_soon.countdown_date else '',
        }
        if coming_soon.background_image:
            context['background_image_url'] = request.build_absolute_uri(coming_soon.background_image.url)
        return render(request, 'public/coming_soon.html', context)
    
    # Cache keys para evitar queries repetidas
    cache_timeout = 60  # 1 minuto de cache
    
    # Pega os clãs mais bem posicionados com cache e fallback
    clanes_cache_key = 'index_top_clans'
    clanes = cache.get(clanes_cache_key)
    
    if clanes is None:
        try:
            # Timeout curto para evitar travamento
            start_time = time.time()
            clanes = LineageStats.top_clans(limit=10) or []
            
            # Se demorou mais que 2 segundos, usa cache vazio
            if time.time() - start_time > 2:
                logger.warning("Query top_clans demorou mais que 2s, usando fallback")
                clanes = []
            
            # Aplica a lógica das crests usando a função já existente
            if clanes:
                clanes = attach_crests_to_clans(clanes)
            
            cache.set(clanes_cache_key, clanes, cache_timeout)
        except Exception as e:
            logger.error(f"Erro ao buscar top clans: {e}")
            clanes = []
            cache.set(clanes_cache_key, [], 30)  # Cache erro por 30s

    # Pega os jogadores online com cache e fallback
    online_cache_key = 'index_players_online'
    online = cache.get(online_cache_key)
    
    if online is None:
        try:
            start_time = time.time()
            online = LineageStats.players_online() or []
            
            # Se demorou mais que 1 segundo, usa fallback
            if time.time() - start_time > 1:
                logger.warning("Query players_online demorou mais que 1s, usando fallback")
                online = [{'quant': 0}]
            
            cache.set(online_cache_key, online, cache_timeout)
        except Exception as e:
            logger.error(f"Erro ao buscar players online: {e}")
            online = [{'quant': 0}]
            cache.set(online_cache_key, online, 30)  # Cache erro por 30s

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
        descricao = c['descricao']  # já é string
        classes_info.append({
            'name': c['name'],
            'slug': c['slug'],  # necessário para o template
            'badge': c['badge'],
            'difficulty': c['difficulty'],
            'stats': c['stats'],
            'skills': c['skills'],
            'descricao': descricao,
            'image': c['image'],  # se você quiser usar
        })

    # Buscar apoiadores ativos e aprovados
    apoiadores = Apoiador.objects.filter(ativo=True, status='aprovado')

    # Buscar notícias públicas para o tema
    latest_news_list = []
    # Busca notícias públicas (sempre, não apenas quando há tema)
    try:
        all_news = News.objects.filter(is_published=True, is_private=False).order_by('-pub_date')[:10]
        logger.info(f"Encontradas {all_news.count()} notícias públicas")
        
        for news in all_news:
            # Tenta buscar tradução no idioma atual
            translation = news.translations.filter(language=current_lang).first()
            # Se não encontrar, tenta português como fallback
            if not translation:
                translation = news.translations.filter(language='pt').first()
            # Se ainda não encontrar, pega a primeira tradução disponível
            if not translation:
                translation = news.translations.first()
            
            # Se encontrou tradução, adiciona à lista
            if translation:
                latest_news_list.append({
                    'news': news,
                    'translation': translation
                })
            else:
                # Log para debug se não encontrou tradução
                logger.warning(f"Notícia {news.pk} não tem tradução disponível")
    except Exception as e:
        logger.error(f"Erro ao buscar notícias: {e}")
        latest_news_list = []

    # Buscar conteúdos do media_storage para a seção Content
    content_items = []
    if hasattr(request, 'theme') and request.theme:
        try:
            from apps.media_storage.models import MediaFile, MediaCategory
            # Busca arquivos de mídia públicos e ativos, limitando a 4 itens
            content_items = MediaFile.objects.filter(
                is_public=True,
                is_active=True,
                file_type='image'  # Apenas imagens para a seção Content
            ).order_by('-uploaded_at')[:4]
        except Exception as e:
            logger.error(f"Erro ao buscar conteúdos do media_storage: {e}")
            content_items = []

    # Verificar status do servidor com cache
    server_status_cache_key = 'index_server_status'
    server_status = cache.get(server_status_cache_key)
    
    if server_status is None:
        try:
            start_time = time.time()
            server_status = check_server_status()
            
            # Se demorou mais que 1 segundo, usa status offline
            if time.time() - start_time > 1:
                logger.warning("check_server_status demorou mais que 1s, usando fallback")
                server_status = {
                    'overall_status': 'offline',
                    'game_server': {'status': 'offline'},
                    'login_server': {'status': 'offline'},
                    'server_ip': '127.0.0.1',
                    'checked_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            cache.set(server_status_cache_key, server_status, cache_timeout)
        except Exception as e:
            logger.error(f"Erro ao verificar status do servidor: {e}")
            server_status = {
                'overall_status': 'offline',
                'game_server': {'status': 'offline'},
                'login_server': {'status': 'offline'},
                'server_ip': '127.0.0.1',
                'checked_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            cache.set(server_status_cache_key, server_status, 30)  # Cache erro por 30s

    # Verificar se deve mostrar jogadores online
    show_players_online = getattr(settings, 'SHOW_PLAYERS_ONLINE', True)

    # Buscar banners ativos e visíveis
    banners = []
    popup_banners = []
    try:
        from django.utils import timezone
        now = timezone.now()
        banners_queryset = Banner.objects.filter(is_active=True)
        
        # Filtrar por datas se necessário
        banners_queryset = banners_queryset.filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        )
        
        # Agrupar por posição (apenas banners normais)
        banners_by_position = {
            'top': [],
            'middle': [],
            'bottom': []
        }
        
        # Separar banners normais de pop-ups
        for banner in banners_queryset.order_by('display_order', '-created_at'):
            if banner.is_visible():
                if banner.display_type == 'popup':
                    popup_banners.append(banner)
                else:
                    banners_by_position[banner.position].append(banner)
        
        banners = banners_by_position
    except Exception as e:
        logger.error(f"Erro ao buscar banners: {e}")
        banners = {'top': [], 'middle': [], 'bottom': []}
        popup_banners = []

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
        'content_items': content_items,
        'server_status': server_status,
        'banners': banners,
        'popup_banners': popup_banners,
    }

    return render_theme_page(request, 'public', 'index.html', context)


@conditional_otp_required
def profile(request):
    import logging
    logger = logging.getLogger(__name__)
    
    # Informações sobre o email master owner
    email_master_owner = None
    is_email_master_owner = True
    
    if request.user.email:
        email_master_owner = request.user.get_email_master_owner()
        is_email_master_owner = request.user.is_email_master_owner
    
    # Verifica se a conta principal do usuário está realmente vinculada
    account_is_linked = False
    original_email_master_owner = email_master_owner
    
    try:
        from utils.dynamic_import import get_query_class
        LineageAccount = get_query_class("LineageAccount")
        
        if LineageAccount and request.user.username:
            conta_data = LineageAccount.check_login_exists(request.user.username)
            if conta_data and len(conta_data) > 0:
                conta = conta_data[0]
                linked_uuid = conta.get("linked_uuid") if isinstance(conta, dict) else getattr(conta, 'linked_uuid', None)
                account_is_linked = bool(linked_uuid)
    except Exception as e:
        logger.warning(f"Erro ao verificar se conta principal está vinculada: {e}")
    
    # Se a conta não está vinculada, não mostra informações de conta mestre
    # mas mantém a referência para mostrar mensagem de desvinculação
    if not account_is_linked:
        is_email_master_owner = True
    
    reward_context = build_profile_rewards_context(request.user)

    from utils.push import get_push_choices_for_user
    perfil = PerfilGamer.objects.filter(user=request.user).first()
    push_prefs = getattr(perfil, 'push_preferences', None) if perfil else {}
    push_prefs = push_prefs or {}
    choices = get_push_choices_for_user(request.user)
    push_choices_with_pref = [(key, label, staff_only, push_prefs.get(key, True) is not False) for key, label, staff_only in choices]

    context = {
        'segment': 'profile',
        'parent': 'home',
        'email_master_owner': email_master_owner if account_is_linked else None,
        'is_email_master_owner': is_email_master_owner,
        'account_is_linked': account_is_linked,
        'original_email_master_owner': original_email_master_owner,  # Para mostrar mensagem de desvinculação
        'push_choices_with_pref': push_choices_with_pref,
    }
    context.update(reward_context)
    return render(request, 'pages/profile.html', context)


@conditional_otp_required
@require_http_methods(["POST"])
def save_push_preferences(request):
    """Salva preferências de notificações push a partir do formulário do perfil."""
    from apps.main.home.models import PerfilGamer
    from utils.push import PUSH_EVENT_CHOICES

    perfil, _ = PerfilGamer.objects.get_or_create(user=request.user)
    is_staff = getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False)
    prefs = dict(getattr(perfil, "push_preferences", None) or {})

    for key, _label, staff_only in PUSH_EVENT_CHOICES:
        if staff_only and not is_staff:
            continue
        prefs[key] = request.POST.get("push_" + key) == "1"

    perfil.push_preferences = prefs
    perfil.save()
    messages.success(request, _("Preferências de notificações push salvas."))
    return redirect("profile")


@conditional_otp_required
def edit_profile(request):
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Verifica se o e-mail foi alterado
            old_email = request.user.email
            new_email = form.cleaned_data.get('email')
            email_changed = old_email != new_email
            
            logger.info(f"[edit_profile] POST recebido - Usuário: {request.user.username}")
            logger.info(f"[edit_profile] E-mail antigo: {old_email}, E-mail novo: {new_email}, Alterado: {email_changed}")
            
            # Verifica se o perfil estava incompleto antes da edição
            perfil_incompleto_antes = not (request.user.first_name and request.user.last_name and request.user.bio)
            
            form.save()
            
            # Recarrega o usuário para ter os dados atualizados
            request.user.refresh_from_db()
            
            # Se o e-mail foi alterado, atualiza o email nas contas do Lineage vinculadas
            if email_changed and new_email:
                try:
                    from utils.dynamic_import import get_query_class
                    LineageDBClass = get_query_class("LineageDB")
                    
                    if LineageDBClass:
                        lineage_db = LineageDBClass()
                        if lineage_db and getattr(lineage_db, 'enabled', False):
                            user_uuid = str(request.user.uuid) if hasattr(request.user, 'uuid') else None
                            if user_uuid:
                                # Atualiza o email de todas as contas vinculadas ao UUID do usuário
                                sql = """
                                    UPDATE accounts
                                    SET email = :new_email
                                    WHERE linked_uuid = :uuid
                                """
                                params = {
                                    "new_email": new_email,
                                    "uuid": user_uuid
                                }
                                result = lineage_db.update(sql, params)
                                logger.info(f"[edit_profile] Atualizado email para {result} conta(s) do Lineage vinculadas ao UUID {user_uuid}")
                                
                                # Verifica se a atualização funcionou
                                if result and result > 0:
                                    # Busca uma conta para verificar se o email foi atualizado
                                    verify_sql = """
                                        SELECT login, email, linked_uuid
                                        FROM accounts
                                        WHERE linked_uuid = :uuid
                                        LIMIT 1
                                    """
                                    verify_result = lineage_db.select(verify_sql, {"uuid": user_uuid})
                                    if verify_result:
                                        verify_email = verify_result[0].get("email") if isinstance(verify_result[0], dict) else getattr(verify_result[0], 'email', None)
                                        logger.info(f"[edit_profile] Verificação: Email no banco após UPDATE: {verify_email}, Email esperado: {new_email}")
                except Exception as e:
                    logger.warning(f"Erro ao atualizar email nas contas do Lineage: {e}", exc_info=True)
            
            # Se o e-mail foi alterado e está verificado, garante que existe EmailOwnership
            if email_changed and new_email and request.user.is_email_verified:
                request.user.ensure_email_master_owner()
            
            # INDEPENDENTE de ter alterado o email ou não:
            # Se a conta atual tem um email que já está validado por uma conta mestre,
            # vincula APENAS a conta atual (username) ao UUID da conta mestre
            # NÃO vincula outras contas com o mesmo email
            user_email = request.user.email
            if user_email:
                try:
                    from apps.main.home.models import EmailOwnership
                    from utils.dynamic_import import get_query_class
                    
                    logger.info(f"[edit_profile] Verificando se email {user_email} tem conta mestre")
                    
                    # Verifica se existe uma conta mestre para este e-mail
                    email_ownership = EmailOwnership.objects.filter(email=user_email).first()
                    
                    if email_ownership:
                        master_user = email_ownership.owner
                        master_uuid = str(master_user.uuid) if hasattr(master_user, 'uuid') else None
                        user_login = request.user.username
                        
                        logger.info(f"[edit_profile] Email {user_email} tem conta mestre: {master_user.username}")
                        logger.info(f"[edit_profile] Vinculando APENAS a conta atual '{user_login}' ao UUID {master_uuid}")
                        
                        if master_uuid and user_login:
                            # Verifica limite de slots antes de vincular
                            from apps.lineage.server.services.account_context import can_link_account
                            can_link, error_message = can_link_account(master_user)
                            if not can_link:
                                logger.warning(f"[edit_profile] ⚠️ Limite de slots atingido para {master_user.username}: {error_message}")
                                messages.warning(
                                    request,
                                    f"⚠️ Não foi possível vincular a conta '{user_login}'. {error_message}"
                                )
                            else:
                                LineageDBClass = get_query_class("LineageDB")
                                
                                if LineageDBClass:
                                    try:
                                        lineage_db = LineageDBClass()
                                        if lineage_db and getattr(lineage_db, 'enabled', False):
                                            # Verifica se o banco está conectado antes de tentar atualizar
                                            if hasattr(lineage_db, 'is_connected') and not lineage_db.is_connected():
                                                logger.warning(f"[edit_profile] ⚠️ Banco do Lineage indisponível para vincular conta '{user_login}'")
                                                messages.warning(
                                                    request,
                                                    f"⚠️ Não foi possível vincular a conta '{user_login}' automaticamente. O banco de dados do Lineage está indisponível."
                                                )
                                            else:
                                                # Vincula APENAS a conta atual (username) ao UUID da conta mestre
                                                sql = """
                                                    UPDATE accounts
                                                    SET linked_uuid = :uuid, email = :email
                                                    WHERE login = :login
                                                """
                                                params = {
                                                    "uuid": master_uuid,
                                                    "email": user_email,
                                                    "login": user_login
                                                }
                                                result = lineage_db.update(sql, params)
                                                
                                                if result and result > 0:
                                                    logger.info(f"[edit_profile] ✅ Conta '{user_login}' vinculada ao mestre {master_user.username} com sucesso")
                                                    messages.info(
                                                        request,
                                                        f"✅ Conta do Lineage '{user_login}' foi vinculada à conta mestre {master_user.username}."
                                                    )
                                                else:
                                                    logger.warning(f"[edit_profile] ⚠️ Conta '{user_login}' não encontrada no banco do Lineage ou já está vinculada")
                                    except Exception as db_error:
                                        logger.error(f"[edit_profile] Erro ao acessar banco do Lineage para vincular conta '{user_login}': {db_error}", exc_info=True)
                                        messages.warning(
                                            request,
                                            f"⚠️ Não foi possível vincular a conta '{user_login}' automaticamente. O banco de dados do Lineage pode estar indisponível."
                                        )
                    else:
                        logger.info(f"[edit_profile] Email {user_email} não tem conta mestre, nenhuma vinculação automática")
                except Exception as e:
                    logger.error(f"Erro ao vincular conta atual do Lineage: {e}", exc_info=True)
            
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
            user = form.save()
            
            # Processa avatar (síncrono em DEBUG, assíncrono em produção)
            if 'avatar' in request.FILES and user.avatar:
                try:
                    from apps.main.home.tasks import process_avatar_image_task, execute_task_sync_or_async
                    if hasattr(user.avatar, 'path'):
                        execute_task_sync_or_async(process_avatar_image_task, user.id, user.avatar.path)
                except Exception as e:
                    logger.warning(f"Erro ao {'processar' if settings.DEBUG else 'agendar processamento de'} avatar: {e}")
            
            messages.success(request, "Avatar atualizado! Processando em background...")
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
    
    from utils.pagination_helper import prepare_pagination_context
    pagination_context = prepare_pagination_context(page_logs)
    
    context = {
        'segment': 'logs',
        'parent': 'system',
        'page_logs': page_logs,
        **pagination_context,
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
    
    from utils.pagination_helper import prepare_pagination_context
    pagination_context = prepare_pagination_context(page_logs)
    
    context = {
        'segment': 'logs',
        'parent': 'system',
        'page_logs': page_logs,
        **pagination_context,
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

    context = {
        'error': error,
        'user': request.user,
    }
    return render_theme_page(request, 'accounts_custom', 'lock.html', context)


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
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[dashboard view] Executando view dashboard - User authenticated: {request.user.is_authenticated}")
    logger.info(f"[dashboard view] User: {request.user}")
    
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
        
        # Prepara dados de paginação para o template
        current_page = page_obj.number
        total_pages = paginator.num_pages
        has_previous = page_obj.has_previous()
        has_next = page_obj.has_next()
        previous_page_number = page_obj.previous_page_number() if has_previous else None
        next_page_number = page_obj.next_page_number() if has_next else None
        
        # Calcula o range de páginas a mostrar (máximo 5 páginas ao redor da atual)
        if total_pages <= 7:
            # Se tem 7 ou menos páginas, mostra todas
            page_range = list(paginator.page_range)
            show_first = False
            show_last = False
            show_first_ellipsis = False
            show_last_ellipsis = False
        else:
            # Se tem mais de 7 páginas, mostra range inteligente
            if current_page <= 4:
                # Perto do início: mostra primeiras 5 páginas
                page_range = list(range(1, 6))
                show_first = False
                show_last = True
                show_first_ellipsis = False
                show_last_ellipsis = True
            elif current_page >= total_pages - 3:
                # Perto do fim: mostra últimas 5 páginas
                page_range = list(range(total_pages - 4, total_pages + 1))
                show_first = True
                show_last = False
                show_first_ellipsis = True
                show_last_ellipsis = False
            else:
                # No meio: mostra 2 antes e 2 depois da atual
                page_range = list(range(current_page - 2, current_page + 3))
                show_first = True
                show_last = True
                show_first_ellipsis = True
                show_last_ellipsis = True

        verificar_recompensas_por_nivel(request.user, perfil.level, request)

        # Calcular nível da patente (limitado a 30)
        patent_level = perfil.get_patent_level()

        # Saudação baseada no horário do dia
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            greeting = _("Bom dia")
            greeting_emoji = "🌅"
        elif 12 <= current_hour < 18:
            greeting = _("Boa tarde")
            greeting_emoji = "☀️"
        elif 18 <= current_hour < 22:
            greeting = _("Boa noite")
            greeting_emoji = "🌆"
        else:
            greeting = _("Boa madrugada")
            greeting_emoji = "🌙"

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
            'patent_level': patent_level,
            'conquistas': page_obj.object_list,
            'page_obj': page_obj,
            'debug': settings.DEBUG,
            'greeting': greeting,
            'greeting_emoji': greeting_emoji,
            # Variáveis de paginação para o template includes/pagination.html
            'current_page': current_page,
            'total_pages': total_pages,
            'has_previous': has_previous,
            'has_next': has_next,
            'previous_page_number': previous_page_number,
            'next_page_number': next_page_number,
            'page_range': page_range,
            'show_first': show_first,
            'show_last': show_last,
            'show_first_ellipsis': show_first_ellipsis,
            'show_last_ellipsis': show_last_ellipsis,
            'vapid_configured': bool(getattr(settings, 'VAPID_PUBLIC_KEY', None) and getattr(settings, 'VAPID_PRIVATE_KEY', None)),
        }
        return render(request, 'dashboard_custom/dashboard.html', context)
    else:
        return redirect('/')


@conditional_otp_required
def reenviar_verificacao_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            # Use filter().first() instead of get() to handle multiple users with same email
            user = User.objects.filter(email=email).first()
            
            if user is None:
                messages.error(request, 'Nenhuma conta foi encontrada com este e-mail.')
                return render(request, 'verify/reenviar_verificacao.html')
            
            # Log warning if multiple users exist with same email (data integrity issue)
            user_count = User.objects.filter(email=email).count()
            if user_count > 1:
                logger.warning(f"Múltiplos usuários encontrados com o email {email} ({user_count} usuários). Usando o primeiro (ID: {user.pk}).")

            if user.is_email_verified:
                messages.info(request, 'Seu email já está verificado.')
                return redirect('dashboard')

            # Gera novo link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('verificar_email', args=[uid, token])
            )

            # Envia o e-mail (síncrono em DEBUG, assíncrono em produção)
            try:
                from apps.main.home.tasks import send_email_task, execute_task_sync_or_async
                execute_task_sync_or_async(
                    send_email_task,
                    'Reenvio de verificação de e-mail',
                    f'Olá {user.username},\n\nAqui está seu novo link de verificação:\n\n{verification_link}\n\nSe você não solicitou isso, ignore este e-mail.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                messages.success(request, 'Um novo e-mail de verificação foi enviado.')
                logger.info(f"Email de reenvio {'enviado' if settings.DEBUG else 'agendado'} para {user.email}")
            except Exception as e:
                logger.error(f"Erro ao {'enviar' if settings.DEBUG else 'agendar'} envio de email: {str(e)}")
                messages.error(request, 'Não foi possível enviar o e-mail no momento. Tente novamente mais tarde.')

            return redirect('dashboard')

        except Exception as e:
            logger.error(f"Erro inesperado em reenviar_verificacao_view: {str(e)}")
            messages.error(request, 'Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.')

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

    context = {
        'qr_png': qr_png,
        'otp_secret': base32_key,
    }
    return render_theme_page(request, 'accounts_custom', 'ativar-2fa.html', context)


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


@require_http_methods(["GET"])
@staff_member_required
def check_version_update(request):
    """
    Verifica se existe uma versão mais nova do projeto no GitHub.
    Busca a última tag do repositório e compara com a versão atual.
    Retorna JSON com informações sobre atualizações disponíveis.
    """
    try:
        current_version = getattr(settings, 'VERSION', '1.0.0')
        
        # Cache por 1 hora para evitar muitas requisições ao GitHub
        cache_key = f'github_latest_version_{current_version}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return JsonResponse(cached_result)
        
        # URL da API do GitHub para buscar tags (ordenadas por data de criação)
        github_api_url = "https://api.github.com/repos/D3NKYT0/lineage/tags"
        
        # Fazer requisição ao GitHub
        response = requests.get(
            github_api_url,
            timeout=5,
            headers={'Accept': 'application/vnd.github.v3+json'},
            params={'per_page': 30, 'page': 1}  # Buscar as 30 primeiras tags
        )
        
        if response.status_code == 200:
            tags_data = response.json()
            
            if not tags_data or not isinstance(tags_data, list):
                # Se não houver tags, retornar sem atualização
                result = {
                    'has_update': False,
                    'current_version': current_version,
                    'latest_version': current_version,
                    'error': 'Nenhuma tag encontrada no repositório'
                }
                return JsonResponse(result)
            
            # Função para comparar versões (formato: X.Y.Z)
            def version_tuple(v):
                """Converte versão string para tuple para comparação"""
                try:
                    # Remove 'v' do início se existir
                    v = str(v).lstrip('vV')
                    # Extrai números da versão
                    parts = re.findall(r'\d+', v)
                    # Retorna tuple com até 3 números (major, minor, patch)
                    # Preenche com zeros se tiver menos de 3 partes
                    while len(parts) < 3:
                        parts.append('0')
                    return tuple(int(p) for p in parts[:3]) if parts else (0, 0, 0)
                except:
                    return (0, 0, 0)
            
            # Ordenar tags por versão (maior primeiro) para garantir que pegamos a mais recente
            # A API pode não retornar em ordem de versão, então ordenamos por versão numérica
            sorted_tags = sorted(
                tags_data,
                key=lambda tag: version_tuple(tag.get('name', '')),
                reverse=True
            )
            
            # Pegar a tag com maior versão
            latest_tag = sorted_tags[0]
            latest_version = latest_tag.get('name', '').lstrip('vV')
            
            # Comparar versões
            current_tuple = version_tuple(current_version)
            latest_tuple = version_tuple(latest_version)
            
            has_update = latest_tuple > current_tuple
            
            # Buscar informações do commit da tag para obter data e mensagem
            commit_url = latest_tag.get('commit', {}).get('url', '')
            commit_sha = latest_tag.get('commit', {}).get('sha', '')
            release_notes = ''
            published_at = ''
            
            if commit_url:
                try:
                    commit_response = requests.get(commit_url, timeout=3, headers={'Accept': 'application/vnd.github.v3+json'})
                    if commit_response.status_code == 200:
                        commit_data = commit_response.json()
                        published_at = commit_data.get('commit', {}).get('author', {}).get('date', '')
                        release_notes = commit_data.get('commit', {}).get('message', '')[:500]
                except:
                    pass  # Se falhar, continua sem as informações do commit
            
            # URL da tag no GitHub
            tag_name = latest_tag.get('name', '')
            # Tenta usar releases/tag primeiro, se não existir usa tree
            tag_url = f"https://github.com/D3NKYT0/lineage/releases/tag/{tag_name}"
            
            result = {
                'has_update': has_update,
                'current_version': current_version,
                'latest_version': latest_version if has_update else current_version,
                'release_url': tag_url,
                'release_notes': release_notes,
                'published_at': published_at,
                'tag_name': latest_tag.get('name', ''),
            }
            
            # Cachear resultado por 1 hora
            cache.set(cache_key, result, 3600)
            
            return JsonResponse(result)
        elif response.status_code == 404:
            # Repositório não encontrado ou sem acesso
            result = {
                'has_update': False,
                'current_version': current_version,
                'latest_version': current_version,
                'error': 'Repositório não encontrado ou sem acesso'
            }
            return JsonResponse(result)
        else:
            # Se não conseguir buscar, retornar sem atualização
            result = {
                'has_update': False,
                'current_version': current_version,
                'latest_version': current_version,
                'error': f'Não foi possível verificar atualizações (Status: {response.status_code})'
            }
            return JsonResponse(result)
            
    except requests.RequestException as e:
        logging.error(f"Erro ao verificar versão no GitHub: {str(e)}")
        result = {
            'has_update': False,
            'current_version': getattr(settings, 'VERSION', '1.0.0'),
            'latest_version': getattr(settings, 'VERSION', '1.0.0'),
            'error': 'Erro de conexão'
        }
        return JsonResponse(result)
    except Exception as e:
        logging.error(f"Erro inesperado ao verificar versão: {str(e)}")
        result = {
            'has_update': False,
            'current_version': getattr(settings, 'VERSION', '1.0.0'),
            'latest_version': getattr(settings, 'VERSION', '1.0.0'),
            'error': 'Erro inesperado'
        }
        return JsonResponse(result)
