# Central de Configurações (Config Hub)

> **Última atualização:** 21/02/2026

O **Config Hub** (`/config/hub/`) atua como a espinha dorsal de parametrização dinâmica do PDL. Diferente do Painel Django nativo, a Central de Configurações visa oferecer um design Neumorphic moderno para os Donos de Servidor gerenciarem a balança de poder, tabelas de prêmios e gatilhos sociais em dezenas de submódulos interativos, sem que precisem tocar em bancos de dados.

Abaixo, detalhamos todos os blocos e ferramentas disponíveis dentro de cada gaveta do Hub.

---

## 1. ⚙️ Sistema & API

Essa categoria expõe as portas do servidor para o mundo corporativo e integrações de longo prazo.

| Ferramenta | O que faz no Servidor |
|------------|------------------------|
| **API** | `/api/v1/config/`. Define se Módulos Rest Externos do L2 (aplicativos mobile ou sites parceiros) têm autorização para puxar dados. Você configura os tokens mestre aqui e o throttling. |
| **Recursos** | `/app/resources/dashboard/`. Controla flags massivas do painel. Ex: Ligar/Desligar registros, Habilitar/Desabilitar sistema de Login Social pelo Google, Discord, ou Github. |

---

## 2. 💰 Financeiro

Gestão irrestrita do que entra de dinheiro real e do que sai de bens virtuais no jogo.

| Ferramenta | O que faz no Servidor |
|------------|------------------------|
| **Moedas (Coins)** | Você define as taxas de inflação aqui (ex: 1 R$ = 100 L2 Coins). Todo ecossistema PDL lê as cotações cadastradas ativas e os bônus fixos de conversão. |
| **Shop (Loja)** | Vitrine Principal Web. Configure categorias da loja (Equipamentos, VIPs, Consumíveis), ajuste descontos em tempo real, defina contadores de pacote rotativo e suba descrições ricas. |

---

## 3. 🎮 Jogos (Ecossistema L2)

O maior bloco do Hub, dominando eventos passivos e economia interativa sem NPC no servidor físico.

| Ferramenta | O que faz no Servidor |
|------------|------------------------|
| **Box Manager (Lootboxes)** | Crie as populares "Caixas Misteriosas". Configure as taxas (Drops %) de cada armadura ou consumível DENTRO das caixas, estipulando os prêmios super raros. |
| **Daily Bonus Manager** | Sistema de Login Diário. Decida exatamente o que o jogador recebe ao fazer login no painel na 1ª, 7ª ou 30ª visita seguida. |
| **Roulette (Roleta)** | Insira 8 até 12 itens lógicos numa roleta da sorte animada. Defina aqui a balança de "weights" (pesos) para controlar itens escassos. |
| **Economy Manager** | Ferramenta estatística de "Big Brother". O admin vê quanto gold (Adena) "nasce" dos minigames contra o "faucet" recolhido, auxiliando balancear a economia central do seu L2. |
| **Battle Pass (Temporadas)** | Ative uma Season (ex: Inverno). Crie Tiers grátis ou premium de level 1 ao 100, injetando chaves, L2 Coins e capas exclusivas de prêmio. |
| **Achievement Rewards** | Conquistas Passivas (ex: "Jogue por 10 dias seguidos", "Verifique seu Discord"). O manager recompensa as contas Master quando as premissas completam. |
| **Level Rewards** | Tabelas de nivelamento contínuo da própria conta Painel (Conta Master - Web) permitindo aos investidores ou ativos destrancaram badges conforme ganham "XP de Perfil". |
| **Slot Machine (Caça-Níquel)**| Configure até 9 emojis visuais, e cruze-os. Se o jogador bater "três maçãs" 🍎🍎🍎, o Config delega quantas fichas ele ganha ou puxa um Item físico direto pra "Bag" da conta. |
| **Dice Game (Dados)** | Especifique as *Odds* (risco matemático). Jogar pra acertar 1 número paga 5 vezes a aposta; chutar pares ou ímpares paga 2. A margem contra exploit é regada por limites min/max definidos aqui. |
| **Fishing Game (Pesca)**| Crie peixes desde os raros "White Shark" aos Comuns. Assinale o tempo base de pescaria por Lançada (Cooldown), e determine itens bônus (Iscas de +% drop). |

---

## 4. 📄 Conteúdo

Gestão do material público consumido pelos players na Index do Servidor ou painéis de notícia.

| Ferramenta | O que faz no Servidor |
|------------|------------------------|
| **Coming Soon** | Se o servidor ainda não lançou, essa tela congela todo roteamento público do painel e sobrepõe uma contagem regressiva viva e um banner épico configuráveis neste menu. |
| **Calendar Manager** | Cronograma de "TV Guias". Você cadastra que "Sábado 20h tem as Siege", ou "Segunda Drop 2x", gerando uma timeline linda pros usuários. |
| **Roadmap Manager** | Transparência de versão. Mostre aos seus players as Kanban Tiers (Desenvolvimento, Testes, Cedo) das magias do próximo mês ou dos fixes aplicados. |

---

## 5. 🖧 Servidor (Lineage)

Gira em torno dos preços praticados de features exclusivas de mecânica L2J.

| Ferramenta | O que faz no Servidor |
|------------|------------------------|
| **Services (Serviços L2)**| Você quer permitir Nick Change, Re-Skins de Raça, Limpeza do Karma PK? Todos esses preços fixos são rebatidos e definidos via `Config Hub > Servidor`. |
| **Apoiadores** | Crie assinaturas VIP mensais ou níveis hierárquicos para patronos do clipe, determinando se "Apoiador Ouro" paga meia nos leilões ou ganha selo extra. |

---

## 6. 🛡️ Administração e Moderação

Ferramentas massivas e configurações do Sistema Central de Verificação de players.

| Ferramenta | O que faz no Servidor |
|------------|------------------------|
| **Licenças** | Verifica a propriedade e chave AES do plano PDL com os nossos sistemas matriz (Validação Legal Automática de Dominio - Nível Dono). |
| **Notificações** | Quer mandar a todos que os servidores voltarão logo anexando 50 L2 Coins pelo transtorno? Use as notificações de massa (Inbox com Premiação embutida). |
| **Enviar Push** | Disparo instantâneo do Notification API no navegador ou no Android/iOS (Push Alerts que flutuam igual mensagem de Whats). |
| **Verificações Sociais** | Se seu servidor exige Discord Linkado e Selfie, é a mesa de aprovação em que o Staff diz "sim" à humanidade do perfil, concedendo o "Selo Azul de Verificado". |

---

**Dica Master**: Todas as ferramentas conectam-se visualmente via Neo-Dashboard. Nenhum painel desloga você da sessão. Caso perca abas de vista, o menu retrátil em todas as visões (Sidebar ESQUERDA) consegue retornar velozmente para o `/config/hub/`.

---

[ Voltar ao Índice](../INDEX.md)

