from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied
from django.utils.timezone import make_aware, now
from datetime import datetime
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.urls import reverse
from django.conf import settings
from apps.main.home.tasks import send_email_task
from utils.resources import gen_avatar, get_class_name
from utils.dynamic_import import get_query_class
from drf_spectacular.utils import extend_schema

LineageAccount = get_query_class("LineageAccount")
LineageServices = get_query_class("LineageServices")
signer = TimestampSigner()
from apps.lineage.server.services.account_context import user_has_access


def resolve_account_login(request):
    """
    Determina qual conta do Lineage deve ser utilizada na requisição.
    Prioriza parâmetros explícitos e, em seguida, dados de sessão ou username.
    """
    account_login = (
        request.query_params.get("account_login")
        or request.data.get("account_login")
        or request.session.get("lineage_active_login")
        or request.user.username
    )

    account_login = (account_login or "").strip()
    if not account_login:
        account_login = request.user.username

    if not user_has_access(request.user, account_login):
        raise PermissionDenied("Você não tem permissão para acessar essa conta.")

    return account_login
@extend_schema(exclude=True)
class AccountDashboardAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_login = resolve_account_login(request)
        account_data = LineageAccount.check_login_exists(user_login)
        if not account_data or len(account_data) == 0:
            return Response({'error': 'Conta não existe.'}, status=404)
        account = account_data[0]
        if not account.get("linked_uuid"):
            return Response({'error': 'Conta não vinculada.'}, status=400)
        owner_uuid = account.get("linked_uuid")
        if owner_uuid != str(request.user.uuid) and not user_has_access(request.user, user_login):
            raise PermissionDenied("Você não tem permissão para visualizar essa conta.")
        try:
            personagens = LineageServices.find_chars(user_login)
        except Exception:
            personagens = []
        acesslevel = LineageAccount.get_acess_level()
        account['status'] = "Ativa" if int(account[acesslevel]) >= 0 else "Bloqueada"
        created_time = None
        if account.get('created_time'):
            try:
                created_time = make_aware(datetime.strptime(account['created_time'], '%Y-%m-%d %H:%M:%S'))
            except:
                try:
                    created_time = make_aware(datetime.fromtimestamp(int(account['created_time'])))
                except:
                    created_time = None
        char_list = []
        for char in personagens:
            level = char.get('base_level', '-')
            char_list.append({
                'id': char['obj_Id'],
                'nome': char['char_name'],
                'title': char.get('title', '-'),
                'lastAccess': datetime.fromtimestamp(int(char['lastAccess']) / 1000).strftime('%B %d, %Y às %H:%M') if char.get('lastAccess') else '-',
                'online': 'Online' if char.get('online') else 'Offline',
                'base_class': get_class_name(char['base_class']),
                'subclass1': get_class_name(char['subclass1']) if char.get('subclass1') else '-',
                'subclass2': get_class_name(char['subclass2']) if char.get('subclass2') else '-',
                'subclass3': get_class_name(char['subclass3']) if char.get('subclass3') else '-',
                'level': level,
                'sex': 'Feminino' if char['sex'] else 'Masculino',
                'pvp': char['pvpkills'],
                'pk': char['pkkills'],
                'karma': char['karma'],
                'clan': char.get('clan_name', '-'),
                'ally': char.get('ally_name', '-'),
                'nobless': 'Sim' if char.get('nobless') else 'Não',
                'hero': 'Sim' if char.get('hero_end') and int(char['hero_end']) > int(now().timestamp() * 1000) else 'Não',
                'avatar': gen_avatar(char['base_class'], char['sex'])
            })
        data = {
            'account': account,
            'created_time': created_time.strftime('%B %d, %Y às %H:%M') if created_time else '-',
            'lastIP': account.get('lastIP', '-'),
            'char_count': len(char_list),
            'characters': char_list
        }
        return Response(data)

@extend_schema(exclude=True)
class UpdatePasswordAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        account_data = LineageAccount.check_login_exists(user.username)
        if not account_data or len(account_data) == 0 or not account_data[0].get("linked_uuid"):
            return Response({'error': 'Conta não vinculada.'}, status=400)
        user_uuid = str(request.user.uuid)
        if account_data[0].get("linked_uuid") != user_uuid:
            return Response({'error': 'Conta vinculada a outro usuário.'}, status=400)
        senha = request.data.get("nova_senha")
        confirmar = request.data.get("confirmar_senha")
        if not senha or not confirmar:
            return Response({'error': 'Preencha todos os campos.'}, status=400)
        if senha != confirmar:
            return Response({'error': 'As senhas não coincidem.'}, status=400)
        success = LineageAccount.update_password(senha, user.username)
        if success:
            return Response({'success': True})
        return Response({'error': 'Erro ao atualizar senha.'}, status=400)

@extend_schema(exclude=True)
class RegisterLineageAccountAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        existing_account = LineageAccount.check_login_exists(user.username)
        if existing_account and len(existing_account) > 0:
            return Response({'error': 'Conta já criada.'}, status=400)
        password = request.data.get('password')
        confirm = request.data.get('confirm')
        if password != confirm:
            return Response({'error': 'As senhas não coincidem.'}, status=400)
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
            logger.error(f"[RegisterLineageAccountAPI] Erro ao registrar conta no banco do Lineage: {e}", exc_info=True)
            return Response({'error': 'Erro ao criar conta. O banco de dados do Lineage pode estar indisponível.'}, status=503)
        
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
                                return Response({
                                    'error': f'Conta criada, mas não foi possível vincular automaticamente. {error_message}',
                                    'warning': True
                                }, status=200)
                            
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
                    logger.error(f"[RegisterLineageAccountAPI] Erro ao verificar conta mestre no registro: {e}", exc_info=True)
                    # Em caso de erro, vincula ao próprio UUID
                    user_uuid = str(request.user.uuid)
            else:
                # Email não verificado ou não tem email, vincula ao próprio UUID
                user_uuid = str(request.user.uuid)
            
            try:
                success_link = LineageAccount.link_account_to_user(user_login, user_uuid)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"[RegisterLineageAccountAPI] Erro ao vincular conta no banco do Lineage: {e}", exc_info=True)
                return Response({
                    'success': True,
                    'warning': True,
                    'message': 'Conta criada, mas houve um problema ao vincular automaticamente. Você pode vincular manualmente depois.'
                }, status=200)
            
            if success_link and success_link is not None:
                response_data = {'success': True}
                if master_user and master_user != request.user:
                    response_data['message'] = f'Conta vinculada automaticamente à conta mestre {master_user.username}'
                return Response(response_data)
            else:
                return Response({
                    'success': True,
                    'warning': True,
                    'message': 'Conta criada, mas houve um problema ao vincular automaticamente. Você pode vincular manualmente depois.'
                }, status=200)
        else:
            return Response({'error': 'Erro ao criar conta. O banco de dados do Lineage pode estar indisponível.'}, status=503)

@extend_schema(exclude=True)
class LinkLineageAccountAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        login_jogo = request.user.username
        senha_jogo = request.data.get("senha")
        is_valided = LineageAccount.validate_credentials(login_jogo, senha_jogo)
        if not is_valided:
            return Response({'error': 'Login ou senha incorretos.'}, status=400)
        conta = LineageAccount.get_account_by_login(login_jogo)
        if conta.get("linked_uuid"):
            return Response({'error': 'Conta já vinculada a outro usuário.'}, status=400)
        user_uuid = str(request.user.uuid)
        success = LineageAccount.link_account_to_user(login_jogo, user_uuid)
        if success:
            return Response({'success': True})
        else:
            return Response({'error': 'Erro ao vincular conta.'}, status=400)

@extend_schema(exclude=True)
class RequestLinkByEmailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({'error': 'Informe um e-mail.'}, status=400)
        contas = LineageAccount.find_accounts_by_email(email)
        conta = next((c for c in contas if not c.get("linked_uuid")), None)
        if not conta:
            return Response({'error': 'Nenhuma conta não vinculada foi encontrada com esse e-mail.'}, status=400)
        data = f"{conta['login']}|{email}"
        token = signer.sign(data)
        link = request.build_absolute_uri(
            reverse("server:link_by_email_token", args=[token])
        )
        send_email_task.delay(
            "Vinculação de Conta Lineage",
            f"Clique no link abaixo para vincular sua conta:\n\n{link}\n\nO link expira em 1 hora.",
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        return Response({'success': True, 'link': link})

@extend_schema(exclude=True)
class LinkByEmailTokenAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token não informado.'}, status=400)
        try:
            data = signer.unsign(token, max_age=3600)
            login, email = data.split('|')
        except SignatureExpired:
            return Response({'error': 'Link expirado.'}, status=400)
        except BadSignature:
            return Response({'error': 'Token inválido.'}, status=400)
        conta = LineageAccount.get_account_by_login_and_email(login, email)
        if not conta or conta.get("linked_uuid"):
            return Response({'error': 'Conta inválida ou já vinculada.'}, status=400)
        success = LineageAccount.link_account_to_user(login, str(request.user.uuid))
        if success:
            return Response({'success': True})
        else:
            return Response({'error': 'Erro ao vincular a conta.'}, status=400) 
