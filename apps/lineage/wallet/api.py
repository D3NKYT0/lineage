"""
API interna para processamento de transferências de wallet.
Esta API é chamada internamente para evitar timeouts no worker do Gunicorn.
"""
import logging
import hashlib
import time
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.throttling import UserRateThrottle
from apps.main.home.decorator import conditional_otp_required
from .models import Wallet, CoinConfig
from .signals import aplicar_transacao, aplicar_transacao_bonus
from apps.lineage.server.database import LineageDB
from apps.lineage.server.services.account_context import get_active_login
from apps.main.home.models import PerfilGamer, User
from utils.dynamic_import import get_query_class
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate

from core.log_utils import log_action
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)

TransferFromWalletToChar = get_query_class("TransferFromWalletToChar")


def process_transfer_to_server(user, nome_personagem, valor, origem_saldo, active_login, senha=None, skip_duplicate_check=False):
    """
    Função helper para processar transferência de wallet para o servidor.
    Pode ser chamada tanto pela API quanto pela view diretamente.
    
    Parâmetros:
    - user: usuário autenticado
    - nome_personagem: nome do personagem
    - valor: valor em Decimal
    - origem_saldo: 'normal' ou 'bonus'
    - active_login: login da conta do Lineage
    - senha: senha do usuário (opcional, se None não valida)
    - skip_duplicate_check: se True, pula verificação de duplicatas (já feita na API)
    
    Retorna dict com 'success' (bool) e 'message' ou 'error' (str).
    """
    try:
        # Validação básica
        if not nome_personagem:
            return {'success': False, 'error': 'Personagem não informado.'}

        if valor < 1 or valor > 1000:
            return {'success': False, 'error': 'Só é permitido transferir entre R$1,00 e R$1.000,00.'}
        
        # Validação de senha (se fornecida)
        if senha:
            from django.contrib.auth import authenticate
            authenticated_user = authenticate(username=user.username, password=senha)
            if not authenticated_user:
                logger.warning(f"Tentativa de transferência com senha incorreta (usuário: {user.username})")
                return {'success': False, 'error': 'Senha incorreta.'}

        # Validação de configuração
        config = CoinConfig.objects.filter(ativa=True).first()
        if not config:
            return {'success': False, 'error': 'Nenhuma moeda configurada está ativa no momento.'}

        COIN_ID = config.coin_id
        multiplicador = config.multiplicador

        if origem_saldo == 'bonus':
            if not getattr(config, 'habilitar_transferencia_com_bonus', False):
                return {'success': False, 'error': 'Transferência usando saldo bônus está desabilitada.'}

        # Validação no banco do Lineage
        db = LineageDB()
        if not db.is_connected():
            logger.error(f"Banco do Lineage desconectado durante transferência (usuário: {user.username})")
            return {'success': False, 'error': 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.'}

        # Confirma se o personagem pertence à conta
        personagem = TransferFromWalletToChar.find_char(active_login, nome_personagem)
        if not personagem:
            logger.warning(f"Tentativa de transferência para personagem inválido: {nome_personagem} (usuário: {user.username})")
            return {'success': False, 'error': 'Personagem inválido ou não pertence a essa conta.'}

        if not TransferFromWalletToChar.items_delayed:
            if personagem[0].get('online', 0) != 0:
                return {'success': False, 'error': 'O personagem precisa estar offline.'}

        # Gera chaves de cache (sempre necessário para marcar como completo)
        request_hash_data = f"{user.id}:{nome_personagem}:{valor}:{origem_saldo}"
        request_hash = hashlib.md5(request_hash_data.encode()).hexdigest()
        cache_key = f"wallet_transfer_{user.id}_{request_hash}"
        cache_lock_key = f"wallet_transfer_lock_{user.id}_{request_hash}"

        # Proteção contra requisições duplicadas (apenas se não foi verificado antes)
        if not skip_duplicate_check:
            cache_data = cache.get(cache_key)
            if cache_data:
                if isinstance(cache_data, dict) and cache_data.get('status') == 'processing':
                    elapsed = time.time() - cache_data.get('started_at', 0)
                    if elapsed < 300:
                        logger.info(f"Transferência duplicada bloqueada: {cache_key} (usuário: {user.username})")
                        return {'success': False, 'error': 'Esta transferência já está sendo processada. Aguarde alguns instantes.'}

            lock_acquired = cache.add(cache_lock_key, True, timeout=10)
            if not lock_acquired:
                return {'success': False, 'error': 'Outra transferência está sendo processada. Aguarde alguns instantes.'}
            
            # Marca como processando
            cache.set(cache_key, {
                'status': 'processing',
                'started_at': time.time(),
                'user_id': user.id,
                'valor': str(valor),
                'personagem': nome_personagem
            }, timeout=300)
        # Se skip_duplicate_check=True, assume que lock e cache já foram configurados na API

        # Flag para controlar se a transação foi commitada e precisa reversão em caso de erro
        transacao_commitada = False
        
        try:
            # Processamento da transferência
            quantidade_moedas = Decimal(valor) * Decimal(multiplicador)
            amount = int(round(quantidade_moedas))

            logger.info(f"Iniciando transferência: usuário={user.username}, personagem={nome_personagem}, valor={valor}, moedas={amount}")

            # Transação atômica
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(usuario=user)

                if origem_saldo == 'bonus':
                    if wallet.saldo_bonus < valor:
                        raise ValueError(_('Saldo bônus insuficiente.'))
                else:
                    if wallet.saldo < valor:
                        raise ValueError(_('Saldo insuficiente.'))

                if origem_saldo == 'bonus':
                    aplicar_transacao_bonus(
                        wallet=wallet,
                        tipo="SAIDA",
                        valor=valor,
                        descricao="Transferência para o servidor (bônus)",
                        origem=active_login,
                        destino=nome_personagem
                    )
                else:
                    aplicar_transacao(
                        wallet=wallet,
                        tipo="SAIDA",
                        valor=valor,
                        descricao="Transferência para o servidor",
                        origem=active_login,
                        destino=nome_personagem
                    )
            
            # Marca que a transação foi commitada (saiu do with transaction.atomic())
            transacao_commitada = True

            # Inserção no banco do Lineage
            # force_stackable=True porque itens de donate sempre devem ser acumuláveis
            try:
                sucesso = TransferFromWalletToChar.insert_coin(
                    char_name=nome_personagem,
                    coin_id=COIN_ID,
                    amount=amount,
                    force_stackable=True  # Itens de donate sempre são acumuláveis
                )

                if not sucesso:
                    logger.error(f"Falha ao inserir moedas no Lineage: personagem={nome_personagem}, amount={amount}")
                    # Verifica se o item foi entregue antes de reverter
                    revertido = _reverter_transacao(user, valor, origem_saldo, active_login, nome_personagem, coin_id=COIN_ID, amount=amount)
                    if revertido:
                        transacao_commitada = False  # Já revertida
                        return {'success': False, 'error': 'Erro ao adicionar a moeda ao personagem. O valor foi revertido.'}
                    else:
                        # Item foi entregue, não reverteu
                        return {'success': False, 'error': 'Erro ao confirmar inserção, mas o item pode ter sido entregue. Verifique no jogo.'}

            except Exception as lineage_error:
                logger.error(f"Erro ao inserir moedas no Lineage: {str(lineage_error)} (usuário: {user.username})")
                # Verifica se o item foi entregue antes de reverter
                revertido = _reverter_transacao(user, valor, origem_saldo, active_login, nome_personagem, coin_id=COIN_ID, amount=amount)
                if revertido:
                    transacao_commitada = False  # Já revertida
                    return {'success': False, 'error': 'Erro ao adicionar a moeda ao personagem. O valor foi revertido automaticamente.'}
                else:
                    # Item foi entregue, não reverteu
                    return {'success': False, 'error': 'Erro ao confirmar inserção, mas o item pode ter sido entregue. Verifique no jogo.'}

            # Sucesso - marca como completo ANTES de qualquer outra operação
            cache.set(cache_key, {
                'status': 'completed',
                'completed_at': time.time(),
                'user_id': user.id,
                'valor': str(valor),
                'personagem': nome_personagem
            }, timeout=300)
            
            # Marca que completou com sucesso (para o finally não tentar reverter)
            transacao_commitada = False  # Reset para indicar que foi completada

            perfil, created = PerfilGamer.objects.get_or_create(user=user)
            perfil.adicionar_xp(40)

            log_action(
                logger, "wallet_transfer_servidor", "sucesso",
                username=user.username,
                personagem=nome_personagem,
                valor=str(valor),
                origem_saldo=origem_saldo,
                moedas=amount,
            )

            # Notifica staff (push) sobre envio para o servidor
            try:
                from django.urls import reverse
                from utils.push import send_push_to_staff_for_event, EVENT_ADMIN_ENVIOS_SERVIDOR
                send_push_to_staff_for_event(
                    EVENT_ADMIN_ENVIOS_SERVIDOR,
                    username=user.username,
                    valor=str(valor),
                    personagem=nome_personagem,
                    url=reverse('wallet:transfer_to_server'),
                    async_send=True,
                )
            except Exception:
                pass

            message = f"R${valor:.2f} transferidos com sucesso para o personagem {nome_personagem}." if origem_saldo == 'normal' else f"R${valor:.2f} do bônus transferidos com sucesso para o personagem {nome_personagem}."
            
            return {
                'success': True,
                'message': message,
                'valor': float(valor),
                'personagem': nome_personagem,
                'moedas': amount
            }

        except ValueError as ve:
            logger.warning(f"Erro de validação na transferência: {str(ve)} (usuário: {user.username})")
            cache.delete(cache_key)
            # Não precisa reverter se a transação não foi commitada (erro de validação)
            return {'success': False, 'error': str(ve)}

        except Exception as e:
            logger.error(f"Erro durante transferência: {str(e)} (usuário: {user.username}, personagem: {nome_personagem})", exc_info=True)
            cache.delete(cache_key)
            
            # Se a transação foi commitada mas deu erro depois, precisa verificar e possivelmente reverter
            if transacao_commitada:
                logger.warning(f"Transação commitada mas erro posterior detectado, verificando entrega antes de reverter... (usuário: {user.username})")
                try:
                    # Pega COIN_ID e amount do contexto (precisa estar disponível)
                    config = CoinConfig.objects.filter(ativa=True).first()
                    if config:
                        quantidade_moedas = Decimal(valor) * Decimal(config.multiplicador)
                        amount = int(round(quantidade_moedas))
                        revertido = _reverter_transacao(user, valor, origem_saldo, active_login, nome_personagem, coin_id=config.coin_id, amount=amount)
                        if revertido:
                            logger.info(f"Reversão executada com sucesso após erro (usuário: {user.username})")
                        else:
                            logger.warning(f"Reversão cancelada: item foi entregue (usuário: {user.username})")
                    else:
                        # Se não conseguir pegar config, reverte sem verificação (fallback)
                        logger.warning(f"Config não encontrada, revertendo sem verificação (usuário: {user.username})")
                        _reverter_transacao(user, valor, origem_saldo, active_login, nome_personagem)
                except Exception as revert_error:
                    logger.critical(f"ERRO CRÍTICO: Falha ao reverter transação após erro: {str(revert_error)} (usuário: {user.username})")
                    # Marca no cache para reversão manual posterior
                    cache.set(f"wallet_revert_pending_{user.id}_{int(time.time())}", {
                        'user_id': user.id,
                        'valor': str(valor),
                        'personagem': nome_personagem,
                        'origem_saldo': origem_saldo,
                        'error': str(e),
                        'revert_error': str(revert_error),
                        'timestamp': timezone.now().isoformat()
                    }, timeout=86400)  # 24 horas
            
            return {'success': False, 'error': f'Ocorreu um erro durante a transferência: {str(e)}'}

        finally:
            # Se a transação foi commitada mas não completou com sucesso, tenta reverter
            # Isso garante reversão mesmo se o worker for morto antes do except
            if transacao_commitada:
                # Verifica se o cache ainda está como "processing" (não foi marcado como "completed")
                cache_data = cache.get(cache_key)
                if cache_data and isinstance(cache_data, dict):
                    if cache_data.get('status') != 'completed':
                        logger.warning(f"Transferência não completada, verificando entrega antes de reverter no finally (usuário: {user.username})")
                        try:
                            # Tenta pegar COIN_ID e amount do contexto
                            config = CoinConfig.objects.filter(ativa=True).first()
                            if config:
                                quantidade_moedas = Decimal(valor) * Decimal(config.multiplicador)
                                amount = int(round(quantidade_moedas))
                                revertido = _reverter_transacao(user, valor, origem_saldo, active_login, nome_personagem, coin_id=config.coin_id, amount=amount)
                                if revertido:
                                    logger.info(f"Reversão executada no finally com sucesso (usuário: {user.username})")
                                else:
                                    logger.warning(f"Reversão cancelada no finally: item foi entregue (usuário: {user.username})")
                            else:
                                # Fallback: reverte sem verificação
                                _reverter_transacao(user, valor, origem_saldo, active_login, nome_personagem)
                                logger.info(f"Reversão executada no finally (fallback, sem verificação) (usuário: {user.username})")
                        except Exception as revert_error:
                            logger.critical(f"ERRO CRÍTICO: Falha ao reverter no finally: {str(revert_error)} (usuário: {user.username})")
            
            # Libera o lock apenas se foi adquirido nesta função
            if not skip_duplicate_check:
                cache.delete(cache_lock_key)

    except Exception as e:
        logger.error(f"Erro crítico na função de transferência: {str(e)}", exc_info=True)
        return {'success': False, 'error': 'Erro interno do servidor. Tente novamente mais tarde.'}


def _verificar_item_entregue(nome_personagem, coin_id, amount):
    """
    Verifica se o item foi realmente entregue no banco do Lineage.
    Retorna True se o item foi entregue, False caso contrário.
    """
    try:
        db = LineageDB()
        if not db.is_connected():
            logger.warning(f"Não foi possível verificar entrega: banco Lineage desconectado")
            # Se não conseguir verificar, assume que NÃO foi entregue (mais seguro)
            return False
        
        # Busca o char_id do personagem usando search_coin (que busca por nome)
        # Alternativamente, podemos buscar diretamente na tabela characters
        char_result = TransferFromWalletToChar.search_coin(nome_personagem, coin_id)
        if not char_result:
            # Se não encontrou na tabela items, tenta buscar o personagem diretamente
            # para pegar o char_id
            try:
                # Busca personagem na tabela characters (find_char precisa de account, mas podemos usar select direto)
                char_query = "SELECT obj_Id, charId, char_id FROM characters WHERE char_name = :char_name LIMIT 1"
                char_result = db.select(char_query, {"char_name": nome_personagem})
                if not char_result:
                    logger.warning(f"Personagem {nome_personagem} não encontrado para verificação")
                    return False
            except Exception as e:
                logger.error(f"Erro ao buscar personagem para verificação: {str(e)}")
                return False
        
        # Se encontrou na search_coin, já tem o owner_id
        if char_result and len(char_result) > 0:
            char_id = char_result[0].get('owner_id') or char_result[0].get('obj_Id') or char_result[0].get('charId') or char_result[0].get('char_id')
        else:
            # Se não encontrou na search_coin, usa o resultado da query direta
            char_id = char_result[0].get('obj_Id') or char_result[0].get('charId') or char_result[0].get('char_id')
        
        if not char_id:
            logger.warning(f"Não foi possível obter char_id do personagem {nome_personagem}")
            return False
        
        # Flag para indicar se item foi processado em items_delayed
        item_processado_items_delayed = False
        
        # Verifica se usa items_delayed
        if TransferFromWalletToChar.items_delayed:
            # Verifica na tabela items_delayed se há item recente
            # O servidor processa items_delayed e atualiza payment_status quando entrega
            try:
                # Detecta as colunas da tabela items_delayed
                columns = db.get_table_columns("items_delayed")
                
                # Identifica as colunas (podem variar entre schemas)
                owner_id_col = None
                item_id_col = None
                payment_status_col = None
                payment_id_col = None
                description_col = None
                
                for col in columns:
                    col_lower = col.lower()
                    if col_lower in ['owner_id', 'ownerid', 'char_id', 'charid']:
                        owner_id_col = col
                    elif col_lower in ['item_id', 'itemid', 'item_type']:
                        item_id_col = col
                    elif col_lower in ['payment_status', 'paymentstatus', 'status']:
                        payment_status_col = col
                    elif col_lower in ['payment_id', 'paymentid', 'id']:
                        payment_id_col = col
                    elif col_lower in ['description', 'desc']:
                        description_col = col
                
                if owner_id_col and item_id_col:
                    # Busca itens recentes na items_delayed para este personagem e moeda
                    # Verifica itens inseridos nos últimos 10 minutos (janela de segurança)
                    query_params = {
                        "owner_id": char_id,
                        "coin_id": coin_id
                    }
                    
                    # Monta query baseada nas colunas disponíveis
                    where_conditions = [f"{owner_id_col} = :owner_id", f"{item_id_col} = :coin_id"]
                    
                    # Se tem description, filtra por 'DONATE WEB' para garantir que é nossa inserção
                    if description_col:
                        where_conditions.append(f"{description_col} = 'DONATE WEB'")
                    
                    query = f"""
                        SELECT {payment_id_col or '*'} as payment_id, 
                               {payment_status_col or 'NULL'} as payment_status,
                               {item_id_col} as item_id,
                               count
                        FROM items_delayed
                        WHERE {' AND '.join(where_conditions)}
                        ORDER BY {payment_id_col or 'payment_id'} DESC
                        LIMIT 10
                    """
                    
                    items_delayed_result = db.select(query, query_params)
                    
                    if items_delayed_result:
                        # Verifica se algum item foi processado (payment_status != 0)
                        # Normalmente: 0 = pendente, 1 = processado/entregue
                        for item in items_delayed_result:
                            payment_status = item.get('payment_status') or item.get('paymentStatus') or 0
                            item_count = item.get('count', 0)
                            
                            # Se payment_status indica que foi processado (normalmente 1 ou > 0)
                            if payment_status != 0 and payment_status is not None:
                                logger.info(
                                    f"✅ Item encontrado em items_delayed com payment_status={payment_status} "
                                    f"(processado/entregue) para personagem {nome_personagem}, count={item_count}"
                                )
                                # Marca que foi processado, mas ainda verifica no inventário para confirmar
                                item_processado_items_delayed = True
                                break  # Encontrou um processado, não precisa verificar mais
                            elif payment_status == 0:
                                # Item ainda pendente na items_delayed
                                logger.info(
                                    f"⏳ Item encontrado em items_delayed mas ainda pendente "
                                    f"(payment_status=0) para personagem {nome_personagem}, count={item_count}"
                                )
                                # Continua verificando no inventário também (pode ter sido processado mas ainda não atualizado o status)
                    
                    if not items_delayed_result:
                        logger.info(f"Nenhum item encontrado em items_delayed para personagem {nome_personagem}, coin_id={coin_id}")
                    
                    # Se encontrou item processado em items_delayed, ainda verifica no inventário
                    # para ter certeza absoluta antes de retornar True
                    if item_processado_items_delayed:
                        logger.info(f"Item processado em items_delayed detectado, verificando inventário para confirmar...")
                    
            except Exception as e:
                logger.warning(f"Erro ao verificar items_delayed: {str(e)}. Continuando verificação no inventário...")
                # Continua para verificar no inventário mesmo se der erro
        
        # Verifica se o item já está no inventário/warehouse do personagem
        # Esta é a verificação final e mais confiável
        from utils.dynamic_import import get_query_class
        TransferFromCharToWallet = get_query_class("TransferFromCharToWallet")
        coin_info = TransferFromCharToWallet.check_ingame_coin(coin_id, char_id)
        
        if coin_info:
            total_coins = coin_info.get('total', 0)
            logger.info(f"Verificação de entrega (inventário): personagem {nome_personagem} tem {total_coins} moedas (coin_id: {coin_id}, esperado: {amount})")
            
            # IMPORTANTE: Esta verificação considera:
            # 1. Se usa items_delayed: o item pode estar pendente (payment_status=0) mas já processado e no inventário
            # 2. O personagem pode já ter moedas pré-existentes
            # 
            # Por segurança, vamos usar uma abordagem conservadora:
            # - Se encontrou moedas E a quantidade é >= ao que tentamos inserir, assume que foi entregue
            # - Caso contrário, assume que NÃO foi entregue (mais seguro)
            
            if total_coins >= amount:
                # Quantidade encontrada é maior ou igual ao esperado
                # Se também foi processado em items_delayed, é certeza absoluta
                if item_processado_items_delayed:
                    logger.info(
                        f"✅✅ Entrega CONFIRMADA (items_delayed + inventário): personagem tem {total_coins} moedas "
                        f"(>= {amount} esperadas). Item foi entregue com certeza."
                    )
                else:
                    logger.warning(
                        f"✅ Entrega confirmada no inventário: personagem tem {total_coins} moedas "
                        f"(>= {amount} esperadas). Item foi entregue."
                    )
                return True
            elif total_coins > 0:
                # Tem algumas moedas, mas menos que o esperado
                # Pode ser moedas pré-existentes ou entrega parcial
                # Por segurança, assume que NÃO foi totalmente entregue
                logger.info(
                    f"⚠️ Moedas encontradas ({total_coins}) mas menos que esperado ({amount}). "
                    f"Pode ser moedas pré-existentes. Assumindo que NÃO foi entregue completamente."
                )
                return False
            else:
                # Não encontrou moedas no inventário
                logger.info(f"❌ Nenhuma moeda encontrada no inventário para personagem {nome_personagem}")
                return False
        
        # Se não encontrou moedas, provavelmente não foi entregue
        logger.info(f"❌ Verificação de entrega: personagem {nome_personagem} NÃO tem moedas no inventário (coin_id: {coin_id})")
        return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar se item foi entregue: {str(e)}")
        # Em caso de erro na verificação, assume que NÃO foi entregue (mais seguro)
        return False


def _reverter_transacao(user, valor, origem_saldo, active_login, nome_personagem, coin_id=None, amount=None):
    """
    Reverte uma transação em caso de erro no Lineage.
    
    IMPORTANTE: Antes de reverter, verifica se o item foi realmente entregue no banco do Lineage.
    Se foi entregue, NÃO reverte o saldo (para evitar duplicação).
    Se NÃO foi entregue, reverte o saldo.
    
    Parâmetros:
    - coin_id: ID da moeda (opcional, usado para verificação)
    - amount: Quantidade de moedas (opcional, usado para verificação)
    """
    # Se temos informações da moeda, verifica se foi entregue ANTES de reverter
    if coin_id is not None and amount is not None:
        logger.info(f"Verificando se item foi entregue antes de reverter (usuário: {user.username}, personagem: {nome_personagem})")
        item_entregue = _verificar_item_entregue(nome_personagem, coin_id, amount)
        
        if item_entregue:
            logger.warning(
                f"⚠️ REVERSÃO CANCELADA: Item foi entregue no Lineage! "
                f"Usuário: {user.username}, Personagem: {nome_personagem}, "
                f"Coin ID: {coin_id}, Amount: {amount}. "
                f"Não revertendo saldo para evitar duplicação."
            )
            # Marca no cache para análise manual
            cache.set(f"wallet_no_revert_item_delivered_{user.id}_{int(time.time())}", {
                'user_id': user.id,
                'valor': str(valor),
                'personagem': nome_personagem,
                'origem_saldo': origem_saldo,
                'coin_id': coin_id,
                'amount': amount,
                'reason': 'Item foi entregue no Lineage, reversão cancelada para evitar duplicação',
                'timestamp': timezone.now().isoformat()
            }, timeout=86400)  # 24 horas
            return False  # Não reverteu
    
    # Se chegou aqui, o item NÃO foi entregue (ou não foi possível verificar)
    # Pode reverter o saldo com segurança
    try:
        logger.info(f"Revertendo transação (usuário: {user.username}, valor: {valor})")
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(usuario=user)
            if origem_saldo == 'bonus':
                aplicar_transacao_bonus(
                    wallet=wallet,
                    tipo="ENTRADA",
                    valor=valor,
                    descricao="Reversão: Erro ao transferir para servidor (bônus)",
                    origem=nome_personagem,
                    destino=active_login
                )
            else:
                aplicar_transacao(
                    wallet=wallet,
                    tipo="ENTRADA",
                    valor=valor,
                    descricao="Reversão: Erro ao transferir para servidor",
                    origem=nome_personagem,
                    destino=active_login
                )
        logger.info(f"Reversão executada com sucesso (usuário: {user.username})")
        return True
    except Exception as revert_error:
        logger.critical(f"ERRO CRÍTICO: Falha ao reverter transação após erro no Lineage: {str(revert_error)} (usuário: {user.username}, valor: {valor})")
        cache.set(f"wallet_revert_error_{user.id}_{int(time.time())}", {
            'user_id': user.id,
            'valor': str(valor),
            'personagem': nome_personagem,
            'origem_saldo': origem_saldo,
            'revert_error': str(revert_error),
            'timestamp': timezone.now().isoformat()
        }, timeout=86400)
        return False


class WalletTransferThrottle(UserRateThrottle):
    """
    Throttle customizado para transferências de wallet.
    Limite: 1 requisição por minuto por usuário.
    """
    rate = '1/minute'
    scope = 'wallet_transfer'


@extend_schema(exclude=True)
class InternalTransferToServerAPI(APIView):
    """
    API interna para processar transferências de wallet para o servidor.
    Esta API é chamada internamente e pode ter timeout maior.
    Aceita autenticação via sessão ou JWT.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]  # Aceita autenticação via sessão
    throttle_classes = [WalletTransferThrottle]  # Rate limit: 1 requisição por minuto
    
    def dispatch(self, request, *args, **kwargs):
        # Garante que o usuário está autenticado via sessão
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Autenticação necessária.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        Processa transferência de wallet para o servidor.
        
        Parâmetros esperados:
        - personagem: nome do personagem
        - valor: valor em R$ (Decimal)
        - origem_saldo: 'normal' ou 'bonus'
        - senha: senha do usuário
        """
        try:
            # ========== FASE 1: VALIDAÇÃO E SANITIZAÇÃO DOS DADOS ==========
            # Tenta obter dados do request.data (DRF JSON) ou request.POST (form)
            try:
                if hasattr(request, 'data') and request.data:
                    data_source = request.data
                else:
                    # Se não tem data, tenta POST (form data)
                    data_source = request.POST if hasattr(request, 'POST') else {}
            except Exception as parse_error:
                logger.error(f"Erro ao parsear dados da requisição: {str(parse_error)}")
                return Response(
                    {'error': 'Erro ao processar dados da requisição.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            nome_personagem = data_source.get('personagem', '').strip() if isinstance(data_source, dict) else ''
            valor_str = data_source.get('valor', '').strip() if isinstance(data_source, dict) else ''
            origem_saldo = data_source.get('origem_saldo', 'normal') if isinstance(data_source, dict) else 'normal'
            senha = data_source.get('senha', '') if isinstance(data_source, dict) else ''

            if not nome_personagem:
                return Response(
                    {'error': 'Personagem não informado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                valor = Decimal(valor_str)
            except (ValueError, TypeError, InvalidOperation):
                logger.warning(f"Tentativa de transferência com valor inválido: {valor_str} (usuário: {request.user.username})")
                return Response(
                    {'error': 'Valor inválido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if valor < 1 or valor > 1000:
                return Response(
                    {'error': 'Só é permitido transferir entre R$1,00 e R$1.000,00.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validação de senha
            from django.contrib.auth import authenticate
            user = authenticate(username=request.user.username, password=senha)
            if not user:
                logger.warning(f"Tentativa de transferência com senha incorreta (usuário: {request.user.username})")
                return Response(
                    {'error': 'Senha incorreta.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ========== FASE 2: VALIDAÇÃO DE CONFIGURAÇÃO ==========
            config = CoinConfig.objects.filter(ativa=True).first()
            if not config:
                return Response(
                    {'error': 'Nenhuma moeda configurada está ativa no momento.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            COIN_ID = config.coin_id
            multiplicador = config.multiplicador

            if origem_saldo == 'bonus':
                if not getattr(config, 'habilitar_transferencia_com_bonus', False):
                    return Response(
                        {'error': 'Transferência usando saldo bônus está desabilitada.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            active_login = get_active_login(request)

            # ========== FASE 3: VALIDAÇÃO NO BANCO DO LINEAGE ==========
            db = LineageDB()
            if not db.is_connected():
                logger.error(f"Banco do Lineage desconectado durante transferência (usuário: {request.user.username})")
                return Response(
                    {'error': 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Confirma se o personagem pertence à conta
            personagem = TransferFromWalletToChar.find_char(active_login, nome_personagem)
            if not personagem:
                logger.warning(f"Tentativa de transferência para personagem inválido: {nome_personagem} (usuário: {request.user.username})")
                return Response(
                    {'error': 'Personagem inválido ou não pertence a essa conta.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not TransferFromWalletToChar.items_delayed:
                if personagem[0].get('online', 0) != 0:
                    return Response(
                        {'error': 'O personagem precisa estar offline.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # ========== FASE 4: PROTEÇÃO CONTRA REQUISIÇÕES DUPLICADAS ==========
            request_hash_data = f"{request.user.id}:{nome_personagem}:{valor}:{origem_saldo}"
            request_hash = hashlib.md5(request_hash_data.encode()).hexdigest()
            cache_key = f"wallet_transfer_{request.user.id}_{request_hash}"
            cache_lock_key = f"wallet_transfer_lock_{request.user.id}_{request_hash}"

            # Verifica se esta requisição idêntica já está sendo processada
            cache_data = cache.get(cache_key)
            if cache_data:
                if isinstance(cache_data, dict) and cache_data.get('status') == 'processing':
                    elapsed = time.time() - cache_data.get('started_at', 0)
                    if elapsed < 300:  # 5 minutos
                        logger.info(f"Transferência duplicada bloqueada: {cache_key} (usuário: {request.user.username})")
                        return Response(
                            {'error': 'Esta transferência já está sendo processada. Aguarde alguns instantes.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )

            # Tenta adquirir lock
            lock_acquired = cache.add(cache_lock_key, True, timeout=10)
            if not lock_acquired:
                return Response(
                    {'error': 'Outra transferência está sendo processada. Aguarde alguns instantes.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            try:
                # Marca como em processamento
                cache.set(cache_key, {
                    'status': 'processing',
                    'started_at': time.time(),
                    'user_id': request.user.id,
                    'valor': str(valor),
                    'personagem': nome_personagem
                }, timeout=300)

                # ========== FASE 5: PROCESSAMENTO DA TRANSFERÊNCIA ==========
                # Usa a função helper para processar (skip_duplicate_check=True porque já verificamos acima)
                result = process_transfer_to_server(
                    user=request.user,
                    nome_personagem=nome_personagem,
                    valor=valor,
                    origem_saldo=origem_saldo,
                    active_login=active_login,
                    senha=senha,
                    skip_duplicate_check=True  # Já verificamos duplicatas acima
                )

                if result.get('success'):
                    # Libera o lock antes de retornar sucesso
                    cache.delete(cache_lock_key)
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    # Libera o lock antes de retornar erro
                    cache.delete(cache_lock_key)
                    status_code = status.HTTP_400_BAD_REQUEST if 'insuficiente' in result.get('error', '').lower() or 'inválido' in result.get('error', '').lower() else status.HTTP_500_INTERNAL_SERVER_ERROR
                    return Response({'error': result.get('error')}, status=status_code)

            except ValueError as ve:
                logger.warning(f"Erro de validação na transferência: {str(ve)} (usuário: {request.user.username})")
                cache.delete(cache_key)
                cache.delete(cache_lock_key)
                return Response(
                    {'error': str(ve)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except Exception as e:
                logger.error(f"Erro durante transferência: {str(e)} (usuário: {request.user.username}, personagem: {nome_personagem})", exc_info=True)
                cache.delete(cache_key)
                cache.delete(cache_lock_key)
                return Response(
                    {'error': f'Ocorreu um erro durante a transferência: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except ValueError as ve:
            # Erro de validação (ex: Decimal inválido)
            logger.warning(f"Erro de validação na API: {str(ve)} (usuário: {request.user.username if hasattr(request, 'user') else 'unknown'})")
            return Response(
                {'error': f'Erro de validação: {str(ve)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log completo do erro para debug
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Erro crítico na API de transferência: {str(e)}\n{error_traceback}")
            return Response(
                {'error': 'Erro interno do servidor. Tente novamente mais tarde.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def process_transfer_to_player(user, nome_jogador, valor, senha=None, skip_duplicate_check=False):
    """
    Função helper para processar transferência de wallet entre jogadores.
    Pode ser chamada tanto pela API quanto pela view diretamente.
    
    Parâmetros:
    - user: usuário autenticado (remetente)
    - nome_jogador: nome do jogador destinatário
    - valor: valor em Decimal
    - senha: senha do usuário (opcional, se None não valida)
    - skip_duplicate_check: se True, pula verificação de duplicatas (já feita na API)
    
    Retorna dict com 'success' (bool) e 'message' ou 'error' (str).
    """
    try:
        # Validação básica
        if not nome_jogador:
            return {'success': False, 'error': 'Jogador não informado.'}

        if valor < 1 or valor > 1000:
            return {'success': False, 'error': 'Só é permitido transferir entre R$1,00 e R$1.000,00.'}
        
        # Validação de senha (se fornecida)
        if senha:
            authenticated_user = authenticate(username=user.username, password=senha)
            if not authenticated_user:
                logger.warning(f"Tentativa de transferência com senha incorreta (usuário: {user.username})")
                return {'success': False, 'error': 'Senha incorreta.'}

        # Verifica se o destinatário existe
        try:
            destinatario = User.objects.get(username=nome_jogador)
        except User.DoesNotExist:
            logger.warning(f"Tentativa de transferência para jogador inexistente: {nome_jogador} (usuário: {user.username})")
            return {'success': False, 'error': 'Jogador não encontrado.'}

        if destinatario == user:
            return {'success': False, 'error': 'Você não pode transferir para si mesmo.'}

        # Gera chaves de cache
        request_hash_data = f"{user.id}:{nome_jogador}:{valor}"
        request_hash = hashlib.md5(request_hash_data.encode()).hexdigest()
        cache_key = f"wallet_transfer_player_{user.id}_{request_hash}"
        cache_lock_key = f"wallet_transfer_player_lock_{user.id}_{request_hash}"

        # Proteção contra requisições duplicadas (apenas se não foi verificado antes)
        if not skip_duplicate_check:
            cache_data = cache.get(cache_key)
            if cache_data:
                if isinstance(cache_data, dict) and cache_data.get('status') == 'processing':
                    elapsed = time.time() - cache_data.get('started_at', 0)
                    if elapsed < 300:
                        logger.info(f"Transferência duplicada bloqueada: {cache_key} (usuário: {user.username})")
                        return {'success': False, 'error': 'Esta transferência já está sendo processada. Aguarde alguns instantes.'}

            lock_acquired = cache.add(cache_lock_key, True, timeout=10)
            if not lock_acquired:
                return {'success': False, 'error': 'Outra transferência está sendo processada. Aguarde alguns instantes.'}
            
            # Marca como processando
            cache.set(cache_key, {
                'status': 'processing',
                'started_at': time.time(),
                'user_id': user.id,
                'valor': str(valor),
                'jogador': nome_jogador
            }, timeout=300)
        # Se skip_duplicate_check=True, assume que lock e cache já foram configurados na API

        try:
            logger.info(f"Iniciando transferência entre jogadores: remetente={user.username}, destinatário={nome_jogador}, valor={valor}")

            # Garante que as carteiras existam
            wallet_origem, created = Wallet.objects.get_or_create(usuario=user)
            wallet_destino, created = Wallet.objects.get_or_create(usuario=destinatario)

            # Transação atômica
            with transaction.atomic():
                # Bloqueia ambas as carteiras para prevenir race conditions
                wallet_origem = Wallet.objects.select_for_update().get(id=wallet_origem.id)
                wallet_destino = Wallet.objects.select_for_update().get(id=wallet_destino.id)
                
                # Valida saldo dentro da transação (com lock)
                if wallet_origem.saldo < valor:
                    raise ValueError(_('Saldo insuficiente.'))

                # Aplica transações
                aplicar_transacao(
                    wallet=wallet_origem,
                    tipo="SAIDA",
                    valor=valor,
                    descricao=f"Transferência para {destinatario.username}",
                    origem=user.username,
                    destino=destinatario.username
                )

                aplicar_transacao(
                    wallet=wallet_destino,
                    tipo="ENTRADA",
                    valor=valor,
                    descricao=f"Transferência de {user.username}",
                    origem=user.username,
                    destino=destinatario.username
                )

            # Sucesso
            cache.set(cache_key, {
                'status': 'completed',
                'completed_at': time.time(),
                'user_id': user.id,
                'valor': str(valor),
                'jogador': nome_jogador
            }, timeout=300)

            perfil, created = PerfilGamer.objects.get_or_create(user=user)
            perfil.adicionar_xp(40)

            log_action(
                logger, "wallet_transfer_p2p", "sucesso",
                remetente=user.username,
                destinatario=nome_jogador,
                valor=str(valor),
            )

            message = f"Transferência de R${valor:.2f} para {destinatario.username} realizada com sucesso."
            
            return {
                'success': True,
                'message': message,
                'valor': float(valor),
                'jogador': nome_jogador
            }

        except ValueError as ve:
            logger.warning(f"Erro de validação na transferência: {str(ve)} (usuário: {user.username})")
            cache.delete(cache_key)
            return {'success': False, 'error': str(ve)}

        except Exception as e:
            logger.error(f"Erro durante transferência: {str(e)} (usuário: {user.username}, jogador: {nome_jogador})", exc_info=True)
            cache.delete(cache_key)
            return {'success': False, 'error': f'Ocorreu um erro durante a transferência: {str(e)}'}

        finally:
            # Libera o lock apenas se foi adquirido nesta função
            if not skip_duplicate_check:
                cache.delete(cache_lock_key)

    except Exception as e:
        logger.error(f"Erro crítico na função de transferência entre jogadores: {str(e)}", exc_info=True)
        return {'success': False, 'error': 'Erro interno do servidor. Tente novamente mais tarde.'}


@extend_schema(exclude=True)
class InternalTransferToPlayerAPI(APIView):
    """
    API interna para processar transferências de wallet entre jogadores.
    Esta API é chamada pelo frontend via AJAX para evitar timeouts no worker do Gunicorn.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    throttle_classes = [WalletTransferThrottle]

    def dispatch(self, request, *args, **kwargs):
        """Garante que o usuário está autenticado antes de processar."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Usuário não autenticado.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        Processa uma transferência de wallet entre jogadores.
        
        Parâmetros esperados (JSON ou form-data):
        - jogador: nome do jogador destinatário
        - valor: valor da transferência (string ou número)
        - senha: senha do usuário (opcional)
        """
        try:
            # Parse dos dados (suporta JSON e form-data)
            if hasattr(request, 'data') and request.data:
                nome_jogador = request.data.get('jogador', '').strip()
                valor_str = request.data.get('valor', '')
                senha = request.data.get('senha', '').strip()
            else:
                nome_jogador = request.POST.get('jogador', '').strip()
                valor_str = request.POST.get('valor', '')
                senha = request.POST.get('senha', '').strip()

            # Validação inicial
            if not nome_jogador:
                return Response(
                    {'error': 'Jogador não informado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not valor_str:
                return Response(
                    {'error': 'Valor não informado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not senha:
                return Response(
                    {'error': 'Senha não informada.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Converte valor para Decimal
            try:
                valor = Decimal(str(valor_str))
            except (ValueError, InvalidOperation):
                return Response(
                    {'error': 'Valor inválido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Gera chaves de cache para verificação de duplicatas
            request_hash_data = f"{request.user.id}:{nome_jogador}:{valor}"
            request_hash = hashlib.md5(request_hash_data.encode()).hexdigest()
            cache_key = f"wallet_transfer_player_{request.user.id}_{request_hash}"
            cache_lock_key = f"wallet_transfer_player_lock_{request.user.id}_{request_hash}"

            # Verifica se já está processando
            cache_data = cache.get(cache_key)
            if cache_data:
                if isinstance(cache_data, dict) and cache_data.get('status') == 'processing':
                    elapsed = time.time() - cache_data.get('started_at', 0)
                    if elapsed < 300:
                        logger.info(f"Transferência duplicada bloqueada na API: {cache_key} (usuário: {request.user.username})")
                        return Response(
                            {'error': 'Esta transferência já está sendo processada. Aguarde alguns instantes.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )

            # Adquire lock
            lock_acquired = cache.add(cache_lock_key, True, timeout=10)
            if not lock_acquired:
                return Response(
                    {'error': 'Outra transferência está sendo processada. Aguarde alguns instantes.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Marca como processando
            cache.set(cache_key, {
                'status': 'processing',
                'started_at': time.time(),
                'user_id': request.user.id,
                'valor': str(valor),
                'jogador': nome_jogador
            }, timeout=300)

            try:
                # Chama a função helper
                result = process_transfer_to_player(
                    user=request.user,
                    nome_jogador=nome_jogador,
                    valor=valor,
                    senha=senha,
                    skip_duplicate_check=True  # Já verificamos duplicatas aqui
                )

                # Limpa o lock antes de retornar
                cache.delete(cache_lock_key)

                if result.get('success'):
                    return Response(
                        {
                            'success': True,
                            'message': result.get('message'),
                            'valor': result.get('valor'),
                            'jogador': result.get('jogador')
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': result.get('error', 'Erro desconhecido')},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except ValueError as ve:
                logger.warning(f"Erro de validação na transferência: {str(ve)} (usuário: {request.user.username})")
                cache.delete(cache_key)
                cache.delete(cache_lock_key)
                return Response(
                    {'error': str(ve)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except Exception as e:
                logger.error(f"Erro durante transferência: {str(e)} (usuário: {request.user.username}, jogador: {nome_jogador})", exc_info=True)
                cache.delete(cache_key)
                cache.delete(cache_lock_key)
                return Response(
                    {'error': f'Ocorreu um erro durante a transferência: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except ValueError as ve:
            # Erro de validação (ex: Decimal inválido)
            logger.warning(f"Erro de validação na API: {str(ve)} (usuário: {request.user.username if hasattr(request, 'user') else 'unknown'})")
            return Response(
                {'error': f'Erro de validação: {str(ve)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log completo do erro para debug
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Erro crítico na API de transferência entre jogadores: {str(e)}\n{error_traceback}")
            return Response(
                {'error': 'Erro interno do servidor. Tente novamente mais tarde.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

