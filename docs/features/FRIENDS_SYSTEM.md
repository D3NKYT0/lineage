# Documentação Técnica: Sistema de Amigos

> **Última atualização:** 21/02/2026

## Problema Original no Endpoint
A estruturação legada do subsistema de amigos (`/app/message/friends-list/`) sofria de deficiências no carregamento em massa (problemas `N+1`) e falta de filtros adequados para bases com altas quantidades de usuários relacionais (N:N).

## Arquitetura Otimizada do Subsistema

O subsistema atual de amigos do PDL foi otimizado atuando em quatro frentes estruturais: Consultas Assíncronas, Paginação, Cache Distribuído Direcional e Querysets Aninhadas (`select_related`). 

### 1. Sistema de Paginação Robusto
Todas as listagens, sejam usuários disponíveis ou o círculo de amizade já consolidado, processam lotes restritos de requisição paginadas nativamente pela classe `Paginator` do Django. O offset padrão atua na restrição de lotes (geralmente `30` ou o parâmetro configurado).

### 2. Filtros Instantâneos e Live Search (AJAX)
A view engloba o controle robusto do `Q` expression list no motor de banco para checagem flexível de propriedades que incluem nomes, pseudônimos, e strings truncadas. Adicionalmente, requests silenciosas feitas pelo JavaScript interagem com APIs exclusivas (`api/search-users/`) retornando listas de autocomparecimento antes do enter na barra de inputs.

### 3. Melhoria no ORM (`select_related`)
Dramas estruturais do framework, o lazy fetch de ORM nas tags de template, foram eliminados agrupando a requisição `JOIN` no Python Server via prefetch.
- Requests unificam as chaves do remetente e destinatário num passe rápido:
```python
accepted_friendships = Friendship.objects.filter(
    user=request.user, 
    accepted=True
).select_related('friend')
```

### 4. Cache Exclusivo
Requisições inteiras da interface relacional são armazenadas nos motores de memcache da máquina (ex: Redis). `views` em blocos estáticos carregam `@cache_page(60 * 5)` limitando as hits exclusivas de visualização para queries já repetidas sob o request scope (`vary_on_cookie`), isolando o cachê por identidade de sessão.

## 📊 View de Agregação Auxiliar

Existe a view utilitária `get_friends_stats` para consumo assíncrono. Sua finalidade é recalcular o counter de status das notificações nos Badges Laterais e Headbars do template a todo instante (`friends_count`, `pending`, `sent`) minimizando overhead no carregamento HTML.

Esta engenharia eleva a confiabilidade da lista e permite escala robusta mesmo em bases povoadas com múltiplos requests de amizade complexos.

---

[ Voltar ao Índice](../INDEX.md)

