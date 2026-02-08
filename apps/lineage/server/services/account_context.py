from __future__ import annotations

from typing import Dict, List, Tuple

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.lineage.server.models import ManagedLineageAccount
from utils.dynamic_import import get_query_class

LineageAccount = get_query_class("LineageAccount")

SESSION_KEY = "lineage_active_login"


def _normalize_login(login: str) -> str:
    return (login or "").strip()


def _default_login(user) -> str:
    return getattr(user, "username", "")


def user_has_access(user, account_login: str) -> bool:
    """
    Verifica se o usuário tem permissão para operar na conta informada.
    """
    if not user or not user.is_authenticated:
        return False

    normalized_login = _normalize_login(account_login)
    if not normalized_login:
        return False

    # Sempre permite acesso à conta principal
    if normalized_login == _default_login(user):
        return True

    # Verifica se existe delegação explícita via ManagedLineageAccount
    if ManagedLineageAccount.objects.filter(
        manager_user=user,
        account_login=normalized_login,
        status=ManagedLineageAccount.Status.ACTIVE,
    ).exists():
        return True

    # Verifica se a conta está vinculada ao UUID do usuário no banco do Lineage
    user_uuid = str(user.uuid) if hasattr(user, 'uuid') else None
    if user_uuid:
        try:
            from utils.dynamic_import import get_query_class
            LineageDBClass = get_query_class("LineageDB")
            
            if LineageDBClass:
                lineage_db = LineageDBClass()
                if lineage_db and getattr(lineage_db, 'enabled', False):
                    sql = """
                        SELECT login
                        FROM accounts
                        WHERE login = :login AND linked_uuid = :uuid
                        LIMIT 1
                    """
                    try:
                        result = lineage_db.select(sql, {"login": normalized_login, "uuid": user_uuid})
                        if result and len(result) > 0:
                            return True
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Erro ao verificar acesso via linked_uuid: {e}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao verificar acesso: {e}")

    # Verifica se o usuário é a conta mestre do e-mail e a conta tem o mesmo e-mail
    user_email = getattr(user, 'email', None)
    if user_email:
        try:
            from apps.main.home.models import EmailOwnership
            email_ownership = EmailOwnership.objects.filter(email=user_email).first()
            if email_ownership and email_ownership.owner == user:
                # Se for conta mestre, verifica se a conta do Lineage tem o mesmo e-mail
                try:
                    from utils.dynamic_import import get_query_class
                    LineageAccount = get_query_class("LineageAccount")
                    if LineageAccount and hasattr(LineageAccount, 'find_accounts_by_email'):
                        contas_por_email = LineageAccount.find_accounts_by_email(user_email)
                        for conta in contas_por_email:
                            login = conta.get("login") if isinstance(conta, dict) else getattr(conta, 'login', None)
                            if login == normalized_login:
                                return True
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Erro ao verificar acesso via e-mail: {e}")
        except Exception:
            pass

    return False


def get_available_accounts(user) -> List[Dict[str, str]]:
    """
    Retorna as contas que o usuário pode utilizar no painel.
    """
    accounts: List[Dict[str, str]] = []

    if not user or not user.is_authenticated:
        return accounts

    # SEMPRE adiciona a conta principal primeiro (username)
    default_login = _default_login(user)
    if default_login:
        accounts.append(
            {
                "login": default_login,
                "role": ManagedLineageAccount.Role.OWNER,
                "role_label": _("Conta principal"),
                "status": ManagedLineageAccount.Status.ACTIVE,
                "is_primary": True,
                "created_by": None,
            }
        )

    # Busca contas do Lineage vinculadas ao UUID do usuário
    user_uuid = str(user.uuid) if hasattr(user, 'uuid') else None
    linked_accounts = set()  # Para evitar duplicatas
    
    # Verifica se o usuário é a conta mestre do e-mail
    is_master = False
    user_email = getattr(user, 'email', None)
    if user_email:
        try:
            from apps.main.home.models import EmailOwnership
            email_ownership = EmailOwnership.objects.filter(email=user_email).first()
            if email_ownership and email_ownership.owner == user:
                is_master = True
        except Exception:
            pass
    
    if user_uuid:
        try:
            # Busca todas as contas do Lineage vinculadas ao UUID do usuário
            from utils.dynamic_import import get_query_class
            LineageDBClass = get_query_class("LineageDB")
            LineageAccount = get_query_class("LineageAccount")
            
            if LineageDBClass:
                lineage_db = LineageDBClass()
                if lineage_db and getattr(lineage_db, 'enabled', False):
                    # Se for conta mestre, busca contas por e-mail também
                    # MAS apenas as que estão vinculadas (têm linked_uuid)
                    # Usa SQL direto para evitar cache
                    if is_master and user_email:
                        try:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.info(f"[get_available_accounts] Buscando contas por email (SQL direto): {user_email}")
                            
                            # Busca diretamente no banco para evitar cache
                            sql = """
                                SELECT login, linked_uuid, email
                                FROM accounts
                                WHERE email = :email
                            """
                            contas_por_email = lineage_db.select(sql, {"email": user_email})
                            logger.info(f"[get_available_accounts] Contas encontradas por email: {len(contas_por_email) if contas_por_email else 0}")
                            
                            for conta in contas_por_email:
                                login = conta.get("login") if isinstance(conta, dict) else getattr(conta, 'login', None)
                                linked_uuid = conta.get("linked_uuid") if isinstance(conta, dict) else getattr(conta, 'linked_uuid', None)
                                email = conta.get("email") if isinstance(conta, dict) else getattr(conta, 'email', None)
                                
                                logger.info(f"[get_available_accounts] Conta encontrada: login={login}, linked_uuid={linked_uuid}, email={email}")
                                
                                # Só adiciona se tiver linked_uuid definido (está vinculada)
                                if login and login != default_login and linked_uuid:
                                    linked_accounts.add(login)
                                    logger.info(f"[get_available_accounts] Adicionando conta {login} à lista de contas disponíveis")
                                elif login and login != default_login and not linked_uuid:
                                    logger.info(f"[get_available_accounts] Conta {login} não está vinculada (linked_uuid é NULL), não adicionando")
                        except Exception as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Erro ao buscar contas por e-mail: {e}", exc_info=True)
                    
                    # Busca contas vinculadas ao UUID do usuário
                    # Busca também linked_uuid e email para logging e validação
                    sql = """
                        SELECT login, linked_uuid, email
                        FROM accounts
                        WHERE linked_uuid = :uuid
                    """
                    try:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"[get_available_accounts] Buscando contas vinculadas ao UUID: {user_uuid}")
                        result = lineage_db.select(sql, {"uuid": user_uuid})
                        logger.info(f"[get_available_accounts] Contas encontradas por UUID: {len(result) if result else 0}")
                        
                        if result:
                            for row in result:
                                # Tenta diferentes formas de acessar os campos
                                login = None
                                linked_uuid = None
                                email = None
                                
                                if isinstance(row, dict):
                                    login = row.get("login")
                                    linked_uuid = row.get("linked_uuid")
                                    email = row.get("email")
                                elif hasattr(row, 'login'):
                                    login = getattr(row, 'login', None)
                                    linked_uuid = getattr(row, 'linked_uuid', None)
                                    email = getattr(row, 'email', None)
                                elif hasattr(row, '__getitem__'):
                                    try:
                                        login = row['login']
                                        linked_uuid = row.get('linked_uuid')
                                        email = row.get('email')
                                    except (KeyError, TypeError):
                                        pass
                                
                                logger.info(f"[get_available_accounts] Conta encontrada por UUID: login={login}, linked_uuid={linked_uuid}, email={email}")
                                
                                if login and login != default_login:  # Evita duplicar a conta principal
                                    linked_accounts.add(login)
                                    logger.info(f"[get_available_accounts] Adicionando conta {login} à lista (via UUID)")
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Erro ao buscar contas vinculadas por UUID: {e}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao inicializar LineageDB: {e}")

    # Adiciona contas do Lineage vinculadas ao UUID do usuário
    for login in linked_accounts:
        accounts.append(
            {
                "login": login,
                "role": ManagedLineageAccount.Role.OWNER,
                "role_label": _("Conta vinculada"),
                "status": ManagedLineageAccount.Status.ACTIVE,
                "is_primary": False,
                "created_by": None,
            }
        )

    # Adiciona contas delegadas via ManagedLineageAccount
    try:
        links = ManagedLineageAccount.objects.filter(
            manager_user=user, status=ManagedLineageAccount.Status.ACTIVE
        ).select_related("created_by")

        for link in links:
            # Evita adicionar se já estiver na lista
            if not any(acc["login"] == link.account_login for acc in accounts):
                accounts.append(
                    {
                        "login": link.account_login,
                        "role": link.role,
                        "role_label": link.get_role_display(),
                        "status": link.status,
                        "is_primary": False,
                        "created_by": link.created_by.username if link.created_by else None,
                    }
                )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Erro ao buscar contas delegadas: {e}")

    return accounts


def get_active_login(request) -> str:
    """
    Obtém a conta ativa armazenada na sessão. Caso o usuário não tenha acesso
    a ela, retorna a conta padrão (username) e atualiza a sessão.
    """
    stored_login = _normalize_login(request.session.get(SESSION_KEY, ""))
    if stored_login and user_has_access(request.user, stored_login):
        return stored_login

    fallback = _default_login(request.user)
    request.session[SESSION_KEY] = fallback
    request.session.modified = True
    return fallback


def set_active_login(request, account_login: str):
    """
    Define explicitamente a conta ativa do usuário, validando o acesso.
    """
    normalized_login = _normalize_login(account_login)
    if not user_has_access(request.user, normalized_login):
        raise PermissionError(_("Você não tem acesso a esta conta."))

    request.session[SESSION_KEY] = normalized_login
    request.session.modified = True


def clear_active_login(request):
    """
    Remove a conta ativa da sessão.
    """
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]
        request.session.modified = True


def get_ownable_accounts(user) -> Tuple[List[Dict[str, str]], bool]:
    """
    Retorna apenas as contas que o usuário é proprietário e pode delegar.
    Inclui contas vinculadas ao UUID do usuário (linked_uuid).
    Se o usuário for conta mestre do e-mail, também inclui contas com o mesmo e-mail que estão vinculadas.
    NÃO inclui contas que foram delegadas para o usuário.
    NÃO inclui a conta principal se ela tiver outras contas vinculadas (pois você já é o mestre).
    
    Returns:
        tuple: (lista de contas, flag indicando se a conta principal foi excluída por ter contas vinculadas)
    """
    accounts: List[Dict[str, str]] = []
    primary_excluded = False

    if not user or not user.is_authenticated:
        return accounts, primary_excluded

    default_login = _default_login(user)
    user_uuid = str(user.uuid) if hasattr(user, 'uuid') else None
    
    # Verifica se o usuário é a conta mestre do e-mail
    is_master = False
    user_email = getattr(user, 'email', None)
    if user_email:
        try:
            from apps.main.home.models import EmailOwnership
            email_ownership = EmailOwnership.objects.filter(email=user_email).first()
            if email_ownership and email_ownership.owner == user:
                is_master = True
        except Exception:
            pass

    # Busca contas vinculadas ao UUID do usuário (proprietário)
    linked_accounts = set()  # Para evitar duplicatas
    
    if user_uuid:
        try:
            from utils.dynamic_import import get_query_class
            LineageDBClass = get_query_class("LineageDB")
            
            if LineageDBClass:
                lineage_db = LineageDBClass()
                if lineage_db and getattr(lineage_db, 'enabled', False):
                    # Se for conta mestre, busca contas por e-mail também (mas apenas as vinculadas)
                    if is_master and user_email:
                        try:
                            sql = """
                                SELECT login, linked_uuid, email
                                FROM accounts
                                WHERE email = :email AND linked_uuid IS NOT NULL
                            """
                            contas_por_email = lineage_db.select(sql, {"email": user_email})
                            if contas_por_email:
                                for conta in contas_por_email:
                                    login = conta.get("login") if isinstance(conta, dict) else getattr(conta, 'login', None)
                                    linked_uuid = conta.get("linked_uuid") if isinstance(conta, dict) else getattr(conta, 'linked_uuid', None)
                                    
                                    # Só adiciona se tiver linked_uuid e não for a conta principal
                                    if login and login != default_login and linked_uuid:
                                        linked_accounts.add(login)
                        except Exception as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.warning(f"Erro ao buscar contas por e-mail: {e}")
                    
                    # Busca contas vinculadas ao UUID do usuário
                    sql = """
                        SELECT login, linked_uuid, email
                        FROM accounts
                        WHERE linked_uuid = :uuid
                    """
                    try:
                        result = lineage_db.select(sql, {"uuid": user_uuid})
                        if result:
                            for row in result:
                                login = None
                                if isinstance(row, dict):
                                    login = row.get("login")
                                elif hasattr(row, 'login'):
                                    login = getattr(row, 'login', None)
                                
                                # Adiciona se não for a conta principal
                                if login and login != default_login:
                                    linked_accounts.add(login)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Erro ao buscar contas próprias: {e}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao inicializar LineageDB para buscar contas próprias: {e}")

    # Se a conta principal tem outras contas vinculadas, não inclui ela na lista
    # (porque você já é o mestre e não faz sentido delegar a conta principal)
    if default_login and linked_accounts:
        primary_excluded = True
    elif default_login and not linked_accounts:
        # Só adiciona a conta principal se ela não tiver outras contas vinculadas
        accounts.append(
            {
                "login": default_login,
                "role_label": _("Conta principal"),
            }
        )

    # Adiciona todas as contas vinculadas encontradas
    for login in linked_accounts:
        if not any(acc["login"] == login for acc in accounts):
            accounts.append(
                {
                    "login": login,
                    "role_label": _("Conta vinculada"),
                }
            )

    return accounts, primary_excluded


def count_linked_accounts(user) -> int:
    """
    Conta quantas contas estão vinculadas ao UUID do usuário (excluindo a conta principal).
    """
    if not user or not user.is_authenticated:
        return 0
    
    user_uuid = str(user.uuid) if hasattr(user, 'uuid') else None
    if not user_uuid:
        return 0
    
    default_login = _default_login(user)
    count = 0
    
    try:
        from utils.dynamic_import import get_query_class
        LineageDBClass = get_query_class("LineageDB")
        
        if LineageDBClass:
            lineage_db = LineageDBClass()
            if lineage_db and getattr(lineage_db, 'enabled', False):
                sql = """
                    SELECT COUNT(*) as total
                    FROM accounts
                    WHERE linked_uuid = :uuid AND login != :login
                """
                try:
                    result = lineage_db.select(sql, {"uuid": user_uuid, "login": default_login})
                    if result and len(result) > 0:
                        row = result[0]
                        if isinstance(row, dict):
                            count = row.get("total", 0)
                        elif hasattr(row, 'total'):
                            count = getattr(row, 'total', 0)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Erro ao contar contas vinculadas: {e}")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Erro ao inicializar LineageDB para contar contas: {e}")
    
    return count


def get_total_link_slots(user) -> int:
    """
    Retorna o total de slots de vinculação disponíveis para o usuário.
    Slots gratuitos configuráveis em ACCOUNT_LINK_FREE_SLOTS + slots comprados.
    """
    free_slots = getattr(settings, 'ACCOUNT_LINK_FREE_SLOTS', 3)
    
    if not user or not user.is_authenticated:
        return free_slots
    
    from apps.lineage.server.models import AccountLinkSlot
    purchased_slots = AccountLinkSlot.objects.filter(user=user).aggregate(
        total=models.Sum('slots_purchased')
    )['total'] or 0
    
    return free_slots + purchased_slots


def get_used_link_slots(user) -> int:
    """
    Retorna quantos slots estão sendo usados (contas vinculadas).
    """
    return count_linked_accounts(user)


def can_link_account(user) -> tuple[bool, str]:
    """
    Verifica se o usuário pode vincular mais uma conta.
    
    Returns:
        tuple: (pode_vincular, mensagem_erro)
    """
    if not user or not user.is_authenticated:
        return False, "Usuário não autenticado."
    
    used_slots = get_used_link_slots(user)
    total_slots = get_total_link_slots(user)
    
    if used_slots >= total_slots:
        return False, f"Você atingiu o limite de {total_slots} conta(s) vinculada(s). Compre mais slots para vincular contas adicionais."
    
    return True, ""


def get_lineage_template_context(request) -> Dict[str, object]:
    """
    Constrói um dicionário padrão para ser usado nos templates com informações
    sobre a conta ativa e as contas disponíveis.
    """
    email_master_owner = None
    is_email_master_owner = True
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False) and hasattr(user, "get_email_master_owner"):
        email_master_owner = user.get_email_master_owner()
        is_email_master_owner = (email_master_owner is None) or (email_master_owner == user)

    ownable_accounts, primary_excluded = get_ownable_accounts(request.user)
    
    return {
        "active_account_login": get_active_login(request),
        "available_lineage_accounts": get_available_accounts(request.user),
        "ownable_lineage_accounts": ownable_accounts,
        "primary_account_excluded": primary_excluded,
        "email_master_owner": email_master_owner,
        "is_email_master_owner": is_email_master_owner,
    }

