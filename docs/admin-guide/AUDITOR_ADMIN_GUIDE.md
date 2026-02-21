# Central do Auditor e Anti-Fraude

> **Última atualização:** 21/02/2026

O Lineage Definitivo Painel carrega um arsenal robusto sob o aplicativo `apps/auditor`. A sua função como Administrador (Staff) não é apenas ler tabelas de bans, mas agir preventivamente contra roubos, RMT e Múltiplas Contas falsas do painel inteiro.

---

## 🔎 Rastreador de Assinaturas (Device ID)

Todo jogador que loga no site não entrega apenas o IP (fácilmente trocado por VPN), ele gera um `Device Hash` interno vinculado ao modelo do celular/processador/GPU. 
- Acesse `/admin/auditor/dashboard/` e puxe a lista de Contas Múltiplas.
- Você visualizará se aquele char *"KillerPvP"* do computador X compartilha acesso de sessão com uma conta criada há 2 minutos chamada *"FarmBot_L2"*, atestando abuso de criação de contas.

## 🏦 Auditoria Financeira e Mercado Pago

Se a equipe receber um chamado no Helpdesk sobre "Não recebi meus coins do PIX!", a tela do auditor entra em ação.
Você não confia num PDF ou Print do WhatsApp:
1. Navegue até a **Busca de Transação**.
2. Insira o Email ou Login.
3. O log em formato JSON destrinchará todas as batidas entre os servidores do PDL e o Mercado Pago / Stripe, mostrando se o cartão de crédito do jogador falhou (Declined) ou estornou (Chargeback). 

A punição pode ser aplicada unicamente através dessa checagem dura.

---

## 🚦 Tabela do Histórico Administrativo

Toda mutação no Painel PDL é *Auditada*.
- Um GM baniu alguém? Fica registrado quem deu `Save` no ban.
- Alguém mudou a taxa (inflação) das moedas na `Config Hub`? O auditor salva a data, o novo valor e o IP do Administrador que causou isso.

**Ninguém foge da auditoria sistêmica.** Use-a a favor da liderança para delegar sub-gerentes sem temer corrupção oculta.

---

[ Voltar ao Índice](../INDEX.md)

