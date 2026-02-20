# Sistema de Inflação de Itens - Documentação Completa

## Visão Geral

O Sistema de Inflação de Itens é uma ferramenta de análise e monitoramento que permite ao staff do servidor acompanhar a quantidade, distribuição e variação de todos os itens no servidor Lineage 2. O sistema verifica todos os inventários dos jogadores, categoriza os itens e rastreia onde estão armazenados (inventário, baú, equipado, baú do clã ou no site).

---

## Índice

1. [Conceitos Fundamentais](#conceitos-fundamentais)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Funcionalidades](#funcionalidades)
4. [Como Usar](#como-usar)
5. [Modelos Django](#modelos-django)
6. [Classes de Query](#classes-de-query)
7. [API e Endpoints](#api-e-endpoints)
8. [Troubleshooting](#troubleshooting)

---

## Conceitos Fundamentais

### O que é Inflação de Itens?

Inflação de itens refere-se ao aumento ou diminuição da quantidade total de itens no servidor ao longo do tempo. O sistema monitora:

- **Quantidade total** de cada item
- **Onde estão armazenados** (localização)
- **Quantos jogadores possuem** cada item
- **Número de instâncias** (útil para itens não empilháveis)
- **Variações ao longo do tempo** (consumo, drop, armazenamento)

### Snapshots

Snapshots são "fotografias" do estado atual dos itens em um momento específico. Eles capturam:

- Data e hora da captura
- Total de personagens no servidor
- Total de instâncias de itens
- Quantidade total de itens
- Detalhes de cada item por localização

**Importante:** Apenas um snapshot pode ser criado por dia para evitar duplicações.

### Localizações dos Itens

O sistema rastreia itens em 5 localizações diferentes:

1. **INVENTORY** - Itens no inventário dos personagens
2. **WAREHOUSE** - Itens armazenados no baú pessoal
3. **PAPERDOLL** - Itens equipados nos personagens
4. **CLANWH** - Itens no baú do clã
5. **SITE** - Itens armazenados no inventário do site (Django)

### Categorias de Itens

Categorias permitem agrupar itens relacionados para análise. Exemplos:

- **Armas** - Espadas, arcos, cajados, etc.
- **Armaduras** - Capacetes, peitorais, botas, etc.
- **Consumíveis** - Poções, scrolls, etc.
- **Materiais** - Cristais, gemas, etc.

Cada categoria pode ter:
- Nome e descrição
- Lista de IDs de itens pertencentes à categoria
- Cor para visualização
- Ordem de exibição

---

## Arquitetura do Sistema

### Componentes Principais

```
apps/lineage/server/
├── models.py                    # Modelos Django (ItemInflationSnapshot, etc.)
├── querys/                      # Classes de query para diferentes schemas
│   ├── query_dreamv3.py        # Schema Dream v3
│   ├── query_classic.py        # Schema Classic
│   ├── query_dreamv2.py        # Schema Dream v2
│   └── ...                     # Outros schemas
├── views/
│   └── inflation_views.py      # Views do painel de inflação
└── templates/
    └── server/inflation/       # Templates do painel
        ├── dashboard.html
        ├── snapshot_detail.html
        ├── comparison.html
        └── categories.html
```

### Fluxo de Dados

1. **Coleta de Dados**
   - As queries acessam o banco de dados do Lineage 2
   - Buscam todos os itens de todos os personagens
   - Agrupam por localização e item

2. **Processamento**
   - Enriquece itens com nomes (CustomItem ou itens.json)
   - Calcula estatísticas agregadas
   - Associa categorias quando aplicável

3. **Armazenamento**
   - Cria snapshots no banco Django
   - Salva detalhes de cada item
   - Mantém histórico para comparações

4. **Visualização**
   - Dashboard mostra dados em tempo real
   - Snapshots permitem análise histórica
   - Comparação mostra variações entre períodos

---

## Funcionalidades

### 1. Dashboard Principal

**URL:** `/app/server/inflation/`

**Funcionalidades:**
- Estatísticas gerais em tempo real
- Resumo por localização
- Top 20 itens mais comuns
- Lista de snapshots recentes
- Botão para criar novo snapshot

**Estatísticas Exibidas:**
- Total de Instâncias
- Total de Itens
- Total de Personagens
- Itens no Site

### 2. Criar Snapshot

**URL:** `/app/server/inflation/snapshot/create/`

**Processo:**
1. Verifica se já existe snapshot para hoje
2. Busca todos os itens do servidor
3. Calcula totais e estatísticas
4. Salva snapshot com data atual
5. Cria detalhes para cada item/localização
6. Inclui itens do site (Django)

**Limitações:**
- Apenas um snapshot por dia
- Processo pode levar alguns segundos em servidores grandes

### 3. Detalhes do Snapshot

**URL:** `/app/server/inflation/snapshot/<id>/`

**Informações Exibidas:**
- Data do snapshot
- Estatísticas gerais
- Resumo por localização
- Top 100 itens com detalhes
- Observações (se houver)

### 4. Comparação de Snapshots

**URL:** `/app/server/inflation/comparison/`

**Funcionalidades:**
- Seleciona dois snapshots para comparar
- Mostra variação de quantidade
- Calcula percentual de mudança
- Identifica itens que apareceram/desapareceram
- Ordena por maior variação

**Métricas de Comparação:**
- Quantidade inicial vs final
- Mudança absoluta
- Percentual de variação
- Categoria do item

### 5. Gerenciamento de Categorias

**URL:** `/app/server/inflation/categories/`

**Funcionalidades:**
- Criar novas categorias
- Definir IDs de itens por categoria
- Escolher cor para visualização
- Definir ordem de exibição
- Deletar categorias

**Uso:**
- Organizar análise por grupos
- Filtrar itens relacionados
- Identificar padrões de inflação

---

## Como Usar

### Passo 1: Acessar o Painel

1. Faça login como staff
2. Acesse `/app/server/inflation/`
3. Visualize as estatísticas em tempo real

### Passo 2: Criar Categorias (Opcional)

1. Clique em "Categorias"
2. Preencha o formulário:
   - Nome da categoria
   - IDs dos itens (separados por vírgula)
   - Cor para visualização
   - Ordem
3. Clique em "Criar Categoria"

**Exemplo:**
```
Nome: Armas
IDs: 1, 2, 3, 4, 5
Cor: #ff0000
Ordem: 1
```

### Passo 3: Criar Snapshot

1. No dashboard, clique em "Criar Snapshot"
2. Confirme a ação
3. Aguarde o processamento
4. O snapshot será criado com a data atual

**Dica:** Crie snapshots regularmente (diariamente ou semanalmente) para ter um histórico completo.

### Passo 4: Analisar Dados

1. **Ver Detalhes:**
   - Clique em "Ver" em qualquer snapshot
   - Analise os itens por localização

2. **Comparar Períodos:**
   - Acesse "Comparar Snapshots"
   - Selecione dois snapshots
   - Analise as variações

3. **Identificar Padrões:**
   - Use categorias para agrupar itens
   - Compare períodos diferentes
   - Identifique consumo excessivo ou drops anômalos

---

## Modelos Django

### ItemInflationCategory

Armazena categorias de itens para organização.

**Campos:**
- `name` - Nome da categoria
- `description` - Descrição opcional
- `item_ids` - Lista de IDs de itens (JSON)
- `color` - Cor hex para visualização
- `order` - Ordem de exibição

**Uso:**
```python
category = ItemInflationCategory.objects.create(
    name="Armas",
    item_ids=[1, 2, 3, 4, 5],
    color="#ff0000",
    order=1
)
```

### ItemInflationSnapshot

Representa um snapshot do estado dos itens em uma data específica.

**Campos:**
- `snapshot_date` - Data do snapshot (único)
- `total_characters` - Total de personagens
- `total_items_instances` - Total de instâncias
- `total_items_quantity` - Quantidade total de itens
- `notes` - Observações opcionais

**Relacionamentos:**
- `details` - ItemInflationSnapshotDetail (muitos)

### ItemInflationSnapshotDetail

Detalhes de cada item em um snapshot.

**Campos:**
- `snapshot` - ForeignKey para ItemInflationSnapshot
- `item_id` - ID do item
- `item_name` - Nome do item
- `location` - Localização (INVENTORY, WAREHOUSE, etc.)
- `quantity` - Quantidade total
- `instances` - Número de instâncias
- `unique_owners` - Proprietários únicos
- `category` - ForeignKey para ItemInflationCategory (opcional)

**Índices:**
- `snapshot + item_id + location` (único)
- `snapshot + item_id`
- `snapshot + location`
- `snapshot + category`

### ItemInflationStats

Estatísticas agregadas de inflação (para uso futuro).

**Campos:**
- `item_id` - ID do item
- `location` - Localização
- `current_quantity` - Quantidade atual
- `previous_quantity` - Quantidade anterior
- `quantity_change` - Mudança absoluta
- `change_percentage` - Percentual de mudança
- `calculated_at` - Data do cálculo
- `category` - Categoria (opcional)

---

## Classes de Query

### LineageInflation

Classe presente em todos os arquivos de query (`query_*.py`) com métodos para análise de inflação.

#### Métodos Disponíveis

##### `get_all_items_by_location()`

Busca todos os itens de todos os personagens, agrupados por localização.

**Retorna:**
```python
[
    {
        'item_id': 57,
        'quantity': 1000000,
        'location': 'INVENTORY',
        'owner_id': 12345,
        'char_name': 'PlayerName',
        'account_name': 'account',
        'item_name': 'Adena',
        'item_category': None,
        'crystal_type': None,
        'enchant': 0
    },
    ...
]
```

##### `get_items_summary_by_category()`

Resumo de itens agrupados por categoria e localização.

**Retorna:**
```python
[
    {
        'item_id': 57,
        'item_name': 'Adena',
        'item_category': None,
        'crystal_type': None,
        'location': 'INVENTORY',
        'total_instances': 100,
        'total_quantity': 100000000,
        'unique_owners': 50,
        'min_enchant': 0,
        'max_enchant': 0,
        'avg_enchant': 0
    },
    ...
]
```

##### `get_items_by_character(char_id=None)`

Busca todos os itens de um personagem específico ou de todos.

**Parâmetros:**
- `char_id` (opcional) - ID do personagem

**Retorna:** Lista de itens do personagem ou de todos

##### `get_top_items_by_quantity(limit=100)`

Retorna os itens mais comuns no servidor.

**Parâmetros:**
- `limit` - Número máximo de itens (padrão: 100)

**Retorna:**
```python
[
    {
        'item_id': 57,
        'item_name': 'Adena',
        'item_category': None,
        'total_quantity': 1000000000,
        'unique_owners': 500,
        'total_instances': 1000
    },
    ...
]
```

##### `get_items_by_location_summary()`

Resumo de itens por localização.

**Retorna:**
```python
[
    {
        'location': 'INVENTORY',
        'unique_item_types': 100,
        'total_instances': 5000,
        'total_quantity': 50000000,
        'unique_owners': 200
    },
    ...
]
```

##### `get_site_items_count()`

Conta itens armazenados no site (preparado para integração).

**Retorna:** Lista vazia (será implementado)

##### `get_inflation_comparison(date_from=None, date_to=None)`

Compara a quantidade de itens entre duas datas (preparado para integração).

**Retorna:** Estrutura de comparação

### Schemas Suportados

O sistema suporta diferentes schemas de banco de dados:

1. **Dream v3** (`query_dreamv3.py`)
   - Campos: `item_type`, `amount`, `location`, `obj_Id`

2. **Classic** (`query_classic.py`)
   - Campos: `item_type`, `amount`, `location`, `obj_Id`

3. **Dream v2** (`query_dreamv2.py`)
   - Campos: `item_id`, `count`, `loc`, `charId`

4. **Lucera v2** (`query_lucerav2.py`)
   - Campos: `item_id`, `item_type`, `amount`, `location`, `obj_Id`

5. **ACIS v1** (`query_acis_v1.py`)
   - Campos: `item_id`, `count`, `loc`, `obj_Id`

6. **ACIS v2** (`query_acis_v2.py`)
   - Campos: `item_id`, `count`, `loc`, `obj_Id`

7. **RuACIS** (`query_ruacis.py`)
   - Campos: `item_id`, `count`, `loc`, `obj_Id`

8. **L2JPremium** (`query_l2jpremium.py`)
   - Campos: `item_id`, `count`, `loc`, `charId`

**Nota:** O sistema detecta automaticamente qual schema usar baseado na configuração `LINEAGE_QUERY_MODULE`.

---

## API e Endpoints

### URLs Disponíveis

| URL | Descrição | Método | Permissão |
|-----|-----------|--------|-----------|
| `/app/server/inflation/` | Dashboard principal | GET | Staff |
| `/app/server/inflation/snapshot/create/` | Criar snapshot | POST | Staff |
| `/app/server/inflation/snapshot/<id>/` | Detalhes do snapshot | GET | Staff |
| `/app/server/inflation/snapshot/<id>/delete/` | Deletar snapshot | POST | Staff |
| `/app/server/inflation/comparison/` | Comparar snapshots | GET | Staff |
| `/app/server/inflation/categories/` | Gerenciar categorias | GET/POST | Staff |

### Exemplo de Uso da API

#### Criar Snapshot

```javascript
fetch('/app/server/inflation/snapshot/create/', {
    method: 'POST',
    body: formData,
    headers: {
        'X-CSRFToken': csrfToken
    }
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Snapshot criado:', data.snapshot_id);
    }
});
```

---

## Troubleshooting

### Problema: Dados aparecem como 0

**Possíveis Causas:**
1. Banco de dados do Lineage não está conectado
2. Não há itens nas localizações consultadas
3. Queries retornando dados vazios

**Solução:**
1. Verifique se `LINEAGE_DB_ENABLED=true` no `.env`
2. Verifique as credenciais do banco
3. Teste a conexão manualmente
4. Verifique se há dados nas tabelas `items` e `characters`

### Problema: Erro "Table 'item_templates' doesn't exist"

**Causa:** A tabela `item_templates` não existe no banco de dados.

**Solução:** O sistema foi atualizado para não depender dessa tabela. Os itens aparecerão como "Item {ID}" quando não houver nome disponível.

### Problema: Snapshot não pode ser criado

**Possíveis Causas:**
1. Já existe snapshot para hoje
2. Erro na query do banco
3. Timeout na execução

**Solução:**
1. Delete o snapshot existente ou aguarde até amanhã
2. Verifique os logs do servidor
3. Verifique se o banco está acessível

### Problema: Queries lentas

**Causa:** Servidor muito grande com muitos itens.

**Solução:**
1. As queries usam cache (60 segundos)
2. Considere criar snapshots em horários de menor uso
3. Otimize o banco de dados do Lineage 2

---

## Boas Práticas

### 1. Criação Regular de Snapshots

- Crie snapshots diariamente para ter histórico completo
- Crie snapshots após eventos importantes (eventos, updates, etc.)
- Mantenha snapshots antigos para comparações de longo prazo

### 2. Organização por Categorias

- Crie categorias lógicas (Armas, Armaduras, etc.)
- Agrupe itens relacionados
- Use cores diferentes para fácil identificação

### 3. Análise de Dados

- Compare snapshots semanais para identificar tendências
- Monitore itens específicos que são críticos para a economia
- Identifique padrões de consumo e drop

### 4. Manutenção

- Delete snapshots muito antigos se necessário
- Revise categorias periodicamente
- Monitore o desempenho das queries

---

## Integração com Outros Sistemas

### CustomItem

O sistema integra com `CustomItem` para obter nomes e ícones dos itens:

```python
from apps.lineage.inventory.models import CustomItem

# Busca nome do item
custom_item = CustomItem.objects.get(item_id=57)
item_name = custom_item.nome
```

### itens.json

Se `CustomItem` não existir, o sistema tenta buscar em `utils/data/itens.json`:

```json
{
    "57": ["Adena"],
    "1": ["Espada de Madeira"],
    ...
}
```

### Template Tags

O sistema usa o template tag `item_image_url` para exibir ícones:

```django
{% load itens_extras %}
<img src="{% item_image_url item.item_id %}" alt="{{ item.item_name }}">
```

---

## Exemplos de Uso

### Exemplo 1: Monitorar Inflação de Adena

1. Crie snapshots diários
2. Compare snapshots semanais
3. Identifique variações anômalas
4. Analise onde a Adena está sendo armazenada

### Exemplo 2: Analisar Drop de Itens Raros

1. Crie categoria "Itens Raros"
2. Adicione IDs dos itens raros
3. Monitore quantidade ao longo do tempo
4. Compare antes/depois de eventos

### Exemplo 3: Verificar Distribuição de Itens

1. Acesse detalhes do snapshot
2. Veja resumo por localização
3. Identifique se itens estão concentrados
4. Analise distribuição entre jogadores

---

## Limitações e Considerações

### Limitações

1. **Performance:** Queries podem ser lentas em servidores muito grandes
2. **Cache:** Dados são cacheados por 60 segundos
3. **Snapshots:** Apenas um snapshot por dia
4. **Dependências:** Requer banco de dados do Lineage 2 acessível

### Considerações

1. **Privacidade:** Dados são acessíveis apenas para staff
2. **Precisão:** Dados são calculados em tempo real, podem variar
3. **Armazenamento:** Snapshots ocupam espaço no banco Django
4. **Manutenção:** Considere limpar snapshots antigos periodicamente

---

## Changelog

### Versão 1.0.0 (2025-11-19)

- Implementação inicial do sistema
- Suporte a múltiplos schemas de banco
- Dashboard com estatísticas em tempo real
- Sistema de snapshots
- Comparação de snapshots
- Gerenciamento de categorias
- Integração com CustomItem e itens.json
- Visualização com ícones e nomes dos itens
- Modal de ajuda explicativo

---

## Suporte

Para dúvidas ou problemas:

1. Consulte esta documentação
2. Use o modal de ajuda no painel (`/app/server/inflation/`)
3. Verifique os logs do servidor
4. Entre em contato com o desenvolvedor

---

## Referências

- [Documentação de Integração do Servidor Lineage](LINEAGE_SERVER_INTEGRATION.md)
- [Sistema de Inventário](README_INVENTORY.md)
- [Modelos Django - Server](apps/lineage/server/models.py)
- [Queries - Server](apps/lineage/server/querys/)

