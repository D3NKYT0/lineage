# Sistema de Bônus para Compras de Moedas

> **Última atualização:** 21/02/2026

## Visão Geral

O sistema de bônus permite que administradores configurem automaticamente bônus percentuais para compras de moedas baseados em faixas de valores. Quando um jogador compra moedas, o sistema verifica automaticamente se há bônus aplicável e credita o valor adicional em uma **carteira de bônus separada**.

## 🎯 **Nova Estrutura: Carteira Dupla**

### Carteira Principal
- **Saldo**: Moedas compradas normalmente
- **Uso**: Todas as funcionalidades do sistema
- **Transações**: `TransacaoWallet`

### Carteira de Bônus
- **Saldo**: Bônus recebidos por compras
- **Uso**: Funcionalidades específicas (configurável)
- **Transações**: `TransacaoBonus`

## Funcionalidades

### 1. Configuração de Bônus (Admin)

- **Valor Mínimo**: Define o valor mínimo da compra para aplicar o bônus
- **Valor Máximo**: Define o valor máximo (opcional, deixe em branco para sem limite)
- **Bônus Percentual**: Percentual de bônus a ser aplicado (ex: 10.00 para 10%)
- **Descrição**: Descrição do bônus que aparecerá nas transações
- **Ativo**: Habilita/desabilita o bônus
- **Ordem**: Prioridade do bônus (menor número = maior prioridade)

### 2. Cálculo Automático

O sistema calcula automaticamente o bônus aplicável baseado em:
- Valor da compra
- Bônus ativos
- Ordem de prioridade
- Faixas de valores configuradas

### 3. Interface do Usuário

- **Página de Compra**: Mostra bônus disponíveis em tempo real via AJAX
- **Carteira**: Exibe dois saldos separados (Principal e Bônus)
- **Transações**: Registra separadamente transações normais e de bônus
- **Detalhes do Pedido**: Exibe informações sobre bônus aplicados

## Como Configurar

### 1. Acesse o Admin Django

```
/admin/lineage/coinpurchasebonus/
```

### 2. Crie um Novo Bônus

Exemplo de configuração:
- **Descrição**: "Bônus de 10% para compras acima de R$ 50"
- **Valor Mínimo**: 50.00
- **Valor Máximo**: (deixe em branco)
- **Bônus Percentual**: 10.00
- **Ativo**: ✓
- **Ordem**: 1

### 3. Exemplos de Configurações

#### Bônus Progressivo
```
Bônus 1: 5% para compras de R$ 10 a R$ 49
Bônus 2: 10% para compras de R$ 50 a R$ 99  
Bônus 3: 15% para compras de R$ 100 a R$ 199
Bônus 4: 20% para compras acima de R$ 200
```

#### Bônus Específico
```
Bônus: 25% para compras de R$ 100 a R$ 150
```

## Como Funciona

### 1. Criação do Pedido

Quando um usuário cria um pedido:
1. Sistema calcula o bônus aplicável
2. Armazena o valor do bônus no pedido
3. Mostra informações na interface

### 2. Confirmação do Pagamento

Quando o pagamento é confirmado:
1. Usa a função centralizada `aplicar_compra_com_bonus`
2. **Carteira Principal**: Credita o valor da compra via `aplicar_transacao`
3. **Carteira de Bônus**: Credita o valor do bônus via `aplicar_transacao_bonus`
4. Atualiza ambos os saldos automaticamente

### 3. Transações Criadas

Para uma compra de R$ 100 com 10% de bônus:

#### Carteira Principal:
```
Transação: ENTRADA - R$ 100.00 - "Compra de moedas via MercadoPago"
```

#### Carteira de Bônus:
```
Transação: ENTRADA - R$ 10.00 - "Bônus: Bônus de 10% para compras acima de R$ 50"
```

## Arquivos Modificados

### Modelos
- `apps/lineage/wallet/models.py`: 
  - Novo campo `saldo_bonus` em `Wallet`
  - Novo modelo `TransacaoBonus`
  - Modelo `CoinPurchaseBonus` para configuração

### Views
- `apps/lineage/wallet/utils.py`: Funções de cálculo e aplicação de bônus
- `apps/lineage/wallet/signals.py`: Nova função `aplicar_transacao_bonus`
- `apps/lineage/wallet/views.py`: View atualizada para mostrar transações combinadas
- `apps/lineage/payment/views/payments_views.py`: View AJAX para cálculo de bônus
- `apps/lineage/payment/views/mercadopago_views.py`: Webhook atualizado
- `apps/lineage/payment/views/stripe_views.py`: Webhook atualizado

### Templates
- `apps/lineage/wallet/templates/wallet/dashboard.html`: Interface com dois saldos
- `apps/lineage/payment/templates/payment/purchase.html`: Interface com cálculo de bônus
- `apps/lineage/payment/templates/payment/detalhes_pedido.html`: Exibição de bônus

### Admin
- `apps/lineage/wallet/admin.py`: Interface administrativa para bônus e transações

## URLs

- `/payment/calcular-bonus/`: Endpoint AJAX para cálculo de bônus

## Migrações Necessárias

Execute as migrações para criar as tabelas:
```bash
python manage.py makemigrations wallet
python manage.py migrate
```

## Benefícios

1. **Flexibilidade**: Configuração total via admin
2. **Separação**: Carteira de bônus independente da principal
3. **Controle**: Você decide onde o bônus pode ser usado
4. **Transparência**: Transações separadas para rastreamento
5. **Experiência do Usuário**: Interface clara mostrando dois saldos
6. **Escalabilidade**: Suporte a múltiplos bônus com prioridades
7. **Consistência**: Usa funções centralizadas para ambas as carteiras

## Considerações

- **Carteira Principal**: Usada para todas as funcionalidades normais
- **Carteira de Bônus**: Usada apenas onde você permitir
- Bônus são aplicados apenas uma vez por pedido
- O sistema usa o bônus de maior prioridade aplicável
- Transações de bônus são registradas separadamente para auditoria
- Interface responsiva funciona em dispositivos móveis
- **Mantém consistência** usando funções centralizadas

## Uso da Carteira de Bônus

Para usar o saldo de bônus em funcionalidades específicas, você pode:

1. **Verificar o saldo de bônus**:
   ```python
   if wallet.saldo_bonus >= valor_necessario:
       # Usar bônus
   ```

2. **Debitar da carteira de bônus**:
   ```python
   from apps.lineage.wallet.signals import aplicar_transacao_bonus
   
   aplicar_transacao_bonus(
       wallet=wallet,
       tipo="SAIDA",
       valor=valor_necessario,
       descricao="Uso em funcionalidade específica"
   )
   ```

3. **Transferir entre carteiras** (se necessário):
   ```python
   from apps.lineage.wallet.utils import transferir_bonus_para_jogador
   ```
---

[ Voltar ao Índice](../INDEX.md)

