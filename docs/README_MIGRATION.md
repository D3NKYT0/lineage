# 🚀 Migração L2 → L2JPremium - Guia Rápido

## O que foi criado

✅ **Comando de migração**: `core/management/commands/migrate_l2_accounts.py`  
✅ **Documentação completa**: `docs/MIGRATION_L2_TO_PDL.md`  
✅ **Script seguro**: `setup/migrate_l2_safe.sh`  
✅ **Script de teste**: `test/test_migration.py`  

## Como usar (Rápido)

### 1. Configurar conexão L2
```bash
# No arquivo .env
LINEAGE_DB_ENABLED=true
LINEAGE_DB_NAME=l2jdb
LINEAGE_DB_USER=l2user
LINEAGE_DB_PASSWORD=suaSenhaAqui
LINEAGE_DB_HOST=192.168.1.100
LINEAGE_DB_PORT=3306
LINEAGE_QUERY_MODULE=dreamv3
```

### 2. Testar primeiro
```bash
docker-compose exec site python3 manage.py migrate_l2_accounts --dry-run
```

### 3. Executar migração
```bash
# Opção 1: Comando direto (dentro do container)
docker-compose exec site python3 manage.py migrate_l2_accounts

# Opção 2: Script seguro (recomendado)
chmod +x setup/migrate_l2_safe.sh
./setup/migrate_l2_safe.sh
```

## Regras implementadas

✅ **Contas com mesmo email**: Adiciona prefixo `L2_`  
✅ **Contas com email nulo**: Desconsideradas automaticamente  
✅ **Senhas aleatórias**: 64 caracteres por padrão  
✅ **Sem vinculação**: Contas não são linkadas (usuário deve confirmar)  

## Exemplos de uso

```bash
# Teste básico
docker-compose exec site python3 manage.py migrate_l2_accounts --dry-run

# Com prefixo customizado
docker-compose exec site python3 manage.py migrate_l2_accounts --prefix "MIGRATED_" --dry-run

# Com senhas mais curtas
docker-compose exec site python3 manage.py migrate_l2_accounts --password-length 32

# Em lotes menores
docker-compose exec site python3 manage.py migrate_l2_accounts --batch-size 50
```

## Saída esperada

```
🚀 Iniciando migração de contas L2 → L2JPremium
📋 Buscando contas do L2...
✅ Encontradas 1500 contas no L2
📦 Processando lote 1/15
✅ Criado: player1 → player1@email.com
✅ Criado: player2 → L2_player2@email.com
⚠️  Username player3 já existe no L2JPremium - pulando

============================================================
📊 RELATÓRIO DE MIGRAÇÃO
============================================================
Total de contas processadas: 1500
Usuários criados: 1450
Pulados: 45
Erros: 5
Conflitos de email resolvidos: 23
```

## Próximos passos

1. **Teste primeiro** com `--dry-run`
2. **Execute a migração** real
3. **Verifique o relatório** de migração
4. **Notifique os usuários** sobre as contas criadas
5. **Monitore** os primeiros acessos

## Troubleshooting

### Erro de conexão L2
```bash
❌ Não foi possível conectar ao banco do L2
```
**Solução**: Verificar configurações no `.env`

### Nenhuma conta encontrada
```bash
⚠️  Nenhuma conta encontrada no L2
```
**Solução**: Verificar se há contas com email válido no L2

### Módulo não encontrado
```bash
Erro ao buscar contas do L2: ModuleNotFoundError
```
**Solução**: Verificar `LINEAGE_QUERY_MODULE` no `.env`

## Documentação completa

📖 Veja `docs/MIGRATION_L2_TO_PDL.md` para documentação detalhada.

## Teste do comando

```bash
# Teste local (se tiver ambiente Python configurado)
python test/test_migration.py

# Ou execute diretamente o comando no container
docker-compose exec site python3 manage.py migrate_l2_accounts --help
```

---

**⚠️ IMPORTANTE**: Sempre faça backup antes da migração! 