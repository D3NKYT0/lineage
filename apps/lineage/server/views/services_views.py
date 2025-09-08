from django.shortcuts import render, redirect
from apps.main.home.decorator import conditional_otp_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from ..models import ServicePrice
from ..decorators import require_lineage_connection
import re

from utils.dynamic_import import get_query_class  
LineageServices = get_query_class("LineageServices")
TransferFromCharToWallet = get_query_class("TransferFromCharToWallet")


@conditional_otp_required
@require_lineage_connection
def change_nickname_view(request, char_id):
    try:
        price = ServicePrice.objects.get(servico='CHANGE_NICKNAME').preco
    except ServicePrice.DoesNotExist:
        messages.error(request, _("Preço do serviço não configurado."))
        return redirect("server:account_dashboard")
    
    response = TransferFromCharToWallet.find_char(request.user.username, char_id)
    
    if request.method == "POST":
        acc = request.user.username
        cid = char_id
        name = request.POST.get("name")

        if not response:
            messages.error(request, 'Personagem não encontrado ou não pertence à sua conta.')
            return redirect("server:change_nickname", char_id=char_id)

        if response[0]['online'] != 0:
            messages.error(request, 'O personagem precisa estar offline.')
            return redirect("server:change_nickname", char_id=char_id)

        # Regex de validação
        pattern = r"^([0-9A-Za-z]{2,16})|([0-9\u0410-\u044f]{3,16})$"

        if not re.fullmatch(pattern, name):
            messages.error(request, _("Nickname inválido. Use de 2 a 16 caracteres latinos ou de 3 a 16 caracteres cirílicos."))
            return redirect("server:change_nickname", char_id=char_id)

        wallet, wallet_created = Wallet.objects.get_or_create(usuario=request.user)

        if wallet.saldo < price:
            messages.error(request, _("Saldo insuficiente na carteira."))
            return redirect("server:change_nickname", char_id=char_id)

        result = LineageServices.change_nickname(acc, cid, name)

        if result:
            aplicar_transacao(wallet, "SAIDA", price, descricao="Alteração de Nickname")
            messages.success(request, _("Nickname alterado com sucesso!"))
            return redirect("server:account_dashboard")
        else:
            messages.error(request, _("Erro ao alterar nickname."))

    context = {
        'char_id': char_id,
        'char_name': response[0]['char_name'],
        'price': price
    }
    return render(request, "services/change_nickname.html", context)


@conditional_otp_required
@require_lineage_connection
def change_sex_view(request, char_id):
    try:
        price = ServicePrice.objects.get(servico='CHANGE_SEX').preco
    except ServicePrice.DoesNotExist:
        messages.error(request, _("Preço do serviço não configurado."))
        return redirect("server:account_dashboard")
    
    response = TransferFromCharToWallet.find_char(request.user.username, char_id)

    if request.method == "POST":
        acc = request.user.username
        cid = char_id
        sex_input = request.POST.get("sex")

        if not response:
            messages.error(request, 'Personagem não encontrado ou não pertence à sua conta.')
            return redirect("server:change_nickname", char_id=char_id)

        if response[0]['online'] != 0:
            messages.error(request, 'O personagem precisa estar offline.')
            return redirect("server:change_nickname", char_id=char_id)

        # Validação
        if sex_input not in ['M', 'F']:
            messages.error(request, _("Sexo inválido selecionado."))
            return redirect("server:change_sex", char_id=char_id)

        # Converte 'F' para 1 e 'M' para 0
        sex_value = 1 if sex_input == 'F' else 0

        wallet, wallet_created = Wallet.objects.get_or_create(usuario=request.user)

        if wallet.saldo < price:
            messages.error(request, _("Saldo insuficiente na carteira."))
            return redirect("server:change_sex", char_id=char_id)

        result = LineageServices.change_sex(acc, cid, sex_value)

        if result:
            aplicar_transacao(wallet, "SAIDA", price, descricao="Alteração de Sexo")
            messages.success(request, _("Sexo alterado com sucesso!"))
            return redirect("server:account_dashboard")
        else:
            messages.error(request, _("Erro ao alterar sexo."))

    context = {
        'char_id': char_id,
        'price': price,
        'char_name': response[0]['char_name'],
    }
    return render(request, "services/change_sex.html", context)


@conditional_otp_required
@require_lineage_connection
def unstuck_view(request, char_id):

    response = TransferFromCharToWallet.find_char(request.user.username, char_id)

    if request.method == "POST":
        acc = request.user.username
        cid = char_id

        if not response:
            messages.error(request, 'Personagem não encontrado ou não pertence à sua conta.')
            return redirect("server:change_nickname", char_id=char_id)

        if response[0]['online'] != 0:
            messages.error(request, 'O personagem precisa estar offline.')
            return redirect("server:change_nickname", char_id=char_id)

        # posições fixas
        spawn_x = 83400
        spawn_y = 147940
        spawn_z = -3404
        result = LineageServices.unstuck(acc, cid, spawn_x, spawn_y, spawn_z)
        if result:
            messages.success(request, _("Personagem desbugado com sucesso!"))
            return redirect("server:account_dashboard")
        else:
            messages.error(request, _("Erro ao desbugar personagem."))
            return redirect("server:unstuck", char_id=char_id)

    context = {
        'char_id': char_id,
        'char_name': response[0]['char_name'],
    }
    return render(request, "services/unstuck.html", context)


@staff_member_required
def configure_service_prices(request):
    if request.method == "POST":
        # Recuperando ou criando entradas para os serviços
        try:
            change_nickname_price = request.POST.get("change_nickname_price")
            change_sex_price = request.POST.get("change_sex_price")

            # Validação básica para garantir que os valores sejam numéricos
            if not change_nickname_price.isnumeric() or not change_sex_price.isnumeric():
                messages.error(request, _("Os preços precisam ser valores numéricos."))
                return redirect("server:configure_service_prices")

            # Configurando ou atualizando os preços
            ServicePrice.objects.update_or_create(
                servico='CHANGE_NICKNAME',
                defaults={'preco': float(change_nickname_price)}
            )
            ServicePrice.objects.update_or_create(
                servico='CHANGE_SEX',
                defaults={'preco': float(change_sex_price)}
            )

            messages.success(request, _("Preços dos serviços atualizados com sucesso!"))
            return redirect("server:configure_service_prices")
        except Exception as e:
            messages.error(request, _("Erro ao configurar os preços: ") + str(e))
            return redirect("server:configure_service_prices")
    
    # Pegando os preços atuais para exibir no formulário
    try:
        change_nickname_price = ServicePrice.objects.get(servico='CHANGE_NICKNAME').preco
        change_sex_price = ServicePrice.objects.get(servico='CHANGE_SEX').preco
    except ServicePrice.DoesNotExist:
        change_nickname_price = 0
        change_sex_price = 0

    context = {
        'change_nickname_price': change_nickname_price,
        'change_sex_price': change_sex_price,
    }

    return render(request, "services/configure_service_prices.html", context)
