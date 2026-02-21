# Migração de Contas L2 → PDL

> **Última atualização:** 21/02/2026

Este documento descreve como migrar contas do banco de dados do Lineage 2 para o PDL (Painel de Controle).

## Visão Geral

O comando `migrate_l2_accounts` permite migrar contas do servidor L2 para o PDL seguindo regras específicas de segurança e validação.

## Regras de Migração

1. **Contas com mesmo email**: Adiciona prefixo configurável (padrão: `L2_`)
2. **Contas com email nulo**: São desconsideradas automaticamente
3. **Senhas aleatórias**: Gera senhas de 64 caracteres por padrão
4. **Sem vinculação**: As contas não são vinculadas (usuários devem confirmar com senha do L2)

## Pré-requisitos

1. **Conexão com banco L2 configurada**:
   ```env
   LINEAGE_DB_ENABLED=true
   LINEAGE_DB_NAME=l2jdb
   LINEAGE_DB_USER=l2user
   LINEAGE_DB_PASSWORD=suaSenhaAqui
   LINEAGE_DB_HOST=192.168.1.100
   LINEAGE_DB_PORT=3306
   LINEAGE_QUERY_MODULE=dreamv3  # ou outro módulo compatível
   ```

2. **Banco PDL configurado e migrações aplicadas**

## Uso do Comando

### Modo de Teste (Recomendado primeiro)

```bash
docker compose exec site_http python3 manage.py migrate_l2_accounts --dry-run
```

Este comando mostra o que seria feito sem criar usuários.

### Execução Real

```bash
docker compose exec site_http python3 manage.py migrate_l2_accounts
```

### Opções Disponíveis

```bash
docker compose exec site_http python3 manage.py migrate_l2_accounts \
    --dry-run \              # Modo de teste
    --prefix "L2_" \         # Prefixo para emails duplicados
    --password-length 64 \   # Comprimento da senha
    --batch-size 100         # Tamanho do lote
```

## Exemplos de Uso

### 1. Teste com configuração personalizada

```bash
docker compose exec site_http python3 manage.py migrate_l2_accounts \
    --dry-run \
    --prefix "MIGRATED_" \
    --password-length 32 \
    --batch-size 50
```

### 2. Migração completa

```bash
docker compose exec site_http python3 manage.py migrate_l2_accounts \
    --prefix "L2_" \
    --batch-size 200
```

### 3. Migração com senhas mais curtas

```bash
docker compose exec site_http python3 manage.py migrate_l2_accounts \
    --password-length 16
```

## Saída do Comando

### Durante a Execução

```
🚀 Iniciando migração de contas L2 → PDL
📋 Buscando contas do L2...
✅ Encontradas 1500 contas no L2
📦 Processando lote 1/15
✅ Criado: player1 → player1@email.com
✅ Criado: player2 → L2_player2@email.com
⚠️  Username player3 já existe no PDL - pulando
🔑 Senha para admin1: K9#mP$2vL@qR7nX...
```

### Relatório Final

```
============================================================
📊 RELATÓRIO DE MIGRAÇÃO
============================================================
Total de contas processadas: 1500
Usuários criados: 1450
Pulados: 45
Erros: 5
Conflitos de email resolvidos: 23

✅ Migração concluída!

📝 PRÓXIMOS PASSOS:
1. Os usuários precisam definir suas próprias senhas
2. Eles devem usar a senha do L2 para confirmar a veracidade da conta
3. As contas não estão vinculadas (conforme solicitado)
4. Considere enviar emails informativos aos usuários
```

## Tratamento de Conflitos

### Emails Duplicados

- **Primeira ocorrência**: Usa o email original
- **Duplicatas**: Adiciona prefixo (ex: `L2_` + email original)
- **Múltiplas duplicatas**: Pula a conta se o email com prefixo também existir

### Usernames Duplicados

- Se o username já existe no PDL, a conta é pulada
- Recomenda-se verificar manualmente essas contas

### Níveis de Acesso

- **access_level = 0**: Usuário normal
- **access_level > 0**: Staff (is_staff = True)
- **access_level >= 100**: Superusuário (is_superuser = True)

## Segurança

### Senhas Geradas

- Senhas aleatórias de 64 caracteres por padrão
- Incluem letras, números e símbolos
- Caracteres problemáticos são removidos automaticamente
- Senhas de administradores são exibidas no log

### Validações

- Apenas contas com email válido são processadas
- Emails nulos, vazios ou "NULL" são ignorados
- Transações garantem consistência dos dados

## Pós-Migração

### Para os Usuários

1. **Primeiro acesso**: Usar username e senha gerada
2. **Alteração de senha**: Obrigatória no primeiro login
3. **Verificação de conta**: Usar senha do L2 para confirmar propriedade

### Para Administradores

1. **Verificar logs**: Revisar relatório de migração
2. **Contas puladas**: Investigar manualmente se necessário
3. **Notificação**: Considerar enviar emails informativos
4. **Monitoramento**: Acompanhar primeiros acessos

## Troubleshooting

### Erro de Conexão com L2

```
❌ Não foi possível conectar ao banco do L2
```

**Soluções:**
- Verificar configurações do banco no `.env`
- Confirmar se o servidor L2 está acessível
- Verificar credenciais de acesso

### Erro de Módulo de Query

```
Erro ao buscar contas do L2: ModuleNotFoundError
```

**Soluções:**
- Verificar `LINEAGE_QUERY_MODULE` no `.env`
- Confirmar se o módulo existe em `apps/lineage/server/querys/`

### Contas Não Encontradas

```
⚠️  Nenhuma conta encontrada no L2
```

**Possíveis causas:**
- Banco L2 vazio
- Todas as contas têm email nulo
- Problema na query SQL

## Logs e Auditoria

O comando gera logs detalhados incluindo:

- Contas processadas com sucesso
- Contas puladas e motivos
- Erros encontrados
- Estatísticas finais
- Senhas de administradores

## Backup Recomendado

**IMPORTANTE**: Sempre faça backup antes da migração:

```bash
# Backup do banco PDL
docker compose exec site_http python3 manage.py dumpdata > backup_pdl_$(date +%Y%m%d_%H%M%S).json

# Backup do banco L2 (se possível)
mysqldump -h 192.168.1.100 -u l2user -p l2jdb > backup_l2_$(date +%Y%m%d_%H%M%S).sql
```

## Script de Execução Segura

```bash
#!/bin/bash
# migrate_l2_safe.sh

echo "🔄 Iniciando migração segura L2 → PDL"

# 1. Backup
echo "💾 Criando backup..."
docker compose exec site_http python3 manage.py dumpdata > backup_pdl_$(date +%Y%m%d_%H%M%S).json

# 2. Teste
echo "🧪 Executando teste..."
docker compose exec site_http python3 manage.py migrate_l2_accounts --dry-run

# 3. Confirmação
read -p "Continuar com a migração real? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Executando migração..."
    docker compose exec site_http python3 manage.py migrate_l2_accounts
else
    echo "❌ Migração cancelada"
fi
```

Execute com: `chmod +x migrate_l2_safe.sh && ./migrate_l2_safe.sh` 
---

[ Voltar ao Índice](../INDEX.md)

