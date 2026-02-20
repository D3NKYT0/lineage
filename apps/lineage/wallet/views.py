from django.core.paginator import Paginator
from apps.main.home.decorator import conditional_otp_required
from .models import Wallet, TransacaoWallet, TransacaoBonus, CoinConfig
from apps.lineage.games.models import TokenHistory
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate
from apps.main.home.models import User
from django.db import transaction, models
from .signals import aplicar_transacao, aplicar_transacao_bonus
from apps.lineage.server.database import LineageDB
from apps.lineage.server.services.account_context import (
    get_active_login,
    get_lineage_template_context,
)
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone
from django.urls import reverse
import hashlib
import time
import logging
from django.conf import settings

from core.log_utils import log_action
from apps.main.home.models import PerfilGamer

from utils.dynamic_import import get_query_class
TransferFromWalletToChar = get_query_class("TransferFromWalletToChar")
TransferFromCharToWallet = get_query_class("TransferFromCharToWallet")
LineageServices = get_query_class("LineageServices")

from django.utils.translation import gettext as _
from django.http import JsonResponse

logger = logging.getLogger(__name__)


@conditional_otp_required
def dashboard_wallet(request):
    wallet, created = Wallet.objects.get_or_create(usuario=request.user)
    
    # Buscar transações normais e de bônus
    transacoes_normais = TransacaoWallet.objects.filter(wallet=wallet).order_by('-data')
    transacoes_bonus = TransacaoBonus.objects.filter(wallet=wallet).order_by('-data')
    
    # Combina as duas listas em Python para evitar problemas com UNION
    todas_transacoes = []
    
    for transacao in transacoes_normais:
        todas_transacoes.append({
            'id': transacao.id,
            'tipo': transacao.tipo,
            'valor': transacao.valor,
            'descricao': transacao.descricao,
            'data': transacao.data,
            'origem': transacao.origem,
            'destino': transacao.destino,
            'tipo_transacao': 'normal'
        })
    
    for transacao in transacoes_bonus:
        todas_transacoes.append({
            'id': transacao.id,
            'tipo': transacao.tipo,
            'valor': transacao.valor,
            'descricao': transacao.descricao,
            'data': transacao.data,
            'origem': transacao.origem,
            'destino': transacao.destino,
            'tipo_transacao': 'bonus'
        })
    
    # Ordena por data (mais recente primeiro)
    todas_transacoes.sort(key=lambda x: x['data'], reverse=True)
    
    paginator = Paginator(todas_transacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from utils.pagination_helper import prepare_pagination_context
    pagination_context = prepare_pagination_context(page_obj)

    context = {
        'wallet': wallet,
        'transacoes': page_obj.object_list,
        'page_obj': page_obj,
        **pagination_context,
    }
    context.update(get_lineage_template_context(request))
    return render(request, 'wallet/dashboard.html', context)


@conditional_otp_required
def transfer_to_server(request):
    active_login = get_active_login(request)

    # Verifica conexão com banco do Lineage
    db = LineageDB()
    if not db.is_connected():
        messages.error(request, 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.')
        return redirect('wallet:dashboard')
    
    config = CoinConfig.objects.filter(ativa=True).first()
    if not config:
        messages.error(request, 'Nenhuma moeda configurada está ativa no momento.')
        return redirect('wallet:dashboard')

    wallet, created = Wallet.objects.get_or_create(usuario=request.user)
    personagens = []

    # Lista os personagens da conta
    try:
        personagens = LineageServices.find_chars(active_login)
    except:
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    # A view apenas renderiza o formulário
    # O processamento é feito via API chamada pelo frontend (AJAX)

    context = {
        'wallet': wallet,
        'personagens': personagens,
        'show_bonus_option': getattr(config, 'exibir_opcao_bonus_transferencia', False),
        'bonus_enabled': getattr(config, 'habilitar_transferencia_com_bonus', False),
    }
    context.update(get_lineage_template_context(request))
    return render(request, 'wallet/transfer_to_server.html', context)


@conditional_otp_required
def transfer_to_player(request):
    # A view apenas renderiza o formulário
    # O processamento é feito via API chamada pelo frontend (AJAX)
    
    wallet, created = Wallet.objects.get_or_create(usuario=request.user)
    return render(request, 'wallet/transfer_to_player.html', {
        'wallet': wallet,
    })


@conditional_otp_required
def transfer_from_server(request):
    active_login = get_active_login(request)

    # Verifica conexão com banco do Lineage
    db = LineageDB()
    if not db.is_connected():
        messages.error(request, 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.')
        return redirect('wallet:dashboard')
    
    config = CoinConfig.objects.filter(ativa=True).first()
    if not config:
        messages.error(request, 'Nenhuma moeda configurada está ativa no momento.')
        return redirect('wallet:dashboard')

    wallet, created = Wallet.objects.get_or_create(usuario=request.user)
    personagens = []
    personagens_com_moedas = []

    # Lista os personagens da conta
    try:
        personagens = LineageServices.find_chars(active_login)
        
        # Para cada personagem, verifica a quantidade de moedas
        COIN_ID = config.coin_id
        for personagem in personagens:
            char_id = personagem.get('charId') or personagem.get('obj_Id') or personagem.get('char_id')
            if not char_id:
                continue
                
            coin_info = TransferFromCharToWallet.check_ingame_coin(COIN_ID, char_id)
            if coin_info and coin_info.get('total', 0) > 0:
                personagens_com_moedas.append({
                    'char_id': char_id,
                    'char_name': personagem.get('char_name') or personagem.get('charName') or personagem.get('name', ''),
                    'online': personagem.get('online', 0),
                    'coin_amount': coin_info.get('total', 0),
                    'coin_inventory': coin_info.get('inventory', 0),
                    'coin_warehouse': coin_info.get('warehouse', 0),
                })
    except Exception as e:
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    if request.method == 'POST':
        char_id = request.POST.get('char_id')
        quantidade_moedas = request.POST.get('quantidade_moedas')
        senha = request.POST.get('senha')

        COIN_ID = config.coin_id
        multiplicador = config.multiplicador
        taxa_percentual = getattr(config, 'taxa_retirada', Decimal('0.00'))

        try:
            quantidade_moedas = int(quantidade_moedas)
            char_id = int(char_id)
        except (ValueError, TypeError):
            messages.error(request, 'Valor inválido.')
            return redirect('wallet:transfer_from_server')

        if quantidade_moedas < 1:
            messages.error(request, 'A quantidade de moedas deve ser maior que zero.')
            return redirect('wallet:transfer_from_server')

        # Verificação de senha
        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect('wallet:transfer_from_server')

        # Verifica se o personagem pertence à conta
        personagem_info = TransferFromCharToWallet.find_char(active_login, char_id)
        if not personagem_info:
            messages.error(request, 'Personagem inválido ou não pertence a essa conta.')
            return redirect('wallet:transfer_from_server')

        # Verifica se o personagem está offline (se necessário)
        if personagem_info and len(personagem_info) > 0:
            if personagem_info[0].get('online', 0) != 0:
                messages.error(request, 'O personagem precisa estar offline para realizar a retirada.')
                return redirect('wallet:transfer_from_server')

        # Verifica a quantidade de moedas disponíveis
        coin_info = TransferFromCharToWallet.check_ingame_coin(COIN_ID, char_id)
        if not coin_info or coin_info.get('total', 0) < quantidade_moedas:
            messages.error(request, 'Quantidade de moedas insuficiente no personagem.')
            return redirect('wallet:transfer_from_server')

        # Calcula o valor em R$ (quantidade de moedas / multiplicador)
        valor_bruto = Decimal(quantidade_moedas) / multiplicador
        
        # Calcula a taxa
        taxa_valor = (valor_bruto * taxa_percentual) / Decimal('100.00')
        
        # Valor líquido que será creditado na carteira
        valor_liquido = valor_bruto - taxa_valor

        try:
            with transaction.atomic():
                # Bloqueia a carteira para prevenir race conditions
                wallet = Wallet.objects.select_for_update().get(usuario=request.user)
                
                # Remove as moedas do personagem
                sucesso = TransferFromCharToWallet.remove_ingame_coin(
                    coin_id=COIN_ID,
                    count=quantidade_moedas,
                    char_id=char_id
                )

                if not sucesso:
                    raise Exception(_("Erro ao remover as moedas do personagem."))

                # Adiciona o valor líquido na carteira
                aplicar_transacao(
                    wallet=wallet,
                    tipo="ENTRADA",
                    valor=valor_liquido,
                    descricao=f"Retirada do servidor (Taxa: {taxa_percentual}%)",
                    origem=personagem_info[0].get('char_name', 'Servidor') if personagem_info else 'Servidor',
                    destino=active_login
                )

        except Exception as e:
            log_action(
                logger, "wallet_retirada_servidor", "erro",
                username=request.user.username,
                char_id=char_id,
                quantidade_moedas=quantidade_moedas,
                valor_liquido=str(valor_liquido),
                erro=str(e),
                level=logging.ERROR,
                exc_info=True,
            )
            messages.error(request, f"Ocorreu um erro durante a retirada: {str(e)}")
            return redirect('wallet:transfer_from_server')

        perfil, created = PerfilGamer.objects.get_or_create(user=request.user)
        perfil.adicionar_xp(40)

        log_action(
            logger, "wallet_retirada_servidor", "sucesso",
            username=request.user.username,
            char_id=char_id,
            quantidade_moedas=quantidade_moedas,
            valor_bruto=str(valor_bruto),
            taxa_percentual=str(taxa_percentual),
            valor_liquido=str(valor_liquido),
        )
        messages.success(request, _(
            f"Retirada realizada com sucesso! "
            f"R${valor_bruto:.2f} retirados (Taxa: R${taxa_valor:.2f} - {taxa_percentual}%). "
            f"R${valor_liquido:.2f} creditados na sua carteira."
        ))
        return redirect('wallet:dashboard')

    context = {
        'wallet': wallet,
        'personagens_com_moedas': personagens_com_moedas,
        'config': config,
        'taxa_retirada': getattr(config, 'taxa_retirada', Decimal('0.00')),
    }
    context.update(get_lineage_template_context(request))
    return render(request, 'wallet/transfer_from_server.html', context)


@staff_member_required
@require_http_methods(["GET", "POST"])
def coin_config_panel(request):
    if request.method == "POST":
        if "activate_coin_id" in request.POST:
            coin_id = request.POST.get("activate_coin_id")
            if coin_id:
                try:
                    # Busca a moeda que será ativada
                    moeda_para_ativar = CoinConfig.objects.get(id=coin_id)
                    
                    # Verifica se a moeda já está ativa
                    if moeda_para_ativar.ativa:
                        messages.info(request, f'Moeda "{moeda_para_ativar.nome}" já está ativa.')
                        return redirect("wallet:coin_config_panel")
                    
                    # Desativa todas as moedas primeiro
                    CoinConfig.objects.update(ativa=False)
                    
                    # Ativa a moeda selecionada usando save() para garantir que a lógica do modelo seja executada
                    moeda_para_ativar.ativa = True
                    moeda_para_ativar.save()
                    log_action(logger, "wallet_coin_config", "moeda_ativada", coin_id=coin_id, nome=moeda_para_ativar.nome, staff=request.user.username)
                    messages.success(request, f'Moeda "{moeda_para_ativar.nome}" ativada com sucesso!')
                except CoinConfig.DoesNotExist:
                    messages.error(request, 'Moeda não encontrada.')
                except Exception as e:
                    messages.error(request, f'Erro ao ativar moeda: {str(e)}')
                
                return redirect("wallet:coin_config_panel")

        elif "create_coin" in request.POST:
            nome = request.POST.get("nome")
            coin_id = request.POST.get("coin_id")
            multiplicador = request.POST.get("multiplicador")
            taxa_retirada = request.POST.get("taxa_retirada", "0.00")

            if nome and coin_id and multiplicador:
                try:
                    # Verifica se já existe uma moeda com este ID
                    if CoinConfig.objects.filter(coin_id=coin_id).exists():
                        messages.error(request, f'Já existe uma moeda configurada com o ID {coin_id}.')
                        return redirect("wallet:coin_config_panel")
                    
                    # Converte taxa_retirada para Decimal
                    try:
                        taxa_retirada = Decimal(taxa_retirada)
                        if taxa_retirada < 0 or taxa_retirada > 100:
                            messages.error(request, 'A taxa de retirada deve estar entre 0 e 100%.')
                            return redirect("wallet:coin_config_panel")
                    except (ValueError, TypeError):
                        taxa_retirada = Decimal('0.00')
                    
                    # Cria a nova moeda (ativa=False por padrão)
                    nova_moeda = CoinConfig.objects.create(
                        nome=nome,
                        coin_id=coin_id,
                        multiplicador=multiplicador,
                        taxa_retirada=taxa_retirada,
                        ativa=False
                    )
                    log_action(logger, "wallet_coin_config", "moeda_criada", nome=nova_moeda.nome, coin_id=coin_id, staff=request.user.username)
                    messages.success(request, f'Moeda "{nova_moeda.nome}" criada com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar moeda: {str(e)}')
                
                return redirect("wallet:coin_config_panel")

        elif "update_taxa" in request.POST:
            coin_id = request.POST.get("coin_id")
            taxa_retirada = request.POST.get("taxa_retirada", "0.00")

            if coin_id:
                try:
                    moeda = CoinConfig.objects.get(id=coin_id)
                    
                    # Converte taxa_retirada para Decimal
                    try:
                        taxa_retirada = Decimal(taxa_retirada)
                        if taxa_retirada < 0 or taxa_retirada > 100:
                            messages.error(request, 'A taxa de retirada deve estar entre 0 e 100%.')
                            return redirect("wallet:coin_config_panel")
                    except (ValueError, TypeError):
                        taxa_retirada = Decimal('0.00')
                    
                    moeda.taxa_retirada = taxa_retirada
                    moeda.save()
                    log_action(logger, "wallet_coin_config", "taxa_atualizada", nome=moeda.nome, taxa_retirada=str(taxa_retirada), staff=request.user.username)
                    messages.success(request, f'Taxa de retirada da moeda "{moeda.nome}" atualizada para {taxa_retirada}%!')
                except CoinConfig.DoesNotExist:
                    messages.error(request, 'Moeda não encontrada.')
                except Exception as e:
                    messages.error(request, f'Erro ao atualizar taxa: {str(e)}')
                
                return redirect("wallet:coin_config_panel")

        elif "delete_coin_id" in request.POST:
            coin_id = request.POST.get("delete_coin_id")
            if coin_id:
                try:
                    moeda = CoinConfig.objects.get(id=coin_id)
                    nome_moeda = moeda.nome
                    estava_ativa = moeda.ativa
                    if estava_ativa:
                        messages.warning(request, f'Moeda "{nome_moeda}" estava ativa e foi removida.')
                    moeda.delete()
                    log_action(logger, "wallet_coin_config", "moeda_excluida", nome=nome_moeda, estava_ativa=estava_ativa, staff=request.user.username)
                    messages.success(request, f'Moeda "{nome_moeda}" excluída com sucesso!')
                except CoinConfig.DoesNotExist:
                    messages.error(request, 'Moeda não encontrada.')
                except Exception as e:
                    messages.error(request, f'Erro ao excluir moeda: {str(e)}')
                
                return redirect("wallet:coin_config_panel")

    moedas = CoinConfig.objects.all().order_by("-ativa", "nome")
    context = {"moedas": moedas}
    return render(request, "configs/coin_config_panel.html", context)


@conditional_otp_required
def comprar_fichas_wallet(request):
    """
    View para comprar fichas usando saldo normal ou saldo bônus da wallet
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Valida quantidade
        quantidade_str = request.POST.get('quantidade', '0')
        origem_saldo = request.POST.get('origem_saldo', 'normal')  # 'normal' | 'bonus'
        
        try:
            quantidade = int(quantidade_str)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Quantidade inválida'}, status=400)
        
        if quantidade <= 0:
            return JsonResponse({'error': 'Quantidade deve ser maior que zero'}, status=400)
        
        if quantidade > 10000:  # Limite máximo de segurança
            return JsonResponse({'error': 'Quantidade máxima permitida é 10.000 fichas'}, status=400)
        
        valor_unitario = Decimal('0.10')  # 10 centavos por ficha
        total = valor_unitario * quantidade

        # Busca ou cria wallet
        wallet, created = Wallet.objects.get_or_create(usuario=request.user)

        # Validação de saldo conforme origem selecionada
        if origem_saldo == 'bonus':
            if wallet.saldo_bonus < total:
                return JsonResponse({'error': 'Saldo de bônus insuficiente'}, status=400)
            
            # Aplica transação de bônus
            try:
                aplicar_transacao_bonus(
                    wallet=wallet,
                    tipo='SAIDA',
                    valor=total,
                    descricao=f'{quantidade} ficha(s) comprada(s) com saldo bônus',
                    origem='Wallet',
                    destino='Sistema de Fichas'
                )
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'Erro ao processar transação: {str(e)}'}, status=500)
        else:
            if wallet.saldo < total:
                return JsonResponse({'error': 'Saldo insuficiente'}, status=400)
            
            # Aplica transação normal
            try:
                aplicar_transacao(
                    wallet=wallet,
                    tipo='SAIDA',
                    valor=total,
                    descricao=f'{quantidade} ficha(s) comprada(s)',
                    origem='Wallet',
                    destino='Sistema de Fichas'
                )
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'Erro ao processar transação: {str(e)}'}, status=500)

        # Credita as fichas
        try:
            request.user.fichas += quantidade
            request.user.save()
            
            # Registra compra no histórico de fichas
            TokenHistory.objects.create(
                user=request.user,
                transaction_type='purchase',
                game_type='purchase',
                amount=quantidade,
                description=f'Compra de {quantidade} ficha(s) usando {"saldo bônus" if origem_saldo == "bonus" else "saldo principal"}',
                metadata={
                    'quantity': quantidade, 
                    'total_cost': float(total), 
                    'cost_per_token': 0.10,
                    'balance_type': origem_saldo
                }
            )
            
            wallet.refresh_from_db()
            log_action(
                logger, "wallet_compra_fichas", "sucesso",
                username=request.user.username,
                quantidade=quantidade,
                total=str(total),
                origem_saldo=origem_saldo,
            )
            return JsonResponse({
                'success': True, 
                'fichas': request.user.fichas,
                'saldo': float(wallet.saldo),
                'saldo_bonus': float(wallet.saldo_bonus)
            })
        except Exception as e:
            return JsonResponse({'error': f'Erro ao creditar fichas: {str(e)}'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': f'Erro inesperado: {str(e)}'}, status=500)
