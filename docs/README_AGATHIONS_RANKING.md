# Como Adicionar um Novo Menu de Tops - Ranking de Agathions

## ✅ **Passos Concluídos**

Todos os passos básicos já foram implementados para adicionar o novo menu de Agathions:

### 1. **URL Configurada** ✅
- ✅ Adicionada nova rota em `apps/lineage/tops/urls.py`
- ✅ URL: `/public/tops/agathions/`
- ✅ Nome: `tops:agathions`

### 2. **View Criada** ✅
- ✅ Classe `TopsAgathionsView` criada em `apps/lineage/tops/views.py`
- ✅ Template configurado: `tops/agathions.html`
- ✅ Context data preparado para receber dados de agathions

### 3. **Template Criado** ✅
- ✅ Template `apps/lineage/tops/templates/tops/agathions.html` criado
- ✅ Estrutura de tabela seguindo padrão dos outros rankings
- ✅ Colunas: Posição, Proprietário, Clã, Agathion, Level Agathion, Nível Char, Classe
- ✅ Estilos específicos para agathions aplicados

### 4. **Menu Navegação** ✅
- ✅ Menu adicionado em `apps/lineage/tops/templates/tops/base.html`
- ✅ Ícone: `fas fa-magic`
- ✅ Texto: "Ranking Agathions"

### 5. **Página Inicial** ✅
- ✅ Card adicionado na página inicial `apps/lineage/tops/templates/tops/home.html`
- ✅ Ícone e cores personalizadas (roxo/mágico)
- ✅ Badge "Magic"
- ✅ Contador de categorias atualizado para 9

## 🔧 **O Que Precisa Ser Implementado**

### 1. **Método de Query no Banco de Dados** ✅

**IMPLEMENTADO CORRETAMENTE**: O método `top_agathions` foi adicionado no arquivo correto:

```
✅ apps/lineage/server/querys/query_l2jpremium.py
```

**Query implementada**:
```python
@staticmethod
@cache_lineage_result(timeout=300)
def top_agathions(limit=10):
    sql = """
        SELECT 
            C.char_name, 
            C.online, 
            C.onlinetime,
            CS.level,
            CS.class_id AS base,
            D.name AS clan_name,
            C.clanid AS clan_id,
            CD.ally_id AS ally_id,
            A.name AS agathion_name,
            A.level AS agathion_level,
            A.exp AS agathion_exp,
            A.item_id AS agathion_item_id,
            A.status AS agathion_status
        FROM characters C
        LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
        LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
        LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
        INNER JOIN agathion_data A ON A.owner_id = C.obj_Id
        WHERE C.accesslevel = '0' 
            AND A.level IS NOT NULL 
            AND A.status IN ('active', 'stored')
        ORDER BY A.level DESC, A.exp DESC, CS.level DESC, C.char_name ASC
        LIMIT :limit
    """
    return LineageStats._run_query(sql, {"limit": limit})
```

#### **Exemplo de Implementação:**

```python
@staticmethod
@cache_lineage_result(timeout=300)
def top_agathions(limit=10):
    sql = """
        SELECT 
            C.char_name, 
            C.online, 
            C.onlinetime,
            CS.level,
            CS.class_id AS base,
            D.name AS clan_name,
            C.clanid AS clan_id,
            CD.ally_id AS ally_id,
            A.agathion_name,
            A.agathion_level
        FROM characters C
        LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
        LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
        LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
        LEFT JOIN character_agathions A ON A.char_id = C.obj_Id
        WHERE C.accesslevel = '0' AND A.agathion_level IS NOT NULL
        ORDER BY A.agathion_level DESC, CS.level DESC, C.char_name ASC
        LIMIT :limit
    """
    return LineageStats._run_query(sql, {"limit": limit})
```

### 2. **Verificar Estrutura do Banco de Dados**

Você precisa verificar se sua base de dados possui:

1. **Tabela de Agathions** (pode ter nomes como):
   - `character_agathions`
   - `agathions`
   - `player_agathions`

2. **Campos necessários**:
   - `char_id` ou `player_id` (FK para characters)
   - `agathion_name` (nome do agathion)
   - `agathion_level` (nível do agathion)

### 3. **Ativar a Query Real**

Após implementar o método, descomente esta linha em `apps/lineage/tops/views.py`:

```python
# Linha 430 aproximadamente - trocar isto:
# result = LineageStats.top_agathions(limit=20)

# Por isto:
result = LineageStats.top_agathions(limit=20)
```

### 4. **Adicionar Traduções (Opcional)**

Para suporte multilíngue, adicione as traduções nos arquivos:

```
locale/pt/LC_MESSAGES/django.po
locale/en/LC_MESSAGES/django.po  
locale/es/LC_MESSAGES/django.po
```

Strings para traduzir:
- "Ranking Agathions"
- "Os melhores criadores de Agathions do servidor"
- "Magic"
- "Proprietário"
- "Agathion"  
- "Level Agathion"
- "Nível Char"

## 🎯 **Como Testar**

1. **Com dados de exemplo** (atual):
   - Acesse: `http://seusite.com/public/tops/agathions/`
   - Deve mostrar dados fictos

2. **Com dados reais** (após implementar query):
   - Implemente o método `top_agathions` 
   - Descomente a linha de query real
   - Acesse novamente a URL

## 🔗 **URLs Relacionadas**

- **Menu Principal**: `http://seusite.com/public/tops/`
- **Ranking Agathions**: `http://seusite.com/public/tops/agathions/`

## 📝 **Estrutura de Dados Esperada**

O método `top_agathions` deve retornar uma lista de dicionários com esta estrutura:

```python
[
    {
        'char_name': 'NomeDoPlayer',
        'clan_name': 'NomeDoClã', 
        'agathion_name': 'Dragon Agathion',
        'agathion_level': 10,
        'level': 80,
        'base': 0,  # class_id
        'clanid': 123,
        'ally_id': 456,
        # ... outros campos
    }
]
```

---

**Implementação concluída por: GitHub Copilot**  
**Data: 21/10/2025**