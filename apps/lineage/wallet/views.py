from django.core.paginator import Paginator
from apps.main.home.decorator import conditional_otp_required
from .models import Wallet, TransacaoWallet, TransacaoBonus, CoinConfig
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import transferir_para_jogador
from decimal import Decimal
from django.contrib.auth import authenticate
from apps.main.home.models import User
from django.db import transaction, models
from .signals import aplicar_transacao
from apps.lineage.server.database import LineageDB
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods

from apps.main.home.models import PerfilGamer

from utils.dynamic_import import get_query_class
TransferFromWalletToChar = get_query_class("TransferFromWalletToChar")
LineageServices = get_query_class("LineageServices")

from django.utils.translation import gettext as _


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

    return render(request, 'wallet/dashboard.html', {
        'wallet': wallet,
        'transacoes': page_obj.object_list,
        'page_obj': page_obj,
    })


@conditional_otp_required
def transfer_to_server(request):

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
        personagens = LineageServices.find_chars(request.user.username)
    except:
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    if request.method == 'POST':
        nome_personagem = request.POST.get('personagem')
        valor = request.POST.get('valor')
        senha = request.POST.get('senha')

        COIN_ID = config.coin_id
        multiplicador = config.multiplicador

        try:
            valor = Decimal(valor)
        except:
            messages.error(request, 'Valor inválido.')
            return redirect('wallet:dashboard')

        if valor < 1 or valor > 1000:
            messages.error(request, 'Só é permitido transferir entre R$1,00 e R$1.000,00.')
            return redirect('wallet:dashboard')

        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect('wallet:dashboard')

        if wallet.saldo < valor:
            messages.error(request, 'Saldo insuficiente.')
            return redirect('wallet:dashboard')

        # Confirma se o personagem pertence à conta
        personagem = TransferFromWalletToChar.find_char(request.user.username, nome_personagem)
        if not personagem:
            messages.error(request, 'Personagem inválido ou não pertence a essa conta.')
            return redirect('wallet:dashboard')

        if not TransferFromWalletToChar.items_delayed:
            if personagem[0]['online'] != 0:
                messages.error(request, 'O personagem precisa estar offline.')
                return redirect('wallet:dashboard')

        try:
            with transaction.atomic():
                aplicar_transacao(
                    wallet=wallet,
                    tipo="SAIDA",
                    valor=valor,
                    descricao="Transferência para o servidor",
                    origem=request.user.username,
                    destino=nome_personagem
                )

                sucesso = TransferFromWalletToChar.insert_coin(
                    char_name=nome_personagem,
                    coin_id=COIN_ID,
                    amount=int(valor * multiplicador)
                )

                if not sucesso:
                    raise Exception(_("Erro ao adicionar a moeda ao personagem."))

        except Exception as e:
            messages.error(request, f"Ocorreu um erro durante a transferência: {str(e)}")
            return redirect('wallet:dashboard')

        perfil = PerfilGamer.objects.get(user=request.user)
        perfil.adicionar_xp(40)

        messages.success(request, f"R${valor:.2f} transferidos com sucesso para o personagem {nome_personagem}.")
        return redirect('wallet:dashboard')

    return render(request, 'wallet/transfer_to_server.html', {
        'wallet': wallet,
        'personagens': personagens,
    })


@conditional_otp_required
def transfer_to_player(request):
    if request.method == 'POST':
        nome_jogador = request.POST.get('jogador')
        valor = request.POST.get('valor')
        senha = request.POST.get('senha')

        try:
            valor = Decimal(valor)
        except:
            messages.error(request, 'Valor inválido.')
            return redirect('wallet:dashboard')

        # Verificação de limites
        if valor < 1 or valor > 1000:
            messages.error(request, 'Só é permitido transferir entre R$1,00 e R$1.000,00.')
            return redirect('wallet:dashboard')

        # Verificação de senha
        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect('wallet:dashboard')
        
        try:
            destinatario = User.objects.get(username=nome_jogador)
        except User.DoesNotExist:
            messages.error(request, 'Jogador não encontrado.')
            return redirect('wallet:dashboard')

        if destinatario == request.user:
            messages.error(request, 'Você não pode transferir para si mesmo.')
            return redirect('wallet:dashboard')

        wallet_origem, created = Wallet.objects.get_or_create(usuario=request.user)
        wallet_destino, created = Wallet.objects.get_or_create(usuario=destinatario)

        try:
            transferir_para_jogador(wallet_origem, wallet_destino, valor)
            messages.success(request, f'Transferência de R${valor:.2f} para {destinatario} realizada com sucesso.')

            perfil = PerfilGamer.objects.get(user=request.user)
            perfil.adicionar_xp(40)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Ocorreu um erro inesperado durante a transferência.")

        return redirect('wallet:dashboard')

    wallet, created = Wallet.objects.get_or_create(usuario=request.user)
    return render(request, 'wallet/transfer_to_player.html', {
        'wallet': wallet,
    })


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

            if nome and coin_id and multiplicador:
                try:
                    # Verifica se já existe uma moeda com este ID
                    if CoinConfig.objects.filter(coin_id=coin_id).exists():
                        messages.error(request, f'Já existe uma moeda configurada com o ID {coin_id}.')
                        return redirect("wallet:coin_config_panel")
                    
                    # Cria a nova moeda (ativa=False por padrão)
                    nova_moeda = CoinConfig.objects.create(
                        nome=nome,
                        coin_id=coin_id,
                        multiplicador=multiplicador,
                        ativa=False
                    )
                    messages.success(request, f'Moeda "{nova_moeda.nome}" criada com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar moeda: {str(e)}')
                
                return redirect("wallet:coin_config_panel")

        elif "delete_coin_id" in request.POST:
            coin_id = request.POST.get("delete_coin_id")
            if coin_id:
                try:
                    moeda = CoinConfig.objects.get(id=coin_id)
                    nome_moeda = moeda.nome
                    
                    # Verifica se é a moeda ativa
                    if moeda.ativa:
                        messages.warning(request, f'Moeda "{nome_moeda}" estava ativa e foi removida.')
                    
                    moeda.delete()
                    messages.success(request, f'Moeda "{nome_moeda}" excluída com sucesso!')
                except CoinConfig.DoesNotExist:
                    messages.error(request, 'Moeda não encontrada.')
                except Exception as e:
                    messages.error(request, f'Erro ao excluir moeda: {str(e)}')
                
                return redirect("wallet:coin_config_panel")

    moedas = CoinConfig.objects.all().order_by("-ativa", "nome")
    context = {"moedas": moedas}
    return render(request, "configs/coin_config_panel.html", context)
