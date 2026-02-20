# 📚 Documentação do Gerador Automático de Queries para Lineage 2

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Objetivo](#objetivo)
3. [Como Funciona](#como-funciona)
4. [Etapas de Execução](#etapas-de-execução)
5. [Detalhamento das Funções](#detalhamento-das-funções)
6. [Estrutura de Configuração](#estrutura-de-configuração)
7. [Geração do Arquivo Final](#geração-do-arquivo-final)
8. [Tabelas Detectadas](#tabelas-detectadas)
9. [Compatibilidade](#compatibilidade)
10. [Como Usar](#como-usar)

---

## 🎯 Visão Geral

O **Gerador Automático de Queries** (`gerar_query.py`) é um script Python interativo que se conecta ao banco de dados real de um servidor Lineage 2 e gera automaticamente um arquivo Python (`query_*.py`) contendo todas as consultas SQL necessárias para integração com o sistema web.

Este gerador resolve um problema crítico: **diferentes versões de servidores Lineage 2 (Mobius, L2J, aCis, etc.) possuem schemas de banco de dados diferentes**, com nomes de colunas, tabelas e estruturas variadas. Criar manualmente queries para cada versão seria trabalhoso e propenso a erros.

---

## 🎯 Objetivo

**Automatizar a criação de queries SQL adaptadas ao schema específico de cada servidor Lineage 2**, eliminando a necessidade de:
- Escrever queries manualmente para cada versão
- Conhecer detalhes específicos do schema do banco
- Manter múltiplas versões de código para diferentes servidores
- Corrigir erros causados por nomes de colunas incorretos

---

## ⚙️ Como Funciona

### Fluxo Geral

```
1. Usuário informa nome do projeto (ex: mobius, l2jpremium)
2. Script verifica configurações do .env
3. Script conecta ao banco de dados real
4. Script mapeia o schema (tabelas e colunas)
5. Script detecta padrões e configurações
6. Script gera arquivo query_[projeto].py
7. Arquivo pronto para uso!
```

### Princípio de Funcionamento

O gerador utiliza **introspecção do banco de dados** para:
1. **Descobrir quais tabelas existem**
2. **Identificar as colunas de cada tabela**
3. **Detectar chaves primárias**
4. **Inferir padrões de nomenclatura** (ex: `charId` vs `char_id` vs `obj_Id`)
5. **Adaptar queries automaticamente** para corresponder ao schema real

---

## 📝 Etapas de Execução

### **ETAPA 0: Nome do Projeto**
- Solicita ao usuário o nome identificador do projeto
- Exemplo: `mobius`, `l2jpremium`, `acis`
- Este nome será usado no arquivo gerado (`query_mobius.py`)

### **ETAPA 1: Verificação de Configuração**
**Função:** `verificar_banco_configurado()`

Verifica se todas as variáveis necessárias estão configuradas no arquivo `.env`:
- `LINEAGE_DB_ENABLED` - Se o banco está habilitado
- `LINEAGE_DB_HOST` - Endereço do servidor MySQL
- `LINEAGE_DB_USER` - Usuário do banco
- `LINEAGE_DB_PASSWORD` - Senha (oculta na exibição)
- `LINEAGE_DB_NAME` - Nome do banco de dados
- `LINEAGE_DB_PORT` - Porta (padrão: 3306)

**Saída:**
```
✅ LINEAGE_DB_HOST: localhost
✅ LINEAGE_DB_USER: root
✅ LINEAGE_DB_PASSWORD: ***
✅ LINEAGE_DB_NAME: l2jserver
✅ LINEAGE_DB_PORT: 3306
```

### **ETAPA 2: Teste de Conexão**
**Função:** `testar_conexao()`

Tenta conectar ao banco de dados usando as credenciais do `.env`:
- Estabelece conexão com timeout de 5 segundos
- Executa query `SELECT VERSION()` para verificar conectividade
- Exibe versão do MySQL/MariaDB

**Saída:**
```
✅ Conectado com sucesso!
📊 Versão MySQL: 8.0.32
```

### **ETAPA 3: Mapeamento do Schema**
**Função:** `mapear_schema_banco()`

Esta é a etapa mais importante. O script:

1. **Define lista de tabelas importantes:**
```python
tabelas_importantes = [
    'characters',           # Personagens
    'character_subclasses', # Subclasses
    'accounts',            # Contas
    'clan_data',           # Clans
    'clan_subpledges',     # Sub-pledges dos clans
    'ally_data',           # Alianças
    'items',               # Itens
    'olympiad_nobles',     # Olympiad
    'heroes',              # Heróis
    'castle',              # Castelos
    'grandboss_data',      # Grand Bosses
    'epic_boss_spawn',     # Epic Bosses (Mobius)
    'raidboss_spawnlist',  # Raid Bosses
    'raidboss_status',     # Status Raid Bosses (Mobius)
    'siege_clans'          # Sieges
]
```

2. **Para cada tabela:**
   - Executa `SHOW COLUMNS FROM [tabela]`
   - Armazena informações de cada coluna:
     - Nome da coluna
     - Tipo de dado
     - Se é chave primária (PRI)

3. **Cria estrutura de schema:**
```python
schema = {
    'characters': {
        'columns': {
            'charId': 'int(11)',
            'char_name': 'varchar(35)',
            'level': 'tinyint(4)',
            'accessLevel': 'int(11)',
            # ...
        },
        'primary_key': 'charId'
    },
    # ... outras tabelas
}
```

**Saída:**
```
✅ characters: 87 colunas
✅ accounts: 23 colunas
✅ clan_data: 34 colunas
⚠️  epic_boss_spawn: não encontrada (opcional)
```

### **ETAPA 4: Detecção de Configurações**
**Função:** `detectar_configuracoes(schema)`

Analisa o schema mapeado e **detecta automaticamente os padrões específicos do servidor**:

#### **4.1. Detecção de ID do Personagem**
Procura por variações comuns:
- `obj_Id` (L2J antigo)
- `charId` (Mobius)
- `char_id` (outras versões)

```python
for candidate in ['obj_Id', 'charId', 'char_id']:
    if candidate in char_cols:
        config['char_id'] = candidate
        break
```

#### **4.2. Detecção de Access Level**
Diferencia entre duas tabelas:
- **Tabela `accounts`:** `accesslevel`, `accessLevel`, `access_level`
- **Tabela `characters`:** `accessLevel`, `accesslevel`, `access_level`

Importante: podem ter nomenclaturas diferentes na mesma base!

#### **4.3. Detecção de Coluna de Classe**
Procura por:
- `base_class` (comum em L2J)
- `classid` (Mobius)
- `class_id` (variações)

Pode ser `None` se a classe só existe na tabela `character_subclasses`.

#### **4.4. Detecção de Subclasses**
Verifica se existe tabela `character_subclasses` e detecta:
- Coluna de ID: `char_obj_id`, `charId`, `char_id`
- **Filtro de classe base vs subclasse:**
  - **Mobius:** usa coluna `isBase` (`'1'` = base, `'0'` = sub)
  - **L2J clássico:** usa `class_index` (`0` = base, `>0` = sub)

```python
if 'isBase' in subclass_cols:
    config['subclass_filter_base'] = "isBase = '1'"
    config['subclass_filter_sub'] = "isBase = '0'"
elif 'class_index' in subclass_cols:
    config['subclass_filter_base'] = "class_index = 0"
    config['subclass_filter_sub'] = "class_index > 0"
```

#### **4.5. Detecção de Estrutura de Clans**
Identifica onde está o nome do clan:

**Opção 1: Diretamente em `clan_data`**
```sql
SELECT clan_name FROM clan_data WHERE clan_id = ?
```

**Opção 2: Em `clan_subpledges` com filtro**
```sql
SELECT name FROM clan_subpledges 
WHERE clan_id = ? AND sub_pledge_id = 0
```

**Opção 3: Em `clan_subpledges` sem filtro**
```sql
SELECT name FROM clan_subpledges WHERE clan_id = ?
```

Também detecta:
- Coluna de ID do clan: `clan_id`, `clanId`, `id`
- Coluna de crest: `crest_id`, `crestId`, `crest`
- Coluna de líder: `leader_id`, `leaderId`, `leader`

#### **4.6. Detecção de Alianças**
Verifica se existe tabela `ally_data` separada ou se usa `clan_data.ally_id`.

#### **4.7. Detecção de Castelos**
Detecta colunas de:
- **Data de siege:** `siegeDate`, `siege_date`, `next_siege_date`
- **Tesouro:** `treasury`, `tax_income`, `tax_money`

#### **4.8. Detecção de Raid Bosses**
Identifica qual tabela usar:
- `raidboss_spawnlist` (L2J clássico)
- `raidboss_status` (Mobius)

Detecta colunas de:
- **ID:** `boss_id`, `id`, `npc_id`
- **Respawn:** `respawn_time`, `respawn_delay`, `date_of_death`

#### **4.9. Detecção de Grand Bosses**
Identifica qual tabela usar:
- `grandboss_data` (L2J clássico)
- `epic_boss_spawn` (Mobius)

Detecta colunas de:
- **ID:** `boss_id`, `bossId`, `id`
- **Respawn:** `respawn_time`, `respawnDate`, `respawn_date`

**Saída:**
```
✅ ID do personagem: charId
✅ Access level (accounts): accesslevel
✅ Access level (characters): accessLevel
✅ Tem tabela character_subclasses
✅ ID em subclass: charId
✅ Filtro de subclass: isBase
✅ ID do clan: clan_id
✅ Coluna de crest: crest_id
✅ Nome do clan: clan_subpledges.name (sub_pledge_id = 0)
✅ Tem tabela ally_data separada
```

### **ETAPA 5: Geração do Arquivo**
**Função:** `gerar_arquivo_query(nome_projeto, schema, config)`

Gera o arquivo Python final em várias etapas:

#### **5.1. Importação de Templates**
Importa geradores de código para cada classe:
```python
from classes.lineage_stats import get_lineage_stats_template
from classes.lineage_services import get_lineage_services_template
from classes.lineage_account import get_lineage_account_template
from classes.transfer_wallet_to_char import get_transfer_wallet_to_char_template
from classes.transfer_char_to_wallet import get_transfer_char_to_wallet_template
from classes.lineage_marketplace import get_lineage_marketplace_template
from classes.lineage_inflation import get_lineage_inflation_template
```

#### **5.2. Geração de Cada Classe**
Cada template recebe as configurações detectadas e gera código Python adaptado:

```python
stats_code = get_lineage_stats_template(
    char_id=config['char_id'],                    # 'charId' ou 'obj_Id'
    access_level=config['access_level_characters'], # 'accessLevel' ou 'accesslevel'
    has_subclass=config['has_subclass'],          # True/False
    subclass_char_id=config['subclass_char_id'],  # Coluna ID na subclass
    clan_structure=clan_structure,                # Estrutura de clans
    base_class_col=config['base_class_col'],      # 'classid' ou None
    # ... mais parâmetros
)
```

#### **5.3. Montagem do Arquivo Final**
Cria arquivo com estrutura:

```python
"""
Query File: query_mobius.py
Generated automatically by Query Generator
Date: 2025-12-05 14:30:00
Database Schema: mobius
"""

# Imports
from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result
import time, base64, hashlib
from datetime import datetime

# Configurações (constantes geradas)
CHAR_ID = 'charId'
ACCESS_LEVEL = 'accesslevel'
BASE_CLASS_COL = 'classid'
# ...

# Classes geradas
class LineageStats:
    # ... código gerado

class LineageServices:
    # ... código gerado

# ... outras classes
```

#### **5.4. Salvamento**
- Salva em: `apps/lineage/server/querys/query_[projeto].py`
- Cria backup se já existir: `query_[projeto].py.backup`

**Saída:**
```
📝 Gerando classe LineageStats...
📝 Gerando classe LineageServices...
📝 Gerando classe LineageAccount...
📝 Gerando classe TransferFromWalletToChar...
📝 Gerando classe TransferFromCharToWallet...
📝 Gerando classe LineageMarketplace...
📝 Gerando classe LineageInflation...
💾 Backup: query_mobius.py.backup
✅ Arquivo gerado: query_mobius.py
```

---

## 🔧 Estrutura de Configuração

O objeto `config` gerado contém todas as configurações detectadas:

```python
config = {
    # === PERSONAGENS ===
    'char_id': 'charId',                           # ID do personagem
    'access_level': 'accesslevel',                 # Access level (accounts)
    'access_level_characters': 'accessLevel',      # Access level (characters)
    'base_class_col': 'classid',                   # Coluna de classe
    
    # === SUBCLASSES ===
    'has_subclass': True,                          # Tem tabela de subclass?
    'subclass_char_id': 'charId',                  # ID na tabela de subclass
    'subclass_filter_base': "isBase = '1'",        # Filtro para classe base
    'subclass_filter_sub': "isBase = '0'",         # Filtro para subclasses
    
    # === CLANS ===
    'clan_name_source': 'clan_subpledges',         # Origem do nome do clan
    'subpledge_filter': 'sub_pledge_id',           # Campo de filtro
    'clan_id_col': 'clan_id',                      # ID do clan
    'crest_col': 'crest_id',                       # Coluna de crest
    'clan_leader_col': 'leader_id',                # Coluna de líder
    
    # === ALIANÇAS ===
    'has_ally_data': True,                         # Tabela ally_data existe?
    
    # === CASTELOS ===
    'castle_siege_date_col': 'siegeDate',          # Coluna de data de siege
    'castle_treasury_col': 'treasury',             # Coluna de tesouro
    
    # === RAID BOSSES ===
    'has_raidboss_table': True,                    # Tabela de raid existe?
    'raidboss_table_name': 'raidboss_status',      # Nome da tabela
    'raidboss_id_col': 'id',                       # Coluna de ID
    'raidboss_respawn_col': 'respawn_delay',       # Coluna de respawn
    
    # === GRAND BOSSES ===
    'has_grandboss_table': True,                   # Tabela de grand boss existe?
    'grandboss_table_name': 'epic_boss_spawn',     # Nome da tabela
    'grandboss_id_col': 'bossId',                  # Coluna de ID
    'grandboss_respawn_col': 'respawnDate',        # Coluna de respawn
}
```

---

## 📦 Geração do Arquivo Final

O arquivo gerado (`query_[projeto].py`) contém:

### **1. Cabeçalho e Imports**
```python
"""
Query File: query_mobius.py
Generated automatically by Query Generator
Date: 2025-12-05 14:30:00
"""

from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result
import time, base64, hashlib
from datetime import datetime
```

### **2. Constantes de Configuração**
```python
# Tabela: characters
CHAR_ID = 'charId'
ACCESS_LEVEL = 'accesslevel'
BASE_CLASS_COL = 'classid'

# Tabela: character_subclasses
HAS_SUBCLASS = True
SUBCLASS_CHAR_ID = 'charId'

# Estrutura de Clans
CLAN_NAME_SOURCE = 'clan_subpledges'
SUBPLEDGE_FILTER = 'sub_pledge_id'
HAS_ALLY_DATA = True
```

### **3. Classes Geradas**

#### **LineageStats**
Queries para estatísticas do servidor:
- `get_online_players()` - Jogadores online
- `get_top_pvp()` - Ranking PvP
- `get_top_pk()` - Ranking PK
- `get_top_level()` - Ranking Level
- `get_clan_ranking()` - Ranking de Clans
- `get_castle_owners()` - Donos de castelos
- `get_heroes()` - Heróis atuais
- `get_grand_olympiad_ranking()` - Ranking Olympiad
- `get_raidboss_status()` - Status de Raid Bosses
- `get_grandboss_status()` - Status de Grand Bosses

#### **LineageServices**
Serviços administrativos:
- `get_character_info()` - Informações do personagem
- `change_character_name()` - Alterar nome
- `change_character_class()` - Alterar classe
- `set_character_level()` - Definir level
- `give_item_to_character()` - Dar item
- `set_clan_reputation()` - Definir reputação do clan

#### **LineageAccount**
Gerenciamento de contas:
- `get_account_info()` - Informações da conta
- `verify_account_credentials()` - Verificar credenciais
- `update_account_password()` - Atualizar senha

#### **TransferFromWalletToChar**
Transferência de moeda (wallet → personagem):
- `transfer()` - Executar transferência

#### **TransferFromCharToWallet**
Transferência de moeda (personagem → wallet):
- `transfer()` - Executar transferência

#### **LineageMarketplace**
Marketplace de itens:
- `get_items_for_sale()` - Itens à venda
- `buy_item()` - Comprar item
- `sell_item()` - Vender item

#### **LineageInflation**
Análise econômica:
- `get_currency_circulation()` - Circulação de moeda
- `get_item_inflation()` - Inflação de itens

---

## 📊 Tabelas Detectadas

### **Tabelas Obrigatórias**
- `characters` - Personagens do jogo
- `accounts` - Contas de usuários

### **Tabelas Opcionais**
- `character_subclasses` - Sistema de subclasses
- `clan_data` - Dados dos clans
- `clan_subpledges` - Sub-pledges (Royal Guard, etc)
- `ally_data` - Alianças entre clans
- `items` - Itens dos jogadores
- `olympiad_nobles` - Participantes da Olympiad
- `heroes` - Heróis do mês
- `castle` - Castelos e sieges
- `grandboss_data` / `epic_boss_spawn` - Grand Bosses
- `raidboss_spawnlist` / `raidboss_status` - Raid Bosses
- `siege_clans` - Clans participando de sieges

---

## 🔀 Compatibilidade

O gerador foi desenvolvido para suportar múltiplas versões de servidores Lineage 2:

### **Mobius (L2J Mobius)**
- `charId` como ID
- `isBase` para diferenciar subclasses
- `epic_boss_spawn` para grand bosses
- `raidboss_status` para raids
- `accessLevel` em characters

### **L2J Premium**
- `obj_Id` como ID
- `class_index` para subclasses
- `grandboss_data` para grand bosses
- `raidboss_spawnlist` para raids

### **aCis**
- Similar ao L2J clássico
- Pode ter variações em nomes de colunas

### **L2OFF (C4-Interlude)**
- Estrutura mais simples
- Menos tabelas opcionais

---

## 🚀 Como Usar

### **Pré-requisitos**
1. Servidor Lineage 2 com banco MySQL/MariaDB
2. Python 3.8+
3. Arquivo `.env` configurado com credenciais do banco

### **Configuração do .env**
```bash
LINEAGE_DB_ENABLED=true
LINEAGE_DB_HOST=localhost
LINEAGE_DB_PORT=3306
LINEAGE_DB_USER=root
LINEAGE_DB_PASSWORD=sua_senha
LINEAGE_DB_NAME=l2jserver
```

### **Execução**
```bash
cd apps/lineage/server/generate_query
python gerar_query.py
```

### **Processo Interativo**
```
🔧 GERADOR AUTOMÁTICO DE QUERIES LINEAGE 2

📋 ETAPA 0: Nome do projeto
Digite o nome do projeto: mobius

📋 ETAPA 1: Verificando configuração do banco
✅ LINEAGE_DB_HOST: localhost
✅ LINEAGE_DB_USER: root
✅ LINEAGE_DB_PASSWORD: ***

📋 ETAPA 2: Testando conexão com o banco
✅ Conectado com sucesso!
📊 Versão MySQL: 8.0.32

📋 ETAPA 3: Mapeando schema do banco
✅ characters: 87 colunas
✅ accounts: 23 colunas
...

📋 ETAPA 4: Detectando configurações do schema
✅ ID do personagem: charId
✅ Access level (characters): accessLevel
...

📋 RESUMO DA CONFIGURAÇÃO
Projeto: mobius
Tabelas encontradas: 12
ID do personagem: charId
...

Gerar arquivo query_mobius.py? (s/n): s

📋 ETAPA 5: Gerando arquivo de query
📝 Gerando classe LineageStats...
...
✅ Arquivo gerado: query_mobius.py

✅ ARQUIVO GERADO COM SUCESSO!
```

### **Resultado**
Arquivo criado em:
```
apps/lineage/server/querys/query_mobius.py
```

Pronto para ser usado nas views Django!

---

## 📝 Notas Importantes

### **1. Backup Automático**
- Se já existir um arquivo query, será criado backup automaticamente
- Backup salvo como: `query_[projeto].py.backup`

### **2. Constantes no Código**
O arquivo gerado usa **constantes** para nomes de colunas:

❌ **ERRADO:**
```python
char['charId']  # Hardcoded!
```

✅ **CERTO:**
```python
char[CHAR_ID]  # Usa constante gerada
```

### **3. Regeneração**
Para atualizar queries após mudanças no banco:
```bash
python gerar_query.py
```

### **4. Múltiplos Servidores**
É possível ter queries para vários servidores:
- `query_mobius.py`
- `query_l2jpremium.py`
- `query_acis.py`

Basta executar o gerador para cada servidor.

---

## 🎓 Conclusão

O Gerador Automático de Queries é uma ferramenta essencial que:
- ✅ **Economiza tempo** - não precisa escrever queries manualmente
- ✅ **Evita erros** - detecta automaticamente nomes de colunas
- ✅ **Suporta múltiplas versões** - funciona com Mobius, L2J, aCis, etc
- ✅ **É inteligente** - adapta-se a diferentes estruturas de banco
- ✅ **Mantém consistência** - usa constantes para evitar hardcoding

Com esta ferramenta, a integração entre o servidor Lineage 2 e o sistema web torna-se **simples, rápida e confiável**! 🚀

