# 📊 Guia do Módulo Financeiro (Accountancy)

> **Última atualização:** 21/02/2026

O módulo **Accountancy** é o centro de análise financeira do PDL para administradores. Acesse `/app/accountancy/` para visualizar o dashboard e todos os relatórios.

> ⚠️ Este módulo é exclusivo para usuários com permissão de **Staff** (`is_staff=True`).

---

## 1. Dashboard Financeiro

Acesse `/app/accountancy/` para ter uma visão geral da saúde financeira do servidor. A partir do dashboard, você navega para qualquer um dos relatórios específicos.

---

## 2. Relatório de Saldo de Usuários

**URL:** `/app/accountancy/balance-report/`

Exibe o saldo de **todos os usuários** do painel, comparando o saldo registrado no banco com o saldo calculado pelas transações.

### Filtros Disponíveis
| Filtro | Descrição |
|--------|-----------|
| **Usuário** | Busca parcial por username |
| **Status** | Consistente, Pequena Discrepância, Discrepância, Sem Carteira |
| **Saldo Mínimo (R$)** | Exibe apenas usuários acima do valor |
| **Saldo Máximo (R$)** | Exibe apenas usuários abaixo do valor |

### O que cada Status significa
| Status | Significado |
|--------|-------------|
| ✅ **Consistente** | Saldo na carteira = saldo calculado pelas transações |
| ⚠️ **Pequena Discrepância** | Diferença pequena — provavelmente arredondamento |
| ❌ **Discrepância** | Diferença significativa — investigar manualmente |
| 🚫 **Sem Carteira** | Usuário não tem carteira criada ainda |

### Totais Exibidos
- Total de Saldo Principal (R$) de todos os usuários filtrados
- Total de Saldo Bônus (R$)
- Total de Transações
- Diferença total (Principal vs. Calculado)

---

## 3. Relatório de Fluxo de Caixa

**URL:** `/app/accountancy/cash-flow-report/`

Exibe as **entradas e saídas diárias** do sistema, com gráfico temporal.

### Filtros Disponíveis
| Filtro | Descrição |
|--------|-----------|
| **Data Início** | Início do período |
| **Data Fim** | Fim do período |

### Dados Exibidos (por dia)
- **Entradas (R$):** Depósitos e créditos do dia
- **Saídas (R$):** Debítos e compras do dia
- **Saldo do Dia (R$):** Entradas - Saídas

O relatório também exibe gráfico com curvas de entradas, saídas e saldo acumulado.

---

## 4. Relatório de Pedidos e Pagamentos

**URL:** `/app/accountancy/orders-payments-report/`

Lista todos os pedidos de pagamento (depósitos), com status e detalhes de cada transação.

### Filtros Disponíveis
| Filtro | Opções |
|--------|--------|
| **Status** | Pendente, Aprovado, Cancelado, Expirado |
| **Método** | Mercado Pago, Stripe |
| **Período** | Data início / Data fim |
| **Usuário** | Busca por username |
| **Valor** | Mínimo e máximo (R$) |

### Dados por Pedido
- ID do pedido
- Usuário
- Valor pago, Bônus aplicado, Total creditado
- Moedas geradas (se houver conversão de itens do jogo)
- Percentual de bônus utilizado
- Status do pedido
- Método de pagamento
- Origem do pagamento: **Manual** (admin) ou **Serviço** (gateway automático)

---

## 5. Relatório de Reconciliação de Carteiras

**URL:** `/app/accountancy/wallet-reconciliation-report/`

Relatório avançado que cruzar **transações de carteira** com os **saldos registrados**, identificando possíveis inconsistências por usuário.

### Filtros Disponíveis
| Filtro | Descrição |
|--------|-----------|
| **Usuário** | Busca parcial por username |
| **Status** | Reconciliado, Discrepância, Em Análise, Pendente |
| **Diferença Mínima** | Examina apenas desvios acima do valor |
| **Diferença Máxima** | Examina apenas desvios abaixo do valor |

### Status de Reconciliação
| Status | Significado |
|--------|-------------|
| ✅ **Reconciliado** | Transações batem com saldo |
| ❌ **Discrepância** | Divergência entre transações e saldo — ação necessária |
| 🔍 **Em Análise** | Sendo investigado |
| ⏳ **Pendente** | Aguardando análise |

---

## Documentação Relacionada

- 💳 [Configuração de Pagamentos](PAYMENT_CONFIGURATION.md)
- 🛒 [Gerenciar Loja (Admin)](SHOP_ADMIN_GUIDE.md)

---

[ Voltar ao Índice](../INDEX.md)

