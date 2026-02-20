# 🎮 Implementação dos Novos Jogos

## Jogos Implementados

Foram implementados **3 novos jogos** no sistema:

### 1. 🎰 Slot Machine (Caça-Níqueis)
Um jogo de sorte baseado em slots com jackpot progressivo.

**Características:**
- Sistema de símbolos com pesos configuráveis
- Jackpot progressivo acumulativo
- Prêmios em fichas e itens
- Histórico de jogadas
- Leaderboard com top ganhadores

**Acesso:** Menu Games → Slot Machine

---

### 2. 🎲 Dice Game (Jogo de Dados)
Jogo de apostas com dados onde o jogador escolhe o tipo de aposta.

**Características:**
- Múltiplos tipos de aposta:
  - Número específico (1-6) - Multiplicador x5
  - Par/Ímpar - Multiplicador x2
  - Alto (4-6) / Baixo (1-3) - Multiplicador x2
- Configuração de limites de aposta (min/max)
- Estatísticas detalhadas por jogador
- Histórico completo de jogadas
- Leaderboard com ranking de lucro

**Acesso:** Menu Games → Dice Game

---

### 3. 🎣 Fishing Game (Pescaria)
Jogo de pescaria com sistema de progressão e coleção de peixes.

**Características:**
- Sistema de vara de pesca com níveis e XP
- Peixes de diferentes raridades (comum, raro, épico, lendário)
- Sistema de iscas especiais que aumentam chances
- Coleção de peixes capturados
- Recompensas em XP, fichas e itens
- Leaderboard de pescadores

**Acesso:** Menu Games → Pescaria

---

## 📦 Arquivos Criados

### Modelos (apps/lineage/games/models.py)
- **Slot Machine:** `SlotMachineConfig`, `SlotMachineSymbol`, `SlotMachinePrize`, `SlotMachineHistory`
- **Dice Game:** `DiceGameConfig`, `DiceGameHistory`
- **Fishing Game:** `FishingRod`, `Fish`, `FishingHistory`, `FishingBait`, `UserFishingBait`

### Views
- `apps/lineage/games/views/slot_machine_views.py`
- `apps/lineage/games/views/dice_game_views.py`
- `apps/lineage/games/views/fishing_game_views.py`

### Templates
- `apps/lineage/games/templates/slot_machine/slot_machine.html`
- `apps/lineage/games/templates/dice_game/dice_game.html`
- `apps/lineage/games/templates/fishing_game/fishing_game.html`

### URLs
Adicionadas no arquivo `apps/lineage/games/urls.py`

### Admin
Todos os modelos foram registrados no Django Admin em `apps/lineage/games/admin.py`

---

## 🚀 Como Ativar os Jogos

### 1. Criar as Migrations

```bash
# Ativar ambiente virtual (se necessário)
# No Linux/Mac:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Criar migrations
python manage.py makemigrations games

# Aplicar migrations
python manage.py migrate games
```

### 2. Configurar no Django Admin

#### 🎰 Slot Machine

1. Acesse: **Admin → Games → Slot Machine Configs**
2. Crie uma nova configuração:
   - Nome: "Slot Machine Principal"
   - Custo por giro: 1 ficha
   - Jackpot inicial: 1000 fichas
   - Chance de jackpot: 0.1%
   - Marque como "Ativo"

3. Acesse: **Admin → Games → Slot Machine Symbols**
4. Crie os símbolos (exemplos):
   - Espada: peso 15, ícone ⚔️
   - Escudo: peso 15, ícone 🛡️
   - Poção: peso 20, ícone 🧪
   - Gema: peso 10, ícone 💎
   - Ouro: peso 25, ícone 🪙
   - Jackpot: peso 1, ícone 💰

5. Acesse: **Admin → Games → Slot Machine Prizes**
6. Configure os prêmios para combinações (exemplos):
   - 3x Jackpot: 10000 fichas
   - 3x Gema: 500 fichas ou item raro
   - 3x Ouro: 100 fichas
   - 2x Espada: 50 fichas

#### 🎲 Dice Game

1. Acesse: **Admin → Games → Dice Game Configs**
2. Crie uma configuração:
   - Aposta mínima: 1 ficha
   - Aposta máxima: 100 fichas
   - Multiplicador número específico: 5.0
   - Multiplicador par/ímpar: 2.0
   - Multiplicador alto/baixo: 2.0
   - Marque como "Ativo"

#### 🎣 Fishing Game

1. Acesse: **Admin → Games → Fishes**
2. Crie os peixes (exemplos):
   
   **Peixes Comuns (Level 1+):**
   - Nome: "Peixinho", Raridade: Comum, Peso: 50, XP: 10, Fichas: 5
   - Nome: "Sardinha", Raridade: Comum, Peso: 45, XP: 12, Fichas: 6

   **Peixes Raros (Level 3+):**
   - Nome: "Atum", Raridade: Raro, Peso: 25, XP: 30, Fichas: 20
   - Nome: "Salmão", Raridade: Raro, Peso: 20, XP: 35, Fichas: 25

   **Peixes Épicos (Level 5+):**
   - Nome: "Tubarão", Raridade: Épico, Peso: 10, XP: 80, Fichas: 50
   - Nome: "Golfinho", Raridade: Épico, Peso: 8, XP: 90, Fichas: 60

   **Peixes Lendários (Level 7+):**
   - Nome: "Dragão Marinho", Raridade: Lendário, Peso: 3, XP: 200, Fichas: 150
   - Nome: "Kraken Bebê", Raridade: Lendário, Peso: 2, XP: 250, Fichas: 200

3. (Opcional) Acesse: **Admin → Games → Fishing Baits**
4. Crie iscas especiais:
   - Nome: "Isca Rara", Preço: 50, Bônus: +50% para raros, Duração: 30 min
   - Nome: "Isca Épica", Preço: 100, Bônus: +50% para épicos, Duração: 30 min
   - Nome: "Isca Lendária", Preço: 200, Bônus: +50% para lendários, Duração: 60 min

---

## 🎯 Como Jogar

### 🎰 Slot Machine
1. Acesse o menu Games → Slot Machine
2. Verifique seu saldo de fichas
3. Clique em "GIRAR" para apostar 1 ficha
4. Aguarde o resultado dos 3 rolos
5. Se fizer uma combinação, ganhará prêmios!

### 🎲 Dice Game
1. Acesse o menu Games → Dice Game
2. Escolha o tipo de aposta (par, ímpar, alto, baixo ou número específico)
3. Se escolher número específico, selecione um número de 1 a 6
4. Defina o valor da aposta (entre min e max)
5. Clique em "JOGAR"
6. O dado será lançado e você verá se ganhou!

### 🎣 Fishing Game
1. Acesse o menu Games → Pescaria
2. Você começa com uma vara Level 1
3. Clique em "LANÇAR LINHA" para pescar (custa 1 ficha)
4. Tente capturar um peixe - quanto maior a raridade, mais difícil
5. Ganhe XP para subir o nível da vara
6. Com níveis mais altos, pode pescar peixes melhores
7. (Opcional) Compre iscas especiais para aumentar suas chances

---

## 📊 Recursos Adicionais

### Leaderboards
Cada jogo tem seu próprio sistema de ranking:
- **Slot Machine:** Top ganhadores, maiores prêmios
- **Dice Game:** Maior lucro, mais jogadas, maior win rate
- **Fishing Game:** Maior nível de vara, mais peixes lendários, mais capturas

### Sistema de Fichas
Todos os jogos usam o sistema de fichas existente. Jogadores podem:
- Comprar fichas (se configurado)
- Ganhar fichas jogando
- Usar fichas para apostar

### Integração com Bag
Os prêmios em itens são automaticamente adicionados à Bag do jogador, podendo ser transferidos para o inventário do jogo.

---

## 🔧 Troubleshooting

### Jogos não aparecem no menu
- Verifique se as URLs foram adicionadas corretamente
- Limpe o cache do navegador
- Reinicie o servidor Django

### Erro ao criar migrations
```bash
# Tente executar:
python manage.py makemigrations
python manage.py migrate
```

### Erro "Nenhum jogo disponível"
- Verifique se criou uma configuração e marcou como "Ativo" no Admin
- No Slot Machine: certifique-se de ter símbolos cadastrados
- No Fishing Game: certifique-se de ter peixes cadastrados

### Jackpot não aumenta
- Verifique a configuração do Slot Machine no Admin
- O jackpot aumenta 10% do custo de cada giro

---

## 🎨 Personalização

### Modificar Símbolos do Slot Machine
Edite os ícones/emojis no Admin → Slot Machine Symbols

### Ajustar Dificuldade
- **Slot Machine:** Ajuste os pesos dos símbolos (menor peso = mais raro)
- **Dice Game:** Altere os multiplicadores na configuração
- **Fishing Game:** Ajuste os pesos dos peixes e as taxas de sucesso no código

### Adicionar Mais Peixes
Crie novos peixes no Admin com diferentes raridades e requisitos de nível

---

## 📝 Notas Importantes

1. **Sistema de Fichas:** Certifique-se de que os jogadores tenham fichas suficientes
2. **Responsividade:** Todos os jogos são responsivos e funcionam em mobile
3. **AJAX:** Os jogos usam AJAX para uma experiência mais fluida
4. **Histórico:** Todo histórico de jogadas é salvo para auditoria
5. **Segurança:** Todas as transações são atômicas para evitar problemas de concorrência

---

## 🚀 Próximos Passos Sugeridos

1. Popular o banco com dados iniciais (símbolos, peixes, configurações)
2. Ajustar valores de recompensas baseado na economia do servidor
3. Criar eventos especiais (jackpots aumentados, peixes raros temporários)
4. Adicionar achievements relacionados aos jogos
5. Implementar estatísticas globais na homepage

---

## 💡 Sugestões de Melhorias Futuras

- **Slot Machine:** Adicionar animações de vitória, sons, mais linhas de pagamento
- **Dice Game:** Modo "duplo ou nada", apostas em múltiplos dados
- **Fishing Game:** Torneios de pesca, aquário virtual para exibir peixes capturados
- **Geral:** Sistema de conquistas específico para os jogos, missões diárias

---

**Desenvolvido por:** Daniel Amaral  
**Data:** Dezembro 2025  
**Versão:** 1.0.0

