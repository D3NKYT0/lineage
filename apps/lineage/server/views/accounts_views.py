from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.main.home.decorator import conditional_otp_required
from ..decorators import require_lineage_connection
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.timezone import now
from utils.resources import gen_avatar, get_class_name
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_POST
from apps.main.home.tasks import send_email_task
from apps.main.home.models import User, EmailOwnership
from apps.main.home.validators import validate_lineage_password
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.lineage.server.lineage_account_manager import LineageAccount
from apps.lineage.server.models import ManagedLineageAccount
from apps.lineage.server.services.account_context import (
    get_active_login,
    get_available_accounts,
    get_lineage_template_context,
    set_active_login,
    user_has_access,
)
from utils.dynamic_import import get_query_class
from django.utils.translation import gettext as _

signer = TimestampSigner()

# Importação dinâmica das classes E constantes do schema
LineageServices = get_query_class("LineageServices")
LineageClans = get_query_class("LineageClans")

# Importar constantes do schema (nomes reais das colunas do banco)
import importlib
import os
query_module_name = os.getenv('LINEAGE_QUERY_MODULE', 'default')
try:
    query_module = importlib.import_module(f'apps.lineage.server.querys.query_{query_module_name}')
except ModuleNotFoundError:
    # Fallback para query_default se não encontrar o módulo
    print(f"AVISO: query_{query_module_name} nao encontrado, usando query_default")
    query_module = importlib.import_module(f'apps.lineage.server.querys.query_default')

ACCESS_LEVEL = getattr(query_module, 'ACCESS_LEVEL', 'accesslevel')
CHAR_ID = getattr(query_module, 'CHAR_ID', 'charId')
BASE_CLASS_COL = getattr(query_module, 'BASE_CLASS_COL', 'classid')


@conditional_otp_required
@require_lineage_connection
def account_dashboard(request):
    import logging
    logger = logging.getLogger(__name__)
    active_login = get_active_login(request)
    account_data = LineageAccount.check_login_exists(active_login)

    if not account_data or len(account_data) == 0:
        if active_login == request.user.username:
            return redirect('server:lineage_register')
        messages.error(request, "Conta do Lineage não encontrada.")
        return redirect('server:manage_lineage_accounts')

    account = account_data[0]
    owner_uuid = account.get("linked_uuid")
    user_uuid = str(request.user.uuid)
    is_owner = owner_uuid == user_uuid

    if not owner_uuid:
        messages.warning(request, "Essa conta ainda não está vinculada a nenhum usuário do painel. Solicite ao proprietário para concluir o processo.")
        return redirect('server:manage_lineage_accounts')

    if not is_owner and not user_has_access(request.user, active_login):
        messages.error(request, "Você não tem permissão para visualizar essa conta.")
        return redirect('server:manage_lineage_accounts')

    try:
        personagens = LineageServices.find_chars(active_login)
    except Exception:
        personagens = []
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    # Verificar se a conta ATIVA possui algum clã em que é líder
    has_clan_leader_access = False
    leader_clans = []
    if LineageClans and active_login:
        try:
            # Apenas o login ativo importa aqui; um clã só pode ter um líder
            leader_clans = LineageClans.get_user_lead_clans([active_login]) or []
        except Exception:
            leader_clans = []

    has_clan_leader_access = bool(leader_clans)
    logger.info(
        "[account_dashboard] active_login=%s leader_clans_count=%s leader_clans=%s",
        active_login,
        len(leader_clans) if leader_clans else 0,
        leader_clans,
    )

    # ✅ Usar constante do schema ao invés de hardcoded
    account['status'] = "Ativa" if int(account.get(ACCESS_LEVEL, 0)) >= 0 else "Bloqueada"

    created_time = None
    if account.get('created_time'):
        try:
            created_time = make_aware(datetime.strptime(account['created_time'], '%Y-%m-%d %H:%M:%S'))
        except:
            try:
                created_time = make_aware(datetime.fromtimestamp(int(account['created_time'])))
            except:
                created_time = None

    # Mapeia IDs/Nomes de personagens líderes de clã para destacar no dashboard
    leader_ids = {str(c.get('leader_id')) for c in (leader_clans or []) if c.get('leader_id') is not None}
    leader_names = {str(c.get('leader_name')).strip().lower() for c in (leader_clans or []) if c.get('leader_name')}

    mock_lead_clans = request.session.get('mock_lead_clans', []) or []
    mock_leader_ids = {str(c.get('leader_id')) for c in mock_lead_clans if c.get('leader_id') is not None}
    mock_leader_names = {str(c.get('leader_name')).strip().lower() for c in mock_lead_clans if c.get('leader_name')}

    logger.info(
        "[account_dashboard] leader_ids=%s leader_names=%s mock_leader_ids=%s mock_leader_names=%s",
        sorted(list(leader_ids)),
        sorted(list(leader_names)),
        sorted(list(mock_leader_ids)),
        sorted(list(mock_leader_names)),
    )

    char_list = []
    for char in personagens:
        level = char.get('base_level', '-')
        obj_id = char.get('obj_id') or char.get('obj_Id') or char.get('charId') or char.get('char_id', '-')
        char_name = char.get('char_name') or char.get('charname', '-')
        base_class = char.get('base_class') or char.get('classid', 0)
        sex = char.get('sex', 0)

        obj_id_str = str(obj_id)
        name_key = str(char_name).strip().lower()
        is_clan_leader = (
            obj_id_str in leader_ids
            or obj_id_str in mock_leader_ids
            or name_key in leader_names
            or name_key in mock_leader_names
        )
        logger.info(
            "[account_dashboard] char_name=%s obj_id=%s is_clan_leader=%s",
            char_name,
            obj_id,
            is_clan_leader,
        )

        char_list.append({
            'id': obj_id,
            'nome': char_name,
            'title': char.get('title', '-'),
            'lastAccess': datetime.fromtimestamp(int(char['lastAccess']) / 1000).strftime('%B %d, %Y às %H:%M') if char.get('lastAccess') else '-',
            'online': 'Online' if char.get('online') else 'Offline',
            'base_class': get_class_name(base_class),
            'subclass1': get_class_name(char['subclass1']) if char.get('subclass1') else '-',
            'subclass2': get_class_name(char['subclass2']) if char.get('subclass2') else '-',
            'subclass3': get_class_name(char['subclass3']) if char.get('subclass3') else '-',
            'level': level,
            'sex': 'Feminino' if sex else 'Masculino',
            'pvp': char.get('pvpkills', 0),
            'pk': char.get('pkkills', 0),
            'karma': char.get('karma', 0),
            'clan': char.get('clan_name', '-'),
            'ally': char.get('ally_name', '-'),
            'nobless': 'Sim' if char.get('nobless') else 'Não',
            'hero': 'Sim' if char.get('hero_end') and int(char['hero_end']) > int(now().timestamp() * 1000) else 'Não',
            'avatar': gen_avatar(base_class, sex),
            'is_clan_leader': is_clan_leader,
        })

    context = {
        'account': account,
        'created_time': created_time.strftime('%B %d, %Y às %H:%M') if created_time else '-',
        'lastIP': account.get('lastIP', '-'),
        'characters': char_list,
        'char_count': len(char_list),
        'is_owner_account': is_owner,
        'has_clan_leader_access': has_clan_leader_access,
    }
    context.update(get_lineage_template_context(request))

    return render(request, 'l2_accounts/dashboard.html', context)


@conditional_otp_required
@require_lineage_connection
def update_password(request):
    import logging
    logger = logging.getLogger(__name__)
    
    # Usa a conta ativa selecionada pelo usuário
    active_login = get_active_login(request)
    user = request.user

    # Verifica se o usuário tem acesso à conta ativa
    if not user_has_access(request.user, active_login):
        messages.error(request, _("Você não tem permissão para alterar a senha desta conta."))
        return redirect('server:manage_lineage_accounts')

    # Verifica se a conta Lineage está vinculada
    account_data = LineageAccount.check_login_exists(active_login)
    if not account_data or len(account_data) == 0:
        messages.error(request, _("Conta do Lineage não encontrada."))
        return redirect('server:account_dashboard')
    
    account = account_data[0]
    linked_uuid = account.get("linked_uuid")
    
    if not linked_uuid:
        messages.error(request, _("Esta conta não está vinculada. Por favor, vincule sua conta antes de atualizar a senha."))
        return redirect('server:link_lineage_account')

    if request.method == "POST":
        senha = request.POST.get("nova_senha")
        confirmar = request.POST.get("confirmar_senha")

        if not senha or not confirmar:
            messages.error(request, _("Por favor, preencha todos os campos."))
            return redirect('server:update_password')

        if senha != confirmar:
            messages.error(request, _("As senhas não coincidem."))
            return redirect('server:update_password')

        logger.info(f"[update_password] Atualizando senha da conta {active_login} pelo usuário {user.username}")
        success = LineageAccount.update_password(senha, active_login)

        if success:
            messages.success(request, _("Senha da conta %(account)s atualizada com sucesso!") % {"account": active_login})
            logger.info(f"[update_password] Senha atualizada com sucesso para conta {active_login}")
            return redirect('server:account_dashboard')
        else:
            messages.error(request, _("Erro ao atualizar senha."))
            logger.error(f"[update_password] Erro ao atualizar senha para conta {active_login}")
            return redirect('server:update_password')

    # GET request — exibe o formulário
    return render(request, "l2_accounts/update_password.html", {
        'active_account_login': active_login,
    })


@conditional_otp_required
@require_lineage_connection
def register_lineage_account(request):
    user = request.user

    # Verifica se a conta já existe
    existing_account = LineageAccount.check_login_exists(user.username)
    if existing_account and len(existing_account) > 0:
        messages.info(request, "Sua conta Lineage já está criada.")
        return redirect('server:account_dashboard')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password != confirm:
            messages.error(request, "As senhas não coincidem.")
            return redirect('server:lineage_register')

        try:
            success = LineageAccount.register(
                login=user.username,
                password=password,
                access_level=0,
                email=user.email
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[register_lineage_account] Erro ao registrar conta no banco do Lineage: {e}", exc_info=True)
            messages.error(request, "Erro ao criar conta. O banco de dados do Lineage pode estar indisponível.")
            return redirect('server:lineage_register')

        if success:
            # Verifica se o email tem uma conta mestre verificada
            user_email = request.user.email
            user_login = request.user.username
            master_user = None
            master_uuid = None
            
            if user_email and request.user.is_email_verified:
                try:
                    from apps.main.home.models import EmailOwnership
                    email_ownership = EmailOwnership.objects.filter(email=user_email).first()
                    
                    if email_ownership:
                        master_user = email_ownership.owner
                        master_uuid = str(master_user.uuid) if hasattr(master_user, 'uuid') else None
                        
                        # Se o usuário atual não é o mestre, vincula ao mestre
                        if master_user != request.user and master_uuid:
                            # Verifica limite de slots antes de vincular
                            from apps.lineage.server.services.account_context import can_link_account
                            can_link, error_message = can_link_account(master_user)
                            
                            if not can_link:
                                import logging
                                logger = logging.getLogger(__name__)
                                logger.warning(f"[register_lineage_account] Limite de slots atingido para {master_user.username}: {error_message}")
                                messages.warning(
                                    request,
                                    f"⚠️ Conta criada, mas não foi possível vincular automaticamente. {error_message}"
                                )
                                return redirect('server:register_success')
                            
                            # Vincula ao UUID da conta mestre
                            user_uuid = master_uuid
                        else:
                            # Usuário é o mestre ou não tem mestre, vincula ao próprio UUID
                            user_uuid = str(request.user.uuid)
                    else:
                        # Não tem conta mestre, vincula ao próprio UUID
                        user_uuid = str(request.user.uuid)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"[register_lineage_account] Erro ao verificar conta mestre no registro: {e}", exc_info=True)
                    # Em caso de erro, vincula ao próprio UUID
                    user_uuid = str(request.user.uuid)
            else:
                # Email não verificado ou não tem email, vincula ao próprio UUID
                user_uuid = str(request.user.uuid)
            
            # Vincula automaticamente a conta após o registro
            try:
                success_link = LineageAccount.link_account_to_user(user_login, user_uuid)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"[register_lineage_account] Erro ao vincular conta no banco do Lineage: {e}", exc_info=True)
                messages.warning(
                    request,
                    "Conta criada com sucesso, mas houve um problema ao vincular automaticamente. Você pode vincular manualmente depois."
                )
                return redirect('server:register_success')

            if success_link and success_link is not None:
                if master_user and master_user != request.user:
                    messages.success(
                        request,
                        f"Conta Lineage criada e vinculada automaticamente à conta mestre {master_user.username}!"
                    )
                else:
                    messages.success(request, "Conta Lineage criada e vinculada com sucesso!")
                return redirect('server:register_success')
            else:
                messages.warning(
                    request,
                    "Conta criada com sucesso, mas houve um problema ao vincular automaticamente. Você pode vincular manualmente depois."
                )
                return redirect('server:register_success')
        else:
            messages.error(request, "Erro ao criar conta. O banco de dados do Lineage pode estar indisponível.")
            return redirect('server:lineage_register')

    return render(request, 'l2_accounts/register.html', {
        'login': user.username,
        'email': user.email
    })


@conditional_otp_required
@require_lineage_connection
def register_success(request):
    return render(request, 'l2_accounts/register_success.html')


@conditional_otp_required
@require_lineage_connection
def link_lineage_account(request):
    import random
    import logging
    logger = logging.getLogger(__name__)
    
    # Verifica se é uma solicitação de código por email
    if request.method == "POST" and request.POST.get("action") == "request_code":
        if not request.user.email:
            messages.error(request, _("Você precisa ter um e-mail cadastrado para receber o código."))
            return redirect("server:link_lineage_account")
        
        # Gera código de 6 dígitos
        verification_code = str(random.randint(100000, 999999))
        
        # Armazena na sessão com timestamp (expira em 10 minutos)
        from django.utils import timezone
        request.session['link_account_code'] = verification_code
        request.session['link_account_code_time'] = timezone.now().timestamp()
        request.session['link_account_email'] = request.user.email
        request.session.modified = True
        
        # Envia email com o código
        try:
            send_email_task.delay(
                _("Código de Verificação - Vincular Conta Lineage"),
                _("""Olá {username},

Você solicitou um código para vincular sua conta do Lineage 2.

Seu código de verificação é: {code}

Este código é válido por 10 minutos.

Se você não solicitou este código, ignore este e-mail.

Atenciosamente,
Equipe PDL""").format(username=request.user.username, code=verification_code),
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email]
            )
            messages.success(request, _("Código de verificação enviado para %(email)s") % {"email": request.user.email})
            logger.info(f"[link_lineage_account] Código enviado para {request.user.email}")
        except Exception as e:
            logger.error(f"[link_lineage_account] Erro ao enviar email: {e}", exc_info=True)
            messages.error(request, _("Erro ao enviar e-mail. Tente novamente."))
        
        return redirect("server:link_lineage_account")
    
    # Processa vinculação com código E senha (ambos obrigatórios se código foi solicitado)
    if request.method == "POST" and request.POST.get("action") == "link":
        login_jogo = request.user.username
        senha_jogo = request.POST.get("senha", "").strip()
        verification_code = request.POST.get("verification_code", "").strip()
        
        # Verifica se há código pendente na sessão
        has_pending_code = bool(request.session.get('link_account_code'))
        
        # Se há código pendente, ambos são obrigatórios
        if has_pending_code:
            if not verification_code:
                messages.error(request, _("Informe o código de verificação enviado por e-mail."))
                return redirect("server:link_lineage_account")
            
            if not senha_jogo:
                messages.error(request, _("Informe a senha da conta."))
                return redirect("server:link_lineage_account")
            
            # Valida o código
            stored_code = request.session.get('link_account_code')
            code_time = request.session.get('link_account_code_time')
            stored_email = request.session.get('link_account_email')
            
            # Verifica se o código existe e não expirou (10 minutos)
            from django.utils import timezone
            if not stored_code or not code_time:
                messages.error(request, _("Código não encontrado. Solicite um novo código."))
                return redirect("server:link_lineage_account")
            
            if timezone.now().timestamp() - code_time > 600:  # 10 minutos
                messages.error(request, _("Código expirado. Solicite um novo código."))
                # Limpa a sessão
                request.session.pop('link_account_code', None)
                request.session.pop('link_account_code_time', None)
                request.session.pop('link_account_email', None)
                return redirect("server:link_lineage_account")
            
            if stored_code != verification_code:
                messages.error(request, _("Código inválido. Verifique e tente novamente."))
                return redirect("server:link_lineage_account")
            
            if stored_email != request.user.email:
                messages.error(request, _("O código foi enviado para outro e-mail."))
                return redirect("server:link_lineage_account")
            
            logger.info(f"[link_lineage_account] Código válido para {request.user.username}")
        
        # Valida senha (sempre obrigatória)
        if not senha_jogo:
            messages.error(request, _("Informe a senha da conta."))
            return redirect("server:link_lineage_account")
        
        try:
            is_valided = LineageAccount.validate_credentials(login_jogo, senha_jogo)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[link_lineage_account] Erro ao validar credenciais no banco do Lineage: {e}", exc_info=True)
            messages.error(request, _("Erro ao validar credenciais. O banco de dados do Lineage pode estar indisponível."))
            return redirect("server:link_lineage_account")
        
        if not is_valided:
            messages.error(request, _("Login ou senha incorretos."))
            return redirect("server:link_lineage_account")
        
        try:
            conta = LineageAccount.get_account_by_login(login_jogo)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[link_lineage_account] Erro ao buscar conta no banco do Lineage: {e}", exc_info=True)
            messages.error(request, _("Erro ao buscar conta. O banco de dados do Lineage pode estar indisponível."))
            return redirect("server:link_lineage_account")

        if not conta:
            messages.error(request, _("Conta não encontrada."))
            return redirect("server:link_lineage_account")

        # Já está vinculada?
        if conta.get("linked_uuid"):
            messages.warning(request, _("Essa conta já está vinculada a outro usuário."))
            return redirect("server:link_lineage_account")

        # Verifica limite de slots antes de vincular
        from apps.lineage.server.services.account_context import can_link_account
        can_link, error_message = can_link_account(request.user)
        if not can_link:
            messages.error(request, error_message)
            return redirect("server:link_lineage_account")

        # Vincula a conta
        user_uuid = str(request.user.uuid)
        try:
            success = LineageAccount.link_account_to_user(login_jogo, user_uuid)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[link_lineage_account] Erro ao vincular conta no banco do Lineage: {e}", exc_info=True)
            messages.error(request, _("Erro ao vincular conta. O banco de dados do Lineage pode estar indisponível."))
            return redirect("server:link_lineage_account")
        
        # Atualiza também o email na conta
        if success and request.user.email:
            try:
                from utils.dynamic_import import get_query_class
                LineageDBClass = get_query_class("LineageDB")
                if LineageDBClass:
                    lineage_db = LineageDBClass()
                    if lineage_db and getattr(lineage_db, 'enabled', False):
                        sql = """
                            UPDATE accounts
                            SET email = :email
                            WHERE login = :login
                        """
                        params = {
                            "email": request.user.email,
                            "login": login_jogo
                        }
                        lineage_db.update(sql, params)
            except Exception as e:
                logger.warning(f"Erro ao atualizar email na conta: {e}")

        if success:
            # Limpa o código da sessão se foi usado
            if verification_code:
                request.session.pop('link_account_code', None)
                request.session.pop('link_account_code_time', None)
                request.session.pop('link_account_email', None)
            
            messages.success(request, _("Conta vinculada com sucesso!"))
            return redirect("server:account_dashboard")
        else:
            messages.error(request, _("Erro ao vincular conta."))
            return redirect("server:link_lineage_account")

    # Verifica se há código pendente na sessão
    has_pending_code = bool(request.session.get('link_account_code'))
    code_email = request.session.get('link_account_email')
    
    return render(request, "l2_accounts/vincular_conta.html", {
        'has_pending_code': has_pending_code,
        'code_email': code_email,
    })


@conditional_otp_required
@require_lineage_connection
def request_link_by_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            messages.error(request, "Informe um e-mail.")
            return redirect("server:request_link_by_email")

        # Verifica se existe uma conta com esse email e ainda não vinculada
        contas = LineageAccount.find_accounts_by_email(email)
        conta = next((c for c in contas if not c.get("linked_uuid")), None)

        if not conta:
            messages.error(request, "Nenhuma conta não vinculada foi encontrada com esse e-mail.")
            return redirect("server:request_link_by_email")

        # Cria token assinado
        data = f"{conta['login']}|{email}"
        token = signer.sign(data)

        link = request.build_absolute_uri(
            reverse("server:link_by_email_token", args=[token])
        )

        # Envia e-mail
        send_email_task.delay(
            "Vinculação de Conta Lineage",
            f"Clique no link abaixo para vincular sua conta:\n\n{link}\n\nO link expira em 1 hora.",
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )

        messages.success(request, "Um link de verificação foi enviado para o seu e-mail.")
        return redirect("server:request_link_by_email")

    return render(request, "l2_accounts/link_by_email_request.html")


@conditional_otp_required
@require_lineage_connection
def link_by_email_token(request, token):
    try:
        data = signer.unsign(token, max_age=3600)  # 1 hora
        login, email = data.split('|')
    except SignatureExpired:
        messages.error(request, "Este link expirou. Solicite um novo.")
        return redirect("server:request_link_by_email")
    except BadSignature:
        messages.error(request, "Token inválido.")
        return redirect("server:request_link_by_email")

    try:
        conta = LineageAccount.get_account_by_login_and_email(login, email)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[link_by_email_token] Erro ao buscar conta no banco do Lineage: {e}", exc_info=True)
        messages.error(request, "Erro ao buscar conta. O banco de dados do Lineage pode estar indisponível.")
        return redirect("server:link_lineage_account")
    
    if not conta or conta.get("linked_uuid"):
        messages.error(request, "Conta inválida ou já vinculada.")
        return redirect("server:link_lineage_account")
    
    # Verifica limite de slots antes de vincular
    from apps.lineage.server.services.account_context import can_link_account
    can_link, error_message = can_link_account(request.user)
    if not can_link:
        messages.error(request, error_message)
        return redirect("server:link_lineage_account")
    
    try:
        success = LineageAccount.link_account_to_user(login, str(request.user.uuid))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[link_by_email_token] Erro ao vincular conta no banco do Lineage: {e}", exc_info=True)
        messages.error(request, "Erro ao vincular conta. O banco de dados do Lineage pode estar indisponível.")
        return redirect("server:link_lineage_account")
    
    if success and success is not None:
        messages.success(request, "Conta vinculada com sucesso!")
        return redirect("server:account_dashboard")
    else:
        messages.error(request, "Erro ao vincular a conta.")
        return redirect("server:link_lineage_account")


@conditional_otp_required
@require_lineage_connection
def manage_lineage_accounts(request):
    from utils.dynamic_import import get_query_class
    LineageAccount = get_query_class("LineageAccount")
    
    # Contas delegadas pelo usuário atual (delegações explícitas)
    delegated_links = ManagedLineageAccount.objects.filter(
        created_by=request.user
    ).select_related("manager_user").order_by("account_login")

    # Contas delegadas para o usuário atual (delegações explícitas)
    links_as_manager = ManagedLineageAccount.objects.filter(
        manager_user=request.user,
        status=ManagedLineageAccount.Status.ACTIVE,
    ).select_related("created_by").order_by("account_login")

    # Busca contas vinculadas automaticamente (via linked_uuid ou e-mail)
    # que não estão em ManagedLineageAccount
    linked_accounts_info = []
    available_accounts = get_available_accounts(request.user)
    
    # Lista de logins que já estão em links_as_manager para evitar duplicatas
    delegated_logins = {link.account_login for link in links_as_manager}
    
    for account in available_accounts:
        # Se a conta não é a principal e não tem created_by (não foi delegada explicitamente)
        if not account.get("is_primary") and not account.get("created_by"):
            login = account.get("login")
            role_label = account.get("role_label", "")
            
            # Verifica se a conta realmente está vinculada (tem linked_uuid)
            # Usa SQL direto para evitar cache
            if login:
                try:
                    from utils.dynamic_import import get_query_class
                    LineageDBClass = get_query_class("LineageDB")
                    
                    if LineageDBClass:
                        lineage_db = LineageDBClass()
                        if lineage_db and getattr(lineage_db, 'enabled', False):
                            sql = """
                                SELECT login, linked_uuid, email
                                FROM accounts
                                WHERE login = :login
                                LIMIT 1
                            """
                            result = lineage_db.select(sql, {"login": login})
                            if result and len(result) > 0:
                                conta = result[0]
                                linked_uuid = conta.get("linked_uuid") if isinstance(conta, dict) else getattr(conta, 'linked_uuid', None)
                                
                                # Se não tem linked_uuid, não adiciona (foi desvinculada)
                                if not linked_uuid:
                                    continue
                            else:
                                # Conta não encontrada no banco
                                continue
                    else:
                        # Fallback: usa check_login_exists se LineageDB não estiver disponível
                        if LineageAccount:
                            conta_data = LineageAccount.check_login_exists(login)
                            if conta_data and len(conta_data) > 0:
                                conta = conta_data[0]
                                linked_uuid = conta.get("linked_uuid") if isinstance(conta, dict) else getattr(conta, 'linked_uuid', None)
                                if not linked_uuid:
                                    continue
                            else:
                                continue
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Erro ao verificar linked_uuid da conta {login}: {e}")
                    continue
            
            # Verifica se já existe um ManagedLineageAccount para esta conta
            existing_link = ManagedLineageAccount.objects.filter(
                account_login=login,
                created_by=request.user
            ).first()
            
            # Se não existe delegação explícita e não está na lista de delegadas, adiciona
            if not existing_link and login and login not in delegated_logins:
                linked_accounts_info.append({
                    "account_login": login,
                    "role_label": role_label,
                    "is_linked": True,  # Marca como vinculada automaticamente
                })

    # Verifica se a conta principal do usuário está realmente vinculada
    # Se não estiver vinculada, não deve mostrar mensagem de conta mestre
    # Usa SQL direto para evitar cache
    account_is_linked = False
    if request.user.username:
        try:
            from utils.dynamic_import import get_query_class
            LineageDBClass = get_query_class("LineageDB")
            
            if LineageDBClass:
                lineage_db = LineageDBClass()
                if lineage_db and getattr(lineage_db, 'enabled', False):
                    sql = """
                        SELECT login, linked_uuid, email
                        FROM accounts
                        WHERE login = :login
                        LIMIT 1
                    """
                    result = lineage_db.select(sql, {"login": request.user.username})
                    if result and len(result) > 0:
                        conta = result[0]
                        linked_uuid = conta.get("linked_uuid") if isinstance(conta, dict) else getattr(conta, 'linked_uuid', None)
                        account_is_linked = bool(linked_uuid)
            else:
                # Fallback: usa check_login_exists se LineageDB não estiver disponível
                if LineageAccount:
                    conta_data = LineageAccount.check_login_exists(request.user.username)
                    if conta_data and len(conta_data) > 0:
                        conta = conta_data[0]
                        linked_uuid = conta.get("linked_uuid") if isinstance(conta, dict) else getattr(conta, 'linked_uuid', None)
                        account_is_linked = bool(linked_uuid)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao verificar se conta principal está vinculada: {e}")
    
    context = get_lineage_template_context(request)
    
    # Guarda o email_master_owner original antes de limpar (para mostrar mensagem de desvinculação)
    original_email_master_owner = context.get('email_master_owner')
    
    # Se a conta não está vinculada, não mostra informações de conta mestre
    # mas mantém a referência para mostrar mensagem de desvinculação
    if not account_is_linked:
        context['is_email_master_owner'] = True
        # Não limpa email_master_owner, apenas marca que não está vinculada
    
    # Busca contas que o usuário pode delegar (apenas as que ele é proprietário)
    from apps.lineage.server.services.account_context import get_ownable_accounts
    ownable_accounts, primary_excluded = get_ownable_accounts(request.user)
    
    context.update(
        {
            "delegated_links": delegated_links,
            "links_as_manager": links_as_manager,
            "linked_accounts_info": linked_accounts_info,  # Contas vinculadas automaticamente
            "total_delegated_accounts": len(links_as_manager) + len(linked_accounts_info),
            "account_is_linked": account_is_linked,  # Flag para verificar se conta está vinculada
            "original_email_master_owner": original_email_master_owner,  # Para mostrar mensagem de desvinculação
            "ownable_lineage_accounts": ownable_accounts,  # Contas que o usuário pode delegar
            "primary_account_excluded": primary_excluded,  # Flag indicando se conta principal foi excluída
        }
    )
    return render(request, "l2_accounts/manage_accounts.html", context)


@conditional_otp_required
@require_lineage_connection
@require_POST
def add_contra_mestre(request):
    if not request.user.is_email_master_owner:
        owner = request.user.get_email_master_owner()
        if owner and owner != request.user:
            messages.error(
                request,
                _("Somente a conta mestre %(owner)s pode delegar acessos com este e-mail.") % {"owner": owner.username},
            )
        else:
            messages.error(request, _("Você não tem permissão para delegar acessos."))
        return redirect("server:manage_lineage_accounts")

    account_login = (request.POST.get("account_login") or "").strip()
    manager_username = (request.POST.get("manager_username") or "").strip()
    notes = (request.POST.get("notes") or "").strip()

    if not account_login or not manager_username:
        messages.error(request, "Informe o login da conta e o usuário do contra mestre.")
        return redirect("server:manage_lineage_accounts")

    if manager_username == request.user.username:
        messages.error(request, "Informe o usuário do contra mestre, não o seu.")
        return redirect("server:manage_lineage_accounts")

    try:
        manager_user = User.objects.get(username=manager_username)
    except User.DoesNotExist:
        messages.error(request, "Usuário informado não foi encontrado.")
        return redirect("server:manage_lineage_accounts")

    conta = LineageAccount.get_account_by_login(account_login)
    if not conta:
        messages.error(request, "Conta do Lineage não encontrada.")
        return redirect("server:manage_lineage_accounts")

    if conta.get("linked_uuid") != str(request.user.uuid):
        messages.error(request, "Apenas o proprietário da conta pode delegar contra mestres.")
        return redirect("server:manage_lineage_accounts")

    link, created = ManagedLineageAccount.objects.update_or_create(
        account_login=account_login,
        manager_user=manager_user,
        defaults={
            "created_by": request.user,
            "role": ManagedLineageAccount.Role.CONTRA_MESTRE,
            "status": ManagedLineageAccount.Status.ACTIVE,
            "notes": notes,
        },
    )

    if created:
        messages.success(request, f"Usuário {manager_username} agora pode gerenciar a conta {account_login}.")
    else:
        messages.success(request, f"Permissões de {manager_username} atualizadas para a conta {account_login}.")

    return redirect("server:manage_lineage_accounts")


@conditional_otp_required
@require_lineage_connection
@require_POST
def remove_contra_mestre(request, link_id):
    link = get_object_or_404(ManagedLineageAccount, pk=link_id)
    if not request.user.is_email_master_owner:
        owner = request.user.get_email_master_owner()
        if owner and owner != request.user:
            messages.error(
                request,
                _("Somente a conta mestre %(owner)s pode revogar acessos com este e-mail.") % {"owner": owner.username},
            )
        else:
            messages.error(request, _("Você não tem permissão para revogar acessos."))
        return redirect("server:manage_lineage_accounts")

    is_owner = False
    conta = LineageAccount.get_account_by_login(link.account_login)
    if conta and conta.get("linked_uuid") == str(request.user.uuid):
        is_owner = True

    if not (link.created_by == request.user or is_owner or request.user.is_superuser):
        messages.error(request, "Você não pode remover este contra mestre.")
        return redirect("server:manage_lineage_accounts")

    link.delete()
    messages.success(request, "Contra mestre removido com sucesso.")
    return redirect("server:manage_lineage_accounts")


@conditional_otp_required
def purchase_link_slot(request):
    """
    View para comprar slots de vinculação de contas.
    """
    from decimal import Decimal
    from django.db import transaction
    from apps.lineage.wallet.models import Wallet
    from apps.lineage.wallet.signals import aplicar_transacao
    from apps.lineage.server.models import AccountLinkSlot
    from apps.lineage.server.services.account_context import get_total_link_slots, get_used_link_slots
    
    # Preço padrão de um slot (pode ser configurável depois)
    SLOT_PRICE = Decimal('10.00')  # R$ 10,00 por slot
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            messages.error(request, "Quantidade inválida.")
            return redirect('server:purchase_link_slot')
        
        if quantity > 10:
            messages.error(request, "Você pode comprar no máximo 10 slots por vez.")
            return redirect('server:purchase_link_slot')
        
        total_price = SLOT_PRICE * quantity
        
        # Processa a compra
        try:
            with transaction.atomic():
                # Verifica saldo na carteira (dentro da transação para evitar race conditions)
                try:
                    wallet = Wallet.objects.select_for_update().get(usuario=request.user)
                except Wallet.DoesNotExist:
                    messages.error(request, "Você não possui uma carteira. Entre em contato com o suporte.")
                    return redirect('server:purchase_link_slot')
                
                if wallet.saldo < total_price:
                    messages.error(
                        request,
                        f"Saldo insuficiente. Você precisa de R$ {total_price:.2f} mas tem apenas R$ {wallet.saldo:.2f}."
                    )
                    return redirect('server:purchase_link_slot')
                
                # Debita da carteira
                aplicar_transacao(
                    wallet=wallet,
                    tipo='SAIDA',
                    valor=total_price,
                    descricao=f"Compra de {quantity} slot(s) de vinculação de contas",
                    origem="Sistema de Slots",
                    destino=request.user.username
                )
                
                # Cria o registro de slots comprados
                AccountLinkSlot.objects.create(
                    user=request.user,
                    slots_purchased=quantity,
                    purchase_price=total_price,
                    notes=f"Compra de {quantity} slot(s) de vinculação"
                )
                
                messages.success(
                    request,
                    f"✅ {quantity} slot(s) de vinculação comprado(s) com sucesso! Você agora pode vincular mais contas."
                )
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao comprar slots: {e}", exc_info=True)
            messages.error(request, "Erro ao processar a compra. Tente novamente.")
        
        return redirect('server:purchase_link_slot')
    
    # GET - mostra a página de compra
    try:
        wallet = Wallet.objects.get(usuario=request.user)
    except Wallet.DoesNotExist:
        wallet = None
    
    total_slots = get_total_link_slots(request.user)
    used_slots = get_used_link_slots(request.user)
    available_slots = total_slots - used_slots
    
    # Calcula preços para diferentes quantidades
    prices = {
        1: SLOT_PRICE,
        2: SLOT_PRICE * 2,
        3: SLOT_PRICE * 3,
        5: SLOT_PRICE * 5,
        10: SLOT_PRICE * 10,
    }
    
    # Busca histórico de compras
    purchase_history = AccountLinkSlot.objects.filter(user=request.user).order_by('-purchase_date')[:10]
    
    context = {
        'slot_price': SLOT_PRICE,
        'prices': prices,
        'wallet': wallet,
        'total_slots': total_slots,
        'used_slots': used_slots,
        'available_slots': available_slots,
        'purchase_history': purchase_history,
    }
    
    return render(request, 'l2_accounts/purchase_link_slot.html', context)


@conditional_otp_required
@require_lineage_connection
@require_POST
def set_active_lineage_account(request):
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("server:account_dashboard")
    account_login = (request.POST.get("account_login") or "").strip()

    if not account_login:
        messages.error(request, "Selecione uma conta válida.")
        return redirect(next_url)

    try:
        set_active_login(request, account_login)
        messages.success(request, f"Conta {account_login} definida como ativa.")
    except PermissionError:
        messages.error(request, "Você não tem permissão para usar essa conta.")

    return redirect(next_url)


@conditional_otp_required
@require_lineage_connection
@require_POST
def unlink_lineage_account(request):
    """
    Desvincula uma conta do Lineage do UUID do usuário atual.
    Remove apenas o linked_uuid da conta no banco do jogo (o email não é alterado).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    account_login = (request.POST.get("account_login") or "").strip()
    
    if not account_login:
        messages.error(request, _("Informe o login da conta para desvincular."))
        return redirect("server:manage_lineage_accounts")
    
    # Verifica se o usuário tem acesso a esta conta
    if not user_has_access(request.user, account_login):
        messages.error(request, _("Você não tem permissão para desvincular esta conta."))
        return redirect("server:manage_lineage_accounts")
    
    # Não permite desvincular a conta principal (username)
    if account_login == request.user.username:
        messages.error(request, _("Você não pode desvincular sua conta principal."))
        return redirect("server:manage_lineage_accounts")
    
    try:
        from utils.dynamic_import import get_query_class
        LineageAccount = get_query_class("LineageAccount")
        
        if not LineageAccount or not hasattr(LineageAccount, 'unlink_account_from_user'):
            messages.error(request, _("Funcionalidade de desvinculação não disponível."))
            return redirect("server:manage_lineage_accounts")
        
        # Verifica se o usuário é o mestre do email
        email_master_owner = None
        if request.user.email:
            email_master_owner = request.user.get_email_master_owner()
        
        # Determina qual UUID usar para desvincular
        # Se for o mestre do email, usa o UUID do mestre
        # Se não for, usa o UUID do usuário atual
        if email_master_owner and email_master_owner != request.user:
            # Usuário não é o mestre, mas pode ter acesso via delegação
            # Verifica se a conta está vinculada ao UUID do mestre
            master_uuid = str(email_master_owner.uuid) if hasattr(email_master_owner, 'uuid') else None
            user_uuid = str(request.user.uuid) if hasattr(request.user, 'uuid') else None
            
            if not master_uuid:
                messages.error(request, _("UUID do usuário mestre não encontrado."))
                return redirect("server:manage_lineage_accounts")
            
            # Verifica se a conta está vinculada ao UUID do mestre
            account_data = LineageAccount.check_login_exists(account_login)
            if not account_data or len(account_data) == 0:
                messages.error(request, _("Conta do Lineage não encontrada."))
                logger.warning(f"[unlink_lineage_account] Conta {account_login} não encontrada no banco")
                return redirect("server:manage_lineage_accounts")
            
            account = account_data[0]
            current_linked_uuid = account.get("linked_uuid")
            
            if not current_linked_uuid:
                messages.error(request, _("Esta conta não está vinculada a nenhum usuário."))
                logger.warning(f"[unlink_lineage_account] Conta {account_login} não está vinculada (linked_uuid é None)")
                return redirect("server:manage_lineage_accounts")
            
            current_linked_uuid_str = str(current_linked_uuid).strip()
            master_uuid_str = str(master_uuid).strip()
            
            # Se a conta está vinculada ao mestre, usa o UUID do mestre para desvincular
            if current_linked_uuid_str == master_uuid_str:
                user_uuid = master_uuid
                logger.info(f"[unlink_lineage_account] Usuário não é mestre, mas conta está vinculada ao mestre. Usando UUID do mestre: {user_uuid}")
            elif user_uuid and current_linked_uuid_str == str(user_uuid).strip():
                # Conta está vinculada ao UUID do usuário atual (não mestre)
                logger.info(f"[unlink_lineage_account] Conta vinculada ao UUID do usuário atual (não mestre): {user_uuid}")
            else:
                messages.error(request, _("Esta conta está vinculada a outro usuário."))
                logger.warning(f"[unlink_lineage_account] Conta {account_login} está vinculada a outro UUID: {current_linked_uuid_str}")
                return redirect("server:manage_lineage_accounts")
        else:
            # Usuário é o mestre ou não tem mestre definido, usa o UUID do usuário atual
            user_uuid = str(request.user.uuid) if hasattr(request.user, 'uuid') else None
            if not user_uuid:
                messages.error(request, _("UUID do usuário não encontrado."))
                return redirect("server:manage_lineage_accounts")
            
            logger.info(f"[unlink_lineage_account] Usuário é mestre ou não tem mestre. Usando UUID do usuário atual: {user_uuid}")
            
            # Verifica se a conta realmente está vinculada ao UUID do usuário antes de tentar desvincular
            account_data = LineageAccount.check_login_exists(account_login)
            if not account_data or len(account_data) == 0:
                messages.error(request, _("Conta do Lineage não encontrada."))
                logger.warning(f"[unlink_lineage_account] Conta {account_login} não encontrada no banco")
                return redirect("server:manage_lineage_accounts")
            
            account = account_data[0]
            current_linked_uuid = account.get("linked_uuid")
            
            logger.info(f"[unlink_lineage_account] Conta {account_login} - linked_uuid atual: {current_linked_uuid}, user_uuid: {user_uuid}")
            
            # Verifica se a conta está vinculada ao UUID do usuário
            if not current_linked_uuid:
                messages.error(request, _("Esta conta não está vinculada a nenhum usuário."))
                logger.warning(f"[unlink_lineage_account] Conta {account_login} não está vinculada (linked_uuid é None)")
                return redirect("server:manage_lineage_accounts")
            
            # Normaliza os UUIDs para comparação (remove espaços, converte para string)
            current_linked_uuid_str = str(current_linked_uuid).strip()
            user_uuid_str = str(user_uuid).strip()
            
            if current_linked_uuid_str != user_uuid_str:
                messages.error(request, _("Esta conta está vinculada a outro usuário (UUID: %(uuid)s).") % {"uuid": current_linked_uuid_str})
                logger.warning(f"[unlink_lineage_account] Conta {account_login} está vinculada a outro UUID: {current_linked_uuid_str} != {user_uuid_str}")
                return redirect("server:manage_lineage_accounts")
        
        logger.info(f"[unlink_lineage_account] Desvinculando conta {account_login} do UUID {user_uuid}")
        
        # Verifica se a conta que está sendo desvinculada é a conta ativa
        active_login = get_active_login(request)
        was_active = (active_login == account_login)
        
        success = LineageAccount.unlink_account_from_user(account_login, user_uuid)
        
        if success:
            # Se a conta desvinculada era a ativa, redefine para a conta principal ANTES de qualquer outra coisa
            if was_active:
                logger.info(f"[unlink_lineage_account] Conta ativa {account_login} foi desvinculada, redefinindo para conta principal")
                set_active_login(request, request.user.username)
                messages.warning(
                    request, 
                    _("Conta %(account)s desvinculada com sucesso. Como ela estava ativa, a conta principal foi definida como ativa.") % {"account": account_login}
                )
            else:
                messages.success(request, _("Conta %(account)s desvinculada com sucesso.") % {"account": account_login})
            
            logger.info(f"[unlink_lineage_account] Conta {account_login} desvinculada com sucesso")
        else:
            messages.error(request, _("Não foi possível desvincular a conta. Verifique se ela está vinculada ao seu usuário."))
            logger.warning(f"[unlink_lineage_account] Falha ao desvincular conta {account_login}")
            
    except Exception as e:
        logger.error(f"[unlink_lineage_account] Erro ao desvincular conta: {e}", exc_info=True)
        messages.error(request, _("Erro ao desvincular a conta: %(error)s") % {"error": str(e)})
    
    return redirect("server:manage_lineage_accounts")


@conditional_otp_required
@require_lineage_connection
def create_master_account(request):
    """
    Cria uma nova conta no portal (PDL) e no Lineage (L2) e vincula automaticamente à conta mestre.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Verifica se o usuário é mestre do email
    user_email = request.user.email
    if not user_email or not request.user.is_email_verified:
        messages.error(request, "Você precisa ter um email verificado para criar contas vinculadas.")
        return redirect('server:account_dashboard')
    
    # Verifica se é mestre do email
    email_ownership = EmailOwnership.objects.filter(email=user_email).first()
    if not email_ownership or email_ownership.owner != request.user:
        messages.error(request, "Apenas a conta mestre do email pode criar novas contas vinculadas.")
        return redirect('server:account_dashboard')
    
    master_user = request.user
    master_uuid = str(master_user.uuid) if hasattr(master_user, 'uuid') else None
    
    if not master_uuid:
        messages.error(request, "Erro ao obter UUID da conta mestre.")
        return redirect('server:account_dashboard')
    
    # Verifica limite de slots antes de criar
    from apps.lineage.server.services.account_context import can_link_account
    can_link, error_message = can_link_account(master_user)
    if not can_link:
        messages.error(request, error_message)
        return redirect('server:account_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password_pdl = request.POST.get('password_pdl', '')
        confirm_password_pdl = request.POST.get('confirm_password_pdl', '')
        password_l2 = request.POST.get('password_l2', '')
        confirm_password_l2 = request.POST.get('confirm_password_l2', '')
        
        # Validações
        if not username:
            messages.error(request, "O nome de usuário é obrigatório.")
            return redirect('server:create_master_account')
        
        if len(username) < 3 or len(username) > 16:
            messages.error(request, "O nome de usuário deve ter entre 3 e 16 caracteres.")
            return redirect('server:create_master_account')
        
        # Validações senha PDL usando validadores do Django
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        if not password_pdl:
            messages.error(request, "A senha do portal (PDL) é obrigatória.")
            return redirect('server:create_master_account')
        
        # Valida senha PDL usando os validadores configurados em AUTH_PASSWORD_VALIDATORS
        try:
            # Cria um usuário temporário para validação (UserAttributeSimilarityValidator precisa)
            temp_user = User(username=username, email=user_email)
            validate_password(password_pdl, user=temp_user)
        except ValidationError as e:
            error_messages = e.messages if hasattr(e, 'messages') else [str(e)]
            for error_msg in error_messages:
                messages.error(request, f"Senha do portal (PDL): {error_msg}")
            return redirect('server:create_master_account')
        
        if password_pdl != confirm_password_pdl:
            messages.error(request, "As senhas do portal (PDL) não coincidem.")
            return redirect('server:create_master_account')
        
        # Validações senha L2
        if not password_l2:
            messages.error(request, "A senha do jogo (L2) é obrigatória.")
            return redirect('server:create_master_account')
        
        # Valida formato da senha L2 (apenas letras e números, mínimo 6 caracteres)
        # Mesma regra apresentada na tela oficial de registro do Lineage
        try:
            validate_lineage_password(password_l2)
        except ValidationError as e:
            error_message = e.messages[0] if hasattr(e, 'messages') and e.messages else str(e)
            messages.error(request, f"Senha do jogo (L2) inválida: {error_message}")
            return redirect('server:create_master_account')
        
        if password_l2 != confirm_password_l2:
            messages.error(request, "As senhas do jogo (L2) não coincidem.")
            return redirect('server:create_master_account')
        
        # Verifica se o username já existe no portal
        if User.objects.filter(username=username).exists():
            messages.error(request, f"O nome de usuário '{username}' já está em uso no portal.")
            return redirect('server:create_master_account')
        
        # Verifica se o username já existe no Lineage
        try:
            existing_account = LineageAccount.check_login_exists(username)
            if existing_account and len(existing_account) > 0:
                messages.error(request, f"O nome de usuário '{username}' já está em uso no jogo.")
                return redirect('server:create_master_account')
        except Exception as e:
            logger.error(f"[create_master_account] Erro ao verificar conta no Lineage: {e}", exc_info=True)
            messages.error(request, "Erro ao verificar disponibilidade do nome de usuário. Tente novamente.")
            return redirect('server:create_master_account')
        
        # Cria a conta no portal e no Lineage
        try:
            with transaction.atomic():
                # 1. Cria usuário no portal (PDL)
                new_user = User.objects.create_user(
                    username=username,
                    email=user_email,  # Usa o mesmo email do mestre
                    password=password_pdl,  # Senha do portal
                    is_active=True,
                    is_email_verified=False,  # Não precisa verificar, já está vinculado ao mestre
                    is_2fa_enabled=False,
                )
                
                logger.info(f"[create_master_account] Usuário {username} criado no portal")
                
                # 2. Cria conta no Lineage (L2)
                try:
                    success = LineageAccount.register(
                        login=username,
                        password=password_l2,  # Senha do Lineage
                        access_level=0,
                        email=user_email
                    )
                except Exception as e:
                    logger.error(f"[create_master_account] Erro ao criar conta no Lineage: {e}", exc_info=True)
                    # Rollback: remove o usuário criado no portal
                    new_user.delete()
                    messages.error(request, "Erro ao criar conta no jogo. O banco de dados do Lineage pode estar indisponível.")
                    return redirect('server:create_master_account')
                
                if not success:
                    # Rollback: remove o usuário criado no portal
                    new_user.delete()
                    messages.error(request, "Erro ao criar conta no jogo.")
                    return redirect('server:create_master_account')
                
                logger.info(f"[create_master_account] Conta {username} criada no Lineage")
                
                # 3. Vincula ao UUID da conta mestre
                try:
                    success_link = LineageAccount.link_account_to_user(username, master_uuid)
                except Exception as e:
                    logger.error(f"[create_master_account] Erro ao vincular conta: {e}", exc_info=True)
                    messages.warning(
                        request,
                        f"Conta '{username}' criada, mas houve um problema ao vincular automaticamente. Você pode vincular manualmente depois."
                    )
                    return redirect('server:account_dashboard')
                
                if success_link and success_link is not None:
                    logger.info(f"[create_master_account] Conta {username} vinculada ao mestre {master_user.username} com sucesso")
                    messages.success(
                        request,
                        f"✅ Conta '{username}' criada com sucesso no portal e no jogo, e vinculada à conta mestre {master_user.username}!"
                    )
                else:
                    messages.warning(
                        request,
                        f"Conta '{username}' criada, mas houve um problema ao vincular automaticamente. Você pode vincular manualmente depois."
                    )
                
        except Exception as e:
            logger.error(f"[create_master_account] Erro ao criar conta: {e}", exc_info=True)
            messages.error(request, f"Erro ao criar conta: {str(e)}")
            return redirect('server:create_master_account')
        
        return redirect('server:account_dashboard')
    
    # GET - mostra o formulário
    from apps.lineage.server.services.account_context import get_total_link_slots, get_used_link_slots
    
    total_slots = get_total_link_slots(master_user)
    used_slots = get_used_link_slots(master_user)
    available_slots = total_slots - used_slots
    
    context = {
        'master_user': master_user,
        'total_slots': total_slots,
        'used_slots': used_slots,
        'available_slots': available_slots,
    }
    
    return render(request, 'l2_accounts/create_master_account.html', context)
