# Documentação do apps.lineage.server

> **Última atualização:** 21/02/2026

## Visão Geral

O app `apps.lineage.server` é responsável pela integração do Django com o banco de dados do servidor Lineage 2 (L2), permitindo que a aplicação web acesse, consulte e manipule dados do jogo em tempo real, sem misturar dados do Django com os dados do L2.

---

## Estrutura do App

- **models.py:** Modelos Django para configurações, preços de serviços, apoiadores, etc. (dados do site, não do L2)
- **database.py:** Classe `LineageDB` para conectar e operar no banco L2 (MySQL) via SQLAlchemy
- **querys/:** Arquivos com consultas SQL e classes utilitárias para acessar dados L2 (personagens, clãs, rankings, etc.)
- **views/:** Endpoints Django que expõem dados L2 ao frontend ou APIs
- **utils/:** Utilitários, cache, etc.
- **generate_query/:** Módulo de geração dinâmica de queries (adaptável a diferentes versões L2)

---

## O Banco de Dados L2

O banco L2 é um banco MySQL separado, com tabelas como `characters`, `accounts`, `clan_data`, `castle`, etc. Não é gerenciado pelo ORM do Django; o acesso é feito via SQL bruto.

- **Conexão:** Feita via SQLAlchemy, usando variáveis de ambiente para host, usuário, senha, etc.
- **Classe principal:** `LineageDB` (singleton, thread-safe)
- **Operações:** select, insert, update, delete, execute_raw, com cache opcional
- **Exemplo de uso:**
  ```python
  from apps.lineage.server.database import LineageDB
  result = LineageDB().select("SELECT * FROM characters WHERE char_name = :name", {"name": "Hero"})
  ```

---

## Relação Django x Banco L2

- **ORM Django:** Usado apenas para dados do site (usuários, configurações, compras, etc.)
- **Banco L2:** Acessado via SQL bruto, sem modelos Django, para garantir performance e compatibilidade com o servidor do jogo
- **Integração:** Funções utilitárias e endpoints Django usam `LineageDB` para buscar dados L2 e exibir no site (rankings, status de castelos, personagens online, etc.)
- **Exemplo de endpoint:**
  ```python
  # views/server_views.py
  @endpoint_enabled('top_level')
  @safe_json_response
  def top_level(request):
      limit = int(request.GET.get("limit", 10))
      return LineageStats.top_level(limit=limit)
  ```
  Aqui, `LineageStats.top_level` executa uma consulta SQL no banco L2 e retorna o ranking de personagens por nível.

---

## Exemplo de Fluxo

1. Usuário acessa uma página de ranking no site
2. Django chama uma função utilitária (ex: `LineageStats.top_level`) que executa a consulta SQL no banco L2 via `LineageDB`
3. O resultado é retornado e exibido no frontend

---

## Vantagens desta Abordagem
- **Isolamento:** Dados do jogo e do site permanecem separados, evitando conflitos e facilitando manutenção
- **Performance:** Consultas otimizadas executadas diretamente no banco L2
- **Flexibilidade:** Possível adaptar a diferentes versões de banco L2 (acis, essence, lucera, etc.) alterando apenas as queries

---

## Notas
- O acesso ao banco L2 pode ser desabilitado via variável de ambiente (`LINEAGE_DB_ENABLED`)
- Cache interno reduz carga em consultas repetidas
- Alterações no banco L2 devem ser feitas com cuidado para não afetar o servidor do jogo

---

[ Voltar ao Índice](../INDEX.md)

