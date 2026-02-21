# Logging no projeto PDL

> **Última atualização:** 21/02/2026

## O que mudou

- **Formato**: logs em arquivo e console passaram a usar formato com timestamp, nível, nome do módulo e `request_id` (quando houver request HTTP).
- **Request ID**: cada request recebe um ID único; ele aparece nos logs e no header de resposta `X-Request-ID`, permitindo rastrear toda a requisição.
- **Helpers**: `core.log_utils` oferece `log_action()` e `log_request()` para mensagens mais consistentes.

## Formato dos logs

Exemplo em arquivo (`logs/info.log`):

```
[2025-02-20T14:30:00] INFO     | apps.main.home.views.accounts | req=a1b2c3d4e5f6 | [UserLoginView] Usuário autenticado com sucesso: joao (is_superuser: False)
```

Console (mais curto):

```
[14:30:00] INFO     apps.main.home.views.accounts req=a1b2c3d4e5f6 [UserLoginView] Usuário autenticado...
```

## Como usar

### Padrão (recomendado)

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Mensagem clara com contexto: usuário=%s ação=%s", username, action)
logger.warning("Algo inesperado mas recuperável: %s", detail)
logger.error("Falha na operação: %s", str(e), exc_info=True)
```

### Mensagens estruturadas (opcional)

```python
from core.log_utils import get_logger, log_action

logger = get_logger(__name__)

# Ação com status e extras
log_action(logger, "login", "sucesso", username=user.username)
log_action(logger, "transfer", "erro", message="saldo insuficiente", level=logging.ERROR, account_id=123)
```

### Boas práticas

1. **Use o nome do módulo**: sempre `logging.getLogger(__name__)` para o logger.
2. **Mensagens úteis**: evite só "Erro" ou "Error"; inclua o que falhou e contexto (ex.: `"Falha ao buscar contas por email: %s"`).
3. **Nível certo**: DEBUG para detalhe, INFO para fluxo normal, WARNING para fallbacks, ERROR para falhas, CRITICAL para falhas graves.
4. **Exceções**: use `exc_info=True` em `logger.error()` quando logar exceção, para aparecer stack trace no log.

## Request ID

- Definido no middleware `RequestIdMiddleware` (após `CommonMiddleware`).
- Se o cliente enviar `X-Request-ID`, ele é reutilizado; senão é gerado um.
- A resposta inclui `X-Request-ID` no header para o cliente poder informar ao suporte.

## Arquivos de log

Em produção (DEBUG=False):

- `logs/debug.log` – DEBUG
- `logs/info.log` – INFO
- `logs/warning.log` – WARNING
- `logs/error.log` – ERROR
- `logs/critical.log` – CRITICAL
- `logs/wallet.log` – app wallet

Rotação: 5 MB por arquivo, até 7 backups.

## Logs de regras de negócio (log_action)

Os seguintes eventos são registrados com `log_action` para auditoria e análise:

| App | Ação | Status/Evento | Exemplo de extras |
|-----|------|----------------|-------------------|
| **wallet** | wallet_transfer_p2p | sucesso, saldo_insuficiente | remetente, destinatario, valor |
| **wallet** | wallet_transfer_bonus_p2p | sucesso, saldo_bonus_insuficiente | remetente, destinatario, valor |
| **wallet** | wallet_transfer_servidor | sucesso | username, personagem, valor, origem_saldo, moedas |
| **wallet** | wallet_retirada_servidor | sucesso, erro | username, char_id, valor_liquido, taxa_percentual |
| **wallet** | wallet_compra_moedas | sucesso | username, valor_compra, valor_bonus, metodo |
| **wallet** | wallet_compra_fichas | sucesso | username, quantidade, total, origem_saldo |
| **wallet** | wallet_coin_config | moeda_ativada, moeda_criada, taxa_atualizada, moeda_excluida | nome, coin_id, staff |
| **payment** | payment_pedido | criado | username, pedido_id, valor, metodo |
| **payment** | payment_mercadopago | aprovado_redirect | username, pagamento_id, valor, valor_bonus |
| **payment** | payment_mercadopago_webhook | aprovado, aprovado_merchant_order | username, pagamento_id, data_id, valor |
| **payment** | payment_stripe_webhook | checkout_completed, payment_intent_succeeded | username, pagamento_id, valor |
| **payment** | payment_stripe | aprovado_redirect | username, session_id, valor |
| **social** | social_post | criado | username, post_id |
| **social** | social_share | sucesso | username, original_post_id, novo_post_id |
| **social** | social_follow | follow, unfollow | follower, following |
| **social** | social_report | criado | reporter, content_type, content_id, report_type |
| **social** | social_moderacao | acao_aplicada | moderator, action_type, report_id, target_* |
| **notification** | notification_claim_rewards | sucesso | username, notification_id, rewards_count, has_fichas |
| **message** | message_amizade | pedido_enviado, aceito, recusado | user, friend, requester, target |
| **shop** | shop_checkout | sucesso | username, purchase_id, total, personagem |
| **auction** | auction_lance | sucesso | auction_id, bidder, amount, character_name |
| **auction** | auction_finalizado | venda | auction_id, seller, winner, amount |
| **licence** | licence | licenca_invalida, sem_licenca | path |

Para buscar em arquivos de log: `grep "\[wallet_transfer_p2p\]" logs/info.log` ou pelo request_id.

## Telemetria (métricas)

Com `TELEMETRY_ENABLED=True`, cada `log_action(...)` também alimenta o contador Prometheus `pdl_business_events_total`. Ver [TELEMETRY.md](TELEMETRY.md).

## Log em JSON (futuro)

O módulo `core.logger` define um formatter `json`. Para ativar em produção (ex.: CloudWatch, ELK), troque o `formatter` dos handlers desejados para `"json"` em `core/logger.py`.

---

[ Voltar ao Índice](../INDEX.md)

