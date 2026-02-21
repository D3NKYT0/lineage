# Guia do Ecossistema de Minigames

> **Última atualização:** 21/02/2026

O Lineage Definitivo Painel (PDL) suporta e gerencia minigames interativos que movimentam a economia (fichas e itens in-game) sem precisar que o usuário esteja logado no cliente do jogo. Atualmente, o painel oferece os seguintes módulos:

## 🎮 Jogos Disponíveis

### 1. 🎰 Slot Machine (Caça-Níqueis)
Um jogo clássico de giro baseado na sorte com suporte a Jackpot Progressivo.
- Sistema de símbolos configuráveis diretamente no Admin utilizando "pesos" para ditar a taxa de raridade por giro.
- Jackpot que se alimenta de uma porcentagem automática gerada pelos custos das tentativas falhas de todos os jogadores.
- Histórico global audíptico das vitórias e premiações vinculadas de tokens ou itens físicos através da integração de inventário.

### 2. 🎲 Dice Game (Jogo de Dados)
Apostas tradicionais e simulações rápidas usando rolagem virtual.
- Permite especificação de risco escolhendo tipo de aposta (Nº Específico = Multiplicador x5; Range/Par/Ímpar = Multiplicador x2).
- Controle de limites (Min/Max Bets) parametrizado pelos donos do servidor para evitar lavagem ou farming quebrado.
- Leaderboards que analisam lucro total em rede.

### 3. 🎣 Fishing Game (Pescaria)
Modelo de progressão "Gacha-lite".
- O jogador treina de varas de pesca Level 1 que ganham XP por "Lançamento de linha". Leveis mais altos aumentam a hit-rate das recompensas.
- Separação da tabela de Drops de peixes entre Comum, Raro, Épico e Lendário.
- Economia impulsionada por *Fishing Baits* compráveis para aumentar buffers temporários visando buscar prêmios exclusivos.

## 📦 Estrutura de Modelos (Base de Dados)

Os minigames rodam como abstrações lógicas no diretório do Lineage Game Data Server:

- As interfaces encontram-se parametrizadas globalmente através dos scripts localizados sob a hierarquia de `apps/lineage/games/`.
- Configurações, Histórico (Historicals), Symbols de Slot, FishingRod States, e Tabelas do Dice encontram-se como instâncias individuais via classes que mapeiam as transações como `SlotMachineHistory` e `DiceGameConfig`.

## ⚙️ Configuração no Painel Administrativo

Todos os módulos dependem estritamente da área Django Adim (`/admin/games/`):
- Para o **Slot Machine**, você obrigatoriamente vincula uma configuração Master definindo os multiplicadores iniciais e atrelos ao banco.
- Em **Pescaria**, o Adm rege a inflação ao lançar peixes na tabela determinando XP exatos, Fichas de trade-off por peso e a tag de Raridade deles.

## 🚀 Setup e Uso no Servidor (População)

Antes de utilizar a interface e os jogos estarem listados no sistema, um setup de banco primário é exigido.

1. **Instale as definições estruturais nativas**
   ```bash
   python manage.py makemigrations games
   python manage.py migrate
   ```

2. **Popule a Base de Minigames Dinâmica**
   ```bash
   python manage.py populate_new_games
   ```
   *O comando automático abastece nativamente o banco com: 9 Símbolos Base e 12 Prêmios para o Slot Machine, Setup padrão de rolagem de Dados (Dice Game), e a fundação biológica de pesca com 12 tipos de peixes variados por raridade, além de 4 iscas de farm.*

Você está livre para manipular a injeção inicial por meio das interfaces visuais do **Config Hub (`/config/hub/`)** que hospedam as planilhas dinâmicas editáveis das configurações descritas acima.

## 🚀 Integrações de Inventário

Qualquer ganho que vá além das abstrações de "Fichas" de minigame (como armaduras, runas especiais etc) engaja o utilitário nativo via API da *"Bag"*. Itens sorteados viram dados lógicos aguardando o usuário enviá-los efetivamente para os personagens associados. Tudo logado contra abusos em banco de dados isolado no L2J.

---

[ Voltar ao Índice](../INDEX.md)

