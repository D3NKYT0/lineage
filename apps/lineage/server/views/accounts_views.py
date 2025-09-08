from django.shortcuts import render, redirect
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
from apps.main.home.tasks import send_email_task
from apps.lineage.server.lineage_account_manager import LineageAccount
from utils.dynamic_import import get_query_class

signer = TimestampSigner()

LineageServices = get_query_class("LineageServices")


@conditional_otp_required
@require_lineage_connection
def account_dashboard(request):
    user_login = request.user.username
    account_data = LineageAccount.check_login_exists(user_login)

    # Verifica se a conta existe
    if not account_data or len(account_data) == 0:
        return redirect('server:lineage_register')

    account = account_data[0]

    # Verifica se a conta já está vinculada
    if not account.get("linked_uuid"):
        messages.warning(request, "Sua conta Lineage ainda não está vinculada. Por favor, vincule sua conta primeiro.")
        return redirect('server:link_lineage_account')
    
    user_uuid = str(request.user.uuid)
    if account.get("linked_uuid") != user_uuid:
        messages.error(request, "Sua conta Lineage está vinculada a outro usuário. Por favor, vincule novamente sua conta corretamente.")
        return redirect('server:link_lineage_account')

    try:
        personagens = LineageServices.find_chars(user_login)
    except Exception as e:
        personagens = []
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    acesslevel = LineageAccount.get_acess_level()
    account['status'] = "Ativa" if int(account[acesslevel]) >= 0 else "Bloqueada"

    # Formata data de criação
    created_time = None
    if account.get('created_time'):
        try:
            created_time = make_aware(datetime.strptime(account['created_time'], '%Y-%m-%d %H:%M:%S'))
        except:
            try:
                created_time = make_aware(datetime.fromtimestamp(int(account['created_time'])))
            except:
                created_time = None

    # Status dos personagens
    char_list = []
    for char in personagens:
        # Verificando se o campo 'level' existe antes de acessá-lo
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

    context = {
        'account': account,
        'created_time': created_time.strftime('%B %d, %Y às %H:%M') if created_time else '-',
        'lastIP': account.get('lastIP', '-'),
        'char_count': account.get('chars', 0),
        'characters': char_list,
        'char_count': len(char_list)
    }

    return render(request, 'l2_accounts/dashboard.html', context)


@conditional_otp_required
@require_lineage_connection
def update_password(request):
    user = request.user

    # Verifica se a conta Lineage está vinculada
    account_data = LineageAccount.check_login_exists(user.username)
    if not account_data or len(account_data) == 0 or not account_data[0].get("linked_uuid"):
        messages.error(request, "Sua conta Lineage não está vinculada. Por favor, vincule sua conta antes de atualizar a senha.")
        return redirect('server:link_lineage_account')
    
    user_uuid = str(request.user.uuid)
    if account_data[0].get("linked_uuid") != user_uuid:
        messages.error(request, "Sua conta Lineage está vinculada a outro usuário. Por favor, vincule novamente sua conta corretamente.")
        return redirect('server:link_lineage_account')

    if request.method == "POST":
        senha = request.POST.get("nova_senha")
        confirmar = request.POST.get("confirmar_senha")

        if not senha or not confirmar:
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect('server:update_password')

        if senha != confirmar:
            messages.error(request, "As senhas não coincidem.")
            return redirect('server:update_password')

        success = LineageAccount.update_password(senha, user.username)

        if success:
            messages.success(request, "Senha atualizada com sucesso!")
            return redirect('server:account_dashboard')
        else:
            messages.error(request, "Erro ao atualizar senha.")
            return redirect('server:update_password')

    # GET request — exibe o formulário
    return render(request, "l2_accounts/update_password.html")


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

        success = LineageAccount.register(
            login=user.username,
            password=password,
            access_level=0,
            email=user.email
        )

        if success:
            # Vincula automaticamente a conta após o registro
            user_uuid = str(request.user.uuid)  # Certifique-se de que o User tem um campo `uuid`
            success_link = LineageAccount.link_account_to_user(user.username, user_uuid)

            if success_link:
                messages.success(request, "Conta Lineage criada e vinculada com sucesso!")
                return redirect('server:register_success')
            else:
                messages.error(request, "Erro ao vincular a conta.")
                return redirect('server:lineage_register')
        else:
            messages.error(request, "Erro ao criar conta.")
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
    if request.method == "POST":
        login_jogo = request.user.username
        senha_jogo = request.POST.get("senha")

        # Verifica se login + senha são válidos
        is_valided = LineageAccount.validate_credentials(login_jogo, senha_jogo)
        if not is_valided:
            messages.error(request, "Login ou senha incorretos.")
            return redirect("server:link_lineage_account")
        
        conta = LineageAccount.get_account_by_login(login_jogo)

        # Já está vinculada?
        if conta.get("linked_uuid"):
            messages.warning(request, "Essa conta já está vinculada a outro usuário.")
            return redirect("server:link_lineage_account")

        # Vincula a conta
        user_uuid = str(request.user.uuid)  # Certifique-se de que o User tem um campo `uuid`
        success = LineageAccount.link_account_to_user(login_jogo, user_uuid)

        if success:
            messages.success(request, "Conta vinculada com sucesso!")
            return redirect("server:account_dashboard")
        else:
            messages.error(request, "Erro ao vincular conta.")
            return redirect("server:link_lineage_account")

    return render(request, "l2_accounts/vincular_conta.html")


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

    conta = LineageAccount.get_account_by_login_and_email(login, email)
    if not conta or conta.get("linked_uuid"):
        messages.error(request, "Conta inválida ou já vinculada.")
        return redirect("server:link_lineage_account")
    
    success = LineageAccount.link_account_to_user(login, str(request.user.uuid))
    if success:
        messages.success(request, "Conta vinculada com sucesso!")
        return redirect("server:account_dashboard")
    else:
        messages.error(request, "Erro ao vincular a conta.")
        return redirect("server:link_lineage_account")
