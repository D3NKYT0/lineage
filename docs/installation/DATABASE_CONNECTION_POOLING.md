# Gerenciamento de Conexões de Banco de Dados

## 🎯 Problema: "Too many connections"

Quando você usa múltiplos workers (Gunicorn), cada um cria seu próprio pool de conexões com o banco de dados. Isso pode rapidamente exceder o limite de conexões do MySQL.

### Exemplo do Problema:
```
Workers: 9 (em servidor de 4 CPUs)
Conexões por worker: 15 (padrão SQLAlchemy)
Total: 9 × 15 = 135 conexões! ❌
```

---

## ✅ Soluções (da mais simples para mais avançada)

### **Opção 1: Reduzir Workers do Gunicorn** ⭐ RECOMENDADO

A forma mais simples e eficaz é usar menos workers.

**Antes:**
```python
workers = cpu_count * 2 + 1  # 4 CPUs = 9 workers
```

**Depois:**
```python
workers = 4  # Fixo, configurável via .env
```

**Configuração no `.env`:**
```bash
GUNICORN_WORKERS=4
LINEAGE_DB_POOL_SIZE=1
LINEAGE_DB_MAX_OVERFLOW=2
```

**Cálculo de conexões:**
```
4 workers × 3 conexões = 12 conexões totais ✅
```

#### **Quantos workers eu preciso?**

| Tipo de Servidor | CPUs | Workers Recomendados | Conexões (pool 1+2) |
|------------------|------|---------------------|---------------------|
| Pequeno          | 2    | 2-3                 | 6-9                |
| Médio            | 4    | 3-4                 | 9-12               |
| Grande           | 8    | 4-6                 | 12-18              |
| Muito Grande     | 16+  | 6-8                 | 18-24              |

**Nota:** Mais workers ≠ melhor performance. O Django é I/O bound, não CPU bound.

---

### **Opção 2: Connection Pooler Externo** (Para alta escala)

Use um middleware de pooling entre sua aplicação e o MySQL.

#### **2.1 ProxySQL** (Recomendado para MySQL)

ProxySQL gerencia um pool centralizado de conexões.

**Arquitetura:**
```
[Workers] → [ProxySQL] → [MySQL]
  (100 conexões)  (10 conexões reais)
```

**Docker Compose exemplo:**
```yaml
services:
  proxysql:
    image: proxysql/proxysql:latest
    ports:
      - "6033:6033"
    volumes:
      - ./proxysql.cnf:/etc/proxysql.cnf
    environment:
      - MYSQL_HOST=seu-mysql-host
      - MYSQL_PORT=3306

  site_http:
    # ... sua configuração
    environment:
      - LINEAGE_DB_HOST=proxysql
      - LINEAGE_DB_PORT=6033
```

**Vantagens:**
- ✅ Query caching
- ✅ Load balancing
- ✅ Query routing
- ✅ Connection pooling centralizado

#### **2.2 MySQL Router**

Solução oficial do MySQL.

**Docker Compose exemplo:**
```yaml
services:
  mysql-router:
    image: mysql/mysql-router:latest
    environment:
      - MYSQL_HOST=seu-mysql-host
      - MYSQL_PORT=3306
    ports:
      - "6446:6446"
```

---

### **Opção 3: Usar NullPool** (NÃO RECOMENDADO)

Abre/fecha conexão a cada query. **Muito lento**, use apenas para debug.

```python
from sqlalchemy.pool import NullPool

self.engine = create_engine(
    url,
    poolclass=NullPool  # Sem pool de conexões
)
```

---

## 🔧 Configuração Recomendada Final

### **Para a maioria dos casos:**

**`.env`:**
```bash
# Gunicorn
GUNICORN_WORKERS=4

# Lineage Database
LINEAGE_DB_ENABLED=True
LINEAGE_DB_HOST=192.168.1.100
LINEAGE_DB_PORT=3306
LINEAGE_DB_NAME=l2jdb
LINEAGE_DB_USER=l2user
LINEAGE_DB_PASSWORD=suaSenhaAqui
LINEAGE_DB_POOL_SIZE=1
LINEAGE_DB_MAX_OVERFLOW=2
```

**Resultado:**
- 4 workers × 3 conexões = **12 conexões totais**
- Bem abaixo do limite MySQL (~151)
- Performance adequada para 90% dos casos
- Com pool_use_lifo=True, reutiliza conexões mais recentes primeiro

---

## 📊 Monitoramento de Conexões

### **Ver conexões ativas no MySQL:**

```sql
-- Total de conexões
SHOW STATUS LIKE 'Threads_connected';

-- Limite de conexões
SHOW VARIABLES LIKE 'max_connections';

-- Conexões por usuário
SELECT user, COUNT(*) 
FROM information_schema.processlist 
GROUP BY user;
```

### **Ver workers do Gunicorn:**

```bash
# Dentro do container
docker exec -it site_http ps aux | grep gunicorn

# Total de workers
docker exec -it site_http ps aux | grep gunicorn | grep -v grep | wc -l
```

---

## 🚨 Troubleshooting

### **Ainda recebendo "Too many connections"?**

1. **Verifique quantos workers estão rodando:**
   ```bash
   ps aux | grep gunicorn | wc -l
   ```

2. **Verifique o pool size atual:**
   - Cada worker usa `POOL_SIZE + MAX_OVERFLOW` conexões
   - Total = workers × (pool_size + max_overflow)

3. **Aumente o limite do MySQL (temporário):**
   ```sql
   SET GLOBAL max_connections = 200;
   ```
   
   No `my.cnf`:
   ```ini
   [mysqld]
   max_connections = 200
   ```

4. **Use ProxySQL** se tiver muitos serviços conectando ao mesmo MySQL

---

## 💡 Melhores Práticas

✅ **FAÇA:**
- Use 2-6 workers para a maioria dos casos
- Configure pool_size baixo (2-3) se tiver muitos workers
- Use ProxySQL se tiver múltiplos serviços
- Monitor conexões regularmente

❌ **NÃO FAÇA:**
- Não use workers = cpu_count * 2 + 1 (muito agressivo)
- Não configure pool_size muito alto com muitos workers
- Não use NullPool em produção (performance ruim)
- Não ignore warnings de conexão

---

## 📚 Referências

- [Gunicorn Workers](https://docs.gunicorn.org/en/stable/design.html#how-many-workers)
- [SQLAlchemy Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [ProxySQL Documentation](https://proxysql.com/documentation/)
- [MySQL max_connections](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_max_connections)

