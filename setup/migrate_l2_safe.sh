#!/bin/bash

# Script de migração segura L2 → L2JPremium
# Autor: Sistema L2JPremium
# Versão: 1.0

set -e  # Para em caso de erro

# Detect Ubuntu version for docker-compose
UBUNTU_VERSION=$(lsb_release -cs 2>/dev/null || echo "unknown")
if [ "$UBUNTU_VERSION" = "focal" ]; then
  DOCKER_COMPOSE="docker-compose"
else
  DOCKER_COMPOSE="docker compose"
fi

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verifica se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Execute este script no diretório raiz do projeto (onde está o docker-compose.yml)"
    exit 1
fi

# Verifica se o .env existe
if [ ! -f ".env" ]; then
    log_error "Arquivo .env não encontrado. Configure as variáveis de ambiente primeiro."
    exit 1
fi

# Verifica se o banco L2 está habilitado
if ! grep -q "LINEAGE_DB_ENABLED=true" .env; then
    log_warning "LINEAGE_DB_ENABLED não está definido como true no .env"
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verifica se os containers estão rodando
log_info "Verificando se os containers estão rodando..."
if ! $DOCKER_COMPOSE ps | grep -q "site.*Up"; then
    log_error "Container 'site' não está rodando. Execute './build.sh' primeiro."
    exit 1
fi

echo "============================================================"
echo "🔄 MIGRAÇÃO SEGURA L2 → L2JPremium"
echo "============================================================"

# 1. Backup do banco L2JPremium
log_info "Criando backup do banco L2JPremium.."
BACKUP_FILE="backup_l2jpremium_$(date +%Y%m%d_%H%M%S).json"
$DOCKER_COMPOSE exec site python3 manage.py dumpdata > "$BACKUP_FILE"
log_success "Backup criado: $BACKUP_FILE"

# 2. Teste de conexão com L2
log_info "Testando conexão com banco L2..."
if $DOCKER_COMPOSE exec site python3 manage.py migrate_l2_accounts --dry-run --batch-size 1 > /dev/null 2>&1; then
    log_success "Conexão com L2 OK"
else
    log_error "Falha na conexão com L2. Verifique as configurações."
    exit 1
fi

# 3. Execução do teste
log_info "Executando teste de migração..."
$DOCKER_COMPOSE exec site python3 manage.py migrate_l2_accounts --dry-run

# 4. Confirmação do usuário
echo
log_warning "ATENÇÃO: Você está prestes a executar a migração real!"
echo "Isso irá criar usuários no L2JPremium baseados nas contas do L2."
echo
read -p "Continuar com a migração real? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Executando migração real..."
    $DOCKER_COMPOSE exec site python3 manage.py migrate_l2_accounts
    log_success "Migração concluída!"
    
    echo
    echo "============================================================"
    echo "📝 PRÓXIMOS PASSOS RECOMENDADOS:"
    echo "============================================================"
    echo "1. Verifique o relatório de migração acima"
    echo "2. Considere enviar emails informativos aos usuários"
    echo "3. Monitore os primeiros acessos"
    echo "4. Configure notificações para contas criadas"
    echo "5. Backup salvo em: $BACKUP_FILE"
    echo "============================================================"
else
    log_warning "Migração cancelada pelo usuário"
    echo
    echo "O backup foi mantido: $BACKUP_FILE"
    echo "Você pode executar a migração manualmente com:"
    echo "$DOCKER_COMPOSE exec site python3 manage.py migrate_l2_accounts"
fi 