#!/bin/bash

# Configurações
CONTAINER_NAME="postgres"
DB_NAME="lineage_db"
DB_USER="lineage_user"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%F_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"
MAX_BACKUPS=7

# Cria a pasta de backup se não existir
mkdir -p $BACKUP_DIR

# Faz o backup e comprime com gzip
docker exec -t $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Verifica se o backup foi bem-sucedido
if [ $? -eq 0 ]; then
  echo "✅ Backup realizado com sucesso: $BACKUP_FILE"
else
  echo "❌ Erro ao realizar o backup."
  exit 1
fi

# Remove backups antigos, mantendo apenas os mais recentes
BACKUP_COUNT=$(ls -1 $BACKUP_DIR/backup_*.sql.gz | wc -l)

if [ $BACKUP_COUNT -gt $MAX_BACKUPS ]; then
  REMOVE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
  echo "🧹 Removendo $REMOVE_COUNT backup(s) antigo(s)..."
  ls -1t $BACKUP_DIR/backup_*.sql.gz | tail -n $REMOVE_COUNT | xargs rm -f
fi
