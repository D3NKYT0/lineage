# 🎮 Como Usar os Novos Jogos - Guia Rápido

## 🚨 IMPORTANTE - Primeiro Passo

Antes de usar os jogos, você **DEVE** rodar as migrations e popular o banco:

```bash
# 1. Criar migrations
python manage.py makemigrations games

# 2. Aplicar migrations
python manage.py migrate

# 3. Popular com dados iniciais
python manage.py populate_new_games
```

O comando `populate_new_games` irá criar automaticamente:
- ✅ 9 símbolos para o Slot Machine
- ✅ 12 prêmios configurados
- ✅ Configuração do Dice Game
- ✅ 12 tipos de peixes
- ✅ 4 tipos de iscas

---

## 🎰 Slot Machine

### Primeira Configuração:

1. **Execute o comando de população** (acima)
2. **Acesse:** `/app/game/slot-machine/manager/`
3. **Verifique:**
   - ✅ Símbolos cadastrados (deve ter 9)
   - ✅ Prêmios configurados (deve ter 12)
   - ✅ Configuração ativa

### Como Adicionar Símbolos Manualmente:

Se por algum motivo não tiver símbolos:

1. Acesse: `/app/game/slot-machine/manager/`
2. Clique em "➕ Adicionar Símbolo"
3. Preencha:
   - **Símbolo:** Escolha da lista (sword, shield, gem, etc.)
   - **Ícone/Emoji:** Digite um emoji (⚔️, 🛡️, 💎, etc.)
   - **Peso:** Quanto maior, mais comum (ex: 15)
4. Clique "➕"

### Como Adicionar Prêmios:

1. **Certifique-se que tem símbolos cadastrados primeiro!**
2. Clique em "➕ Adicionar Prêmio"
3. Preencha:
   - **Símbolo:** Escolha qual símbolo
   - **Combinações:** 2 ou 3 símbolos iguais
   - **Item:** (Opcional) Escolha um item do sistema
   - **Fichas:** Quantidade de fichas de prêmio
4. Clique "➕ Adicionar"

### Exemplo de Configuração:

```
Símbolo: Jackpot 💰
Combinações: 3
Item: (nenhum)
Fichas: 10000

Símbolo: Gema 💎
Combinações: 3
Item: (opcional: Blessed Scroll)
Fichas: 500

Símbolo: Espada ⚔️
Combinações: 2
Item: (nenhum)
Fichas: 50
```

---

## 🎲 Dice Game

### Primeira Configuração:

1. **Execute o comando de população**
2. **Acesse:** `/app/game/dice-game/manager/`
3. **Edite a configuração** se necessário:
   - Aposta mínima/máxima
   - Multiplicadores

### Configuração Padrão:

```
Aposta Mínima: 1 ficha
Aposta Máxima: 100 fichas
Multiplicador Número Específico: x5.0
Multiplicador Par/Ímpar: x2.0
Multiplicador Alto/Baixo: x2.0
```

---

## 🎣 Fishing Game

### Primeira Configuração:

1. **Execute o comando de população**
2. **Acesse:** `/app/game/fishing/manager/`
3. **Verifique:**
   - ✅ 12 peixes cadastrados
   - ✅ 4 iscas disponíveis

### Como Adicionar Peixes:

1. Clique em "➕ Adicionar Peixe"
2. Preencha:
   - **Nome:** Nome do peixe (ex: "Atum Azul")
   - **Imagem:** Upload de imagem do peixe
   - **Raridade:** comum, raro, épico ou lendário
   - **Nível Mínimo:** Level de vara necessário
   - **Peso:** Chance de captura (quanto maior, mais comum)
   - **XP:** Experiência ganha ao capturar
   - **Fichas:** Fichas ganhas ao capturar
   - **Item:** (Opcional) Item do sistema como recompensa
3. Clique "➕ Adicionar"

### Como Adicionar Iscas:

1. Clique em "➕ Adicionar Isca"
2. Preencha:
   - **Nome:** Nome da isca
   - **Descrição:** Descrição do efeito
   - **Preço:** Custo em fichas
   - **Raridade Beneficiada:** Qual raridade tem bônus
   - **Bônus (%):** Percentual de aumento de chance
   - **Duração:** Quantos minutos dura
3. Clique "➕ Adicionar"

---

## 📍 URLs de Acesso

### Jogar:
- **Slot Machine:** `/app/game/slot-machine/`
- **Dice Game:** `/app/game/dice-game/`
- **Fishing:** `/app/game/fishing/`

### Gerenciar:
- **Slot Machine Manager:** `/app/game/slot-machine/manager/`
- **Dice Game Manager:** `/app/game/dice-game/manager/`
- **Fishing Manager:** `/app/game/fishing/manager/`

### Pelo Config Hub:
- **Acesse:** `/config/hub/`
- **Veja os 3 novos gerenciadores** com badge "NOVO"

---

## ⚠️ Solução de Problemas

### "Nenhum símbolo disponível" no Slot Machine

**Solução:**
```bash
python manage.py populate_new_games
```

Ou adicione manualmente em `/app/game/slot-machine/manager/`

### "Nenhum peixe disponível"

**Solução:**
```bash
python manage.py populate_new_games
```

Ou adicione manualmente em `/app/game/fishing/manager/`

### "Erro ao criar migrations"

**Solução:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 💡 Dicas

1. **Use Items existentes** como prêmios nos jogos
2. **Ajuste os multiplicadores** para equilibrar a economia
3. **Monitore as estatísticas** para ver se os jogos estão balanceados
4. **Peixes lendários** devem ser raros e valiosos
5. **Iscas** ajudam jogadores a progredir mais rápido

---

## 🎯 Checklist de Ativação

- [ ] Rodar migrations (`makemigrations` e `migrate`)
- [ ] Popular dados iniciais (`populate_new_games`)
- [ ] Verificar Config Hub (`/config/hub/`)
- [ ] Testar cada jogo
- [ ] Ajustar valores se necessário
- [ ] Informar os jogadores sobre os novos jogos!

---

**Pronto para jogar!** 🎉

