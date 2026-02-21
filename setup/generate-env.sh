#!/bin/bash

################################################################################
# Script de Geração do Arquivo .env - Painel Definitivo Lineage (PDL)
# 
# Este script gera o arquivo .env de forma interativa, permitindo escolher
# quais categorias opcionais incluir.
#
# Uso:
#   bash setup/generate-env.sh
################################################################################

set -euo pipefail

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Função para log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Função para criar backup do .env antes de modificações (com numeração incremental)
backup_env_file() {
    local env_file="${1:-$ENV_FILE}"
    
    if [ ! -f "$env_file" ]; then
        return 0  # Se o arquivo não existe, não precisa fazer backup
    fi
    
    # Encontrar o próximo número de backup disponível
    local backup_num=1
    local backup_file="${env_file}.bkp"
    
    while [ -f "$backup_file" ]; do
        backup_num=$((backup_num + 1))
        backup_file="${env_file}.bkp${backup_num}"
    done
    
    # Criar o backup
    cp "$env_file" "$backup_file" 2>/dev/null || {
        log_error "Falha ao criar backup do .env em $backup_file"
        return 1
    }
    
    log_success "Backup do .env criado: $backup_file"
    return 0
}

# Diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Se estamos dentro de um diretório lineage, ajustar
if [ -d "${PROJECT_DIR}/lineage" ] && [ -f "${PROJECT_DIR}/lineage/manage.py" ]; then
    PROJECT_DIR="${PROJECT_DIR}/lineage"
fi

ENV_FILE="${PROJECT_DIR}/.env"

# Função para gerar chave Fernet
generate_fernet_key() {
    python3 - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
}

# Função para gerar SECRET_KEY
generate_secret_key() {
    python3 - <<EOF
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
EOF
}

# Função para perguntar sim/não
ask_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local answer
    
    if [ "$default" = "y" ]; then
        prompt="${prompt} (S/n): "
    else
        prompt="${prompt} (s/N): "
    fi
    
    read -p "$prompt" answer
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    
    if [ -z "$answer" ]; then
        answer="$default"
    fi
    
    if [[ "$answer" =~ ^[sSyY]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Função para perguntar valor
ask_value() {
    local prompt="$1"
    local default="$2"
    local value
    
    if [ -n "$default" ]; then
        read -p "$prompt [${default}]: " value
        echo "${value:-$default}"
    else
        read -p "$prompt: " value
        echo "$value"
    fi
}

# Função para ler valor existente do .env
get_existing_value() {
    local key="$1"
    local env_file="${2:-$ENV_FILE}"
    
    if [ ! -f "$env_file" ]; then
        return 1
    fi
    
    # Busca a variável no arquivo, removendo aspas e espaços (aceita espaços opcionais ao redor do =)
    local value=$(grep -E "^${key}\s*=" "$env_file" 2>/dev/null | head -1 | cut -d'=' -f2- | sed "s/^[[:space:]]*//;s/[[:space:]]*$//" | sed "s/^['\"]//;s/['\"]$//")
    
    if [ -n "$value" ]; then
        echo "$value"
        return 0
    fi
    
    return 1
}

# Função para verificar se variável existe no .env
var_exists() {
    local key="$1"
    local env_file="${2:-$ENV_FILE}"
    
    if [ ! -f "$env_file" ]; then
        return 1
    fi
    
    grep -qE "^${key}\s*=" "$env_file" 2>/dev/null
}

# Função para adicionar seção ao .env
add_section() {
    local section_name="$1"
    echo "" >> "$ENV_FILE"
    echo "# =========================== $section_name ===========================" >> "$ENV_FILE"
}

# Função para adicionar variável ao .env
add_var() {
    local key="$1"
    local value="$2"
    
    # Criar backup antes de adicionar (apenas uma vez por sessão)
    if [ -z "${_BACKUP_CREATED:-}" ]; then
        backup_env_file "$ENV_FILE"
        _BACKUP_CREATED=1
    fi
    
    echo "${key}=${value}" >> "$ENV_FILE"
}

# Função para atualizar ou adicionar variável no .env
update_var() {
    local key="$1"
    local value="$2"
    local env_file="${3:-$ENV_FILE}"
    
    # Criar backup antes de atualizar (apenas uma vez por sessão)
    if [ -z "${_BACKUP_CREATED:-}" ]; then
        backup_env_file "$env_file"
        _BACKUP_CREATED=1
    fi
    
    if var_exists "$key" "$env_file"; then
        # Atualiza variável existente (preserva a linha original se possível, aceita espaços opcionais)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS usa versão diferente do sed
            sed -i '' "s|^${key}\s*=.*|${key}=${value}|" "$env_file"
        else
            sed -i "s|^${key}\s*=.*|${key}=${value}|" "$env_file"
        fi
    else
        # Adiciona nova variável
        echo "${key}=${value}" >> "$env_file"
    fi
}

# Função para gerar variáveis obrigatórias
generate_required() {
    local edit_mode="${1:-false}"
    log_info "Gerando variáveis obrigatórias..."
    
    if [ "$edit_mode" = "false" ]; then
        add_section "REQUIRED CONFIGURATION"
    fi
    
    # DEBUG
    local existing_debug=$(get_existing_value "DEBUG" 2>/dev/null || echo "")
    local debug_default="${existing_debug:-False}"
    if [ "$edit_mode" = "true" ] && [ -n "$existing_debug" ]; then
        if ask_yes_no "Habilitar modo DEBUG? (atual: $existing_debug)" "$(echo "$existing_debug" | tr '[:upper:]' '[:lower:]')"; then
            update_var "DEBUG" "True"
        else
            update_var "DEBUG" "False"
        fi
    else
        if ask_yes_no "Habilitar modo DEBUG?" "$(echo "$debug_default" | tr '[:upper:]' '[:lower:]')"; then
            if [ "$edit_mode" = "true" ]; then
                update_var "DEBUG" "True"
            else
                add_var "DEBUG" "True"
            fi
        else
            if [ "$edit_mode" = "true" ]; then
                update_var "DEBUG" "False"
            else
                add_var "DEBUG" "False"
            fi
        fi
    fi
    
    # SECRET_KEY
    local existing_secret=$(get_existing_value "SECRET_KEY" 2>/dev/null || echo "")
    if [ -z "$existing_secret" ] || [ "$edit_mode" = "false" ]; then
        log_info "Gerando SECRET_KEY..."
        SECRET_KEY=$(generate_secret_key 2>/dev/null || echo "41&l85x\$t8g5!wgvzxw9_v%jbph2msibr3x7jww5%1u8w*3ax")
        if [ "$edit_mode" = "true" ]; then
            update_var "SECRET_KEY" "$SECRET_KEY"
        else
            add_var "SECRET_KEY" "$SECRET_KEY"
        fi
    else
        log_info "SECRET_KEY já existe, mantendo valor atual."
        if [ "$edit_mode" = "true" ]; then
            # Não atualiza, mantém o existente
            :
        fi
    fi
    
    # Database
    if [ "$edit_mode" = "false" ]; then
        add_section "DATABASE CONFIGURATION"
    fi
    local existing_db_engine=$(get_existing_value "DB_ENGINE" 2>/dev/null || echo "postgresql")
    DB_ENGINE=$(ask_value "Tipo de banco de dados (postgresql/mysql/sqlite3)" "$existing_db_engine")
    if [ "$edit_mode" = "true" ]; then
        update_var "DB_ENGINE" "$DB_ENGINE"
    else
        add_var "DB_ENGINE" "$DB_ENGINE"
    fi
    
    if [ "$DB_ENGINE" != "sqlite3" ]; then
        local existing_db_host=$(get_existing_value "DB_HOST" 2>/dev/null || echo "postgres")
        local existing_db_name=$(get_existing_value "DB_NAME" 2>/dev/null || echo "db_name")
        local existing_db_user=$(get_existing_value "DB_USERNAME" 2>/dev/null || echo "db_user")
        local existing_db_pass=$(get_existing_value "DB_PASS" 2>/dev/null || echo "db_pass")
        local existing_db_port=$(get_existing_value "DB_PORT" 2>/dev/null || echo "5432")
        
        DB_HOST=$(ask_value "Host do banco de dados" "$existing_db_host")
        DB_NAME=$(ask_value "Nome do banco de dados" "$existing_db_name")
        DB_USERNAME=$(ask_value "Usuário do banco de dados" "$existing_db_user")
        DB_PASS=$(ask_value "Senha do banco de dados" "$existing_db_pass")
        DB_PORT=$(ask_value "Porta do banco de dados" "$existing_db_port")
        
        if [ "$edit_mode" = "true" ]; then
            update_var "DB_HOST" "$DB_HOST"
            update_var "DB_NAME" "$DB_NAME"
            update_var "DB_USERNAME" "$DB_USERNAME"
            update_var "DB_PASS" "$DB_PASS"
            update_var "DB_PORT" "$DB_PORT"
        else
            add_var "DB_HOST" "$DB_HOST"
            add_var "DB_NAME" "$DB_NAME"
            add_var "DB_USERNAME" "$DB_USERNAME"
            add_var "DB_PASS" "$DB_PASS"
            add_var "DB_PORT" "$DB_PORT"
        fi
    fi
    
    # Redis e Cache
    if [ "$edit_mode" = "false" ]; then
        add_section "REDIS AND CACHE"
    fi
    local existing_cache=$(get_existing_value "DJANGO_CACHE_REDIS_URI" 2>/dev/null || echo "redis://redis:6379/0")
    local existing_broker=$(get_existing_value "CELERY_BROKER_URI" 2>/dev/null || echo "redis://redis:6379/1")
    local existing_backend=$(get_existing_value "CELERY_BACKEND_URI" 2>/dev/null || echo "redis://redis:6379/1")
    local existing_channels=$(get_existing_value "CHANNELS_BACKEND" 2>/dev/null || echo "redis://redis:6379/2")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "DJANGO_CACHE_REDIS_URI" "$existing_cache"
        update_var "CELERY_BROKER_URI" "$existing_broker"
        update_var "CELERY_BACKEND_URI" "$existing_backend"
        update_var "CHANNELS_BACKEND" "$existing_channels"
    else
        add_var "DJANGO_CACHE_REDIS_URI" "$existing_cache"
        add_var "CELERY_BROKER_URI" "$existing_broker"
        add_var "CELERY_BACKEND_URI" "$existing_backend"
        add_var "CHANNELS_BACKEND" "$existing_channels"
    fi
    
    # Auditor
    local existing_auditor=$(get_existing_value "CONFIG_AUDITOR_MIDDLEWARE_ENABLE" 2>/dev/null || echo "True")
    local auditor_default=$(echo "$existing_auditor" | tr '[:upper:]' '[:lower:]')
    if [ "$edit_mode" = "true" ] && [ -n "$existing_auditor" ]; then
        if ask_yes_no "Habilitar auditor middleware? (atual: $existing_auditor)" "$auditor_default"; then
            update_var "CONFIG_AUDITOR_MIDDLEWARE_ENABLE" "True"
        else
            update_var "CONFIG_AUDITOR_MIDDLEWARE_ENABLE" "False"
        fi
    else
        if ask_yes_no "Habilitar auditor middleware?" "$auditor_default"; then
            if [ "$edit_mode" = "true" ]; then
                update_var "CONFIG_AUDITOR_MIDDLEWARE_ENABLE" "True"
            else
                add_var "CONFIG_AUDITOR_MIDDLEWARE_ENABLE" "True"
            fi
        else
            if [ "$edit_mode" = "true" ]; then
                update_var "CONFIG_AUDITOR_MIDDLEWARE_ENABLE" "False"
            else
                add_var "CONFIG_AUDITOR_MIDDLEWARE_ENABLE" "False"
            fi
        fi
    fi
    
    # Hostname
    if [ "$edit_mode" = "false" ]; then
        add_section "HOSTNAME CONFIGURATION"
    fi
    local existing_hostname=$(get_existing_value "RENDER_EXTERNAL_HOSTNAME" 2>/dev/null || echo "pdl.denky.dev.br")
    local existing_frontend=$(get_existing_value "RENDER_EXTERNAL_FRONTEND" 2>/dev/null || echo "$existing_hostname")
    RENDER_EXTERNAL_HOSTNAME=$(ask_value "Hostname externo" "$existing_hostname")
    RENDER_EXTERNAL_FRONTEND=$(ask_value "Frontend externo" "$existing_frontend")
    if [ "$edit_mode" = "true" ]; then
        update_var "RENDER_EXTERNAL_HOSTNAME" "$RENDER_EXTERNAL_HOSTNAME"
        update_var "RENDER_EXTERNAL_FRONTEND" "$RENDER_EXTERNAL_FRONTEND"
    else
        add_var "RENDER_EXTERNAL_HOSTNAME" "$RENDER_EXTERNAL_HOSTNAME"
        add_var "RENDER_EXTERNAL_FRONTEND" "$RENDER_EXTERNAL_FRONTEND"
    fi
    
    # Encryption
    # IMPORTANTE: NÃO sobrescreve chaves existentes para evitar quebrar dados criptografados
    local existing_encryption=$(get_existing_value "ENCRYPTION_KEY" 2>/dev/null || echo "")
    local default_key="iOg0mMfE54rqvAOZKxhmb-Rq0sgmRC4p1TBGu_JqHac="
    
    if [ -z "$existing_encryption" ]; then
        # Se não existe, gera uma nova
        log_info "Gerando ENCRYPTION_KEY..."
        ENCRYPTION_KEY=$(generate_fernet_key 2>/dev/null || echo "$default_key")
        if [ "$edit_mode" = "true" ]; then
            update_var "ENCRYPTION_KEY" "'$ENCRYPTION_KEY'"
        else
            add_var "ENCRYPTION_KEY" "'$ENCRYPTION_KEY'"
        fi
    elif [ "$existing_encryption" = "$default_key" ]; then
        # Se for a chave padrão/placeholder, substitui (apenas primeira instalação)
        log_warning "ENCRYPTION_KEY é a chave padrão/placeholder. Gerando nova chave..."
        ENCRYPTION_KEY=$(generate_fernet_key 2>/dev/null || echo "$default_key")
        if [ "$edit_mode" = "true" ]; then
            update_var "ENCRYPTION_KEY" "'$ENCRYPTION_KEY'"
            log_warning "ATENÇÃO: Se houver dados criptografados com a chave antiga, eles não poderão ser descriptografados!"
        else
            add_var "ENCRYPTION_KEY" "'$ENCRYPTION_KEY'"
        fi
    else
        # Se já existe e não é a chave padrão, mantém (CRÍTICO: não sobrescrever!)
        log_info "ENCRYPTION_KEY já existe, mantendo valor atual (não será alterado para preservar dados criptografados)."
    fi
    local existing_upload_size=$(get_existing_value "DATA_UPLOAD_MAX_MEMORY_SIZE" 2>/dev/null || echo "31457280")
    if [ "$edit_mode" = "true" ]; then
        update_var "DATA_UPLOAD_MAX_MEMORY_SIZE" "$existing_upload_size"
    else
        add_var "DATA_UPLOAD_MAX_MEMORY_SIZE" "$existing_upload_size"
    fi
    
    # hCaptcha
    if [ "$edit_mode" = "false" ]; then
        add_section "HCAPTCHA CONFIGURATION"
    fi
    local existing_hcaptcha_site=$(get_existing_value "CONFIG_HCAPTCHA_SITE_KEY" 2>/dev/null || echo "bcf40348-fa88-4570-a752-2asdasde0b2bc")
    local existing_hcaptcha_secret=$(get_existing_value "CONFIG_HCAPTCHA_SECRET_KEY" 2>/dev/null || echo "ES_dc688fdasdasdadasdas4e918093asddsddsafa3f1b")
    local existing_max_attempts=$(get_existing_value "CONFIG_LOGIN_MAX_ATTEMPTS" 2>/dev/null || echo "3")
    local existing_fail_open=$(get_existing_value "CONFIG_HCAPTCHA_FAIL_OPEN" 2>/dev/null || echo "False")
    
    CONFIG_HCAPTCHA_SITE_KEY=$(ask_value "hCaptcha Site Key" "$existing_hcaptcha_site")
    CONFIG_HCAPTCHA_SECRET_KEY=$(ask_value "hCaptcha Secret Key" "$existing_hcaptcha_secret")
    CONFIG_LOGIN_MAX_ATTEMPTS=$(ask_value "Número máximo de tentativas de login" "$existing_max_attempts")
    CONFIG_HCAPTCHA_FAIL_OPEN=$(ask_value "hCaptcha Fail Open (True/False)" "$existing_fail_open")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "CONFIG_HCAPTCHA_SITE_KEY" "$CONFIG_HCAPTCHA_SITE_KEY"
        update_var "CONFIG_HCAPTCHA_SECRET_KEY" "$CONFIG_HCAPTCHA_SECRET_KEY"
        update_var "CONFIG_LOGIN_MAX_ATTEMPTS" "$CONFIG_LOGIN_MAX_ATTEMPTS"
        update_var "CONFIG_HCAPTCHA_FAIL_OPEN" "$CONFIG_HCAPTCHA_FAIL_OPEN"
    else
        add_var "CONFIG_HCAPTCHA_SITE_KEY" "$CONFIG_HCAPTCHA_SITE_KEY"
        add_var "CONFIG_HCAPTCHA_SECRET_KEY" "$CONFIG_HCAPTCHA_SECRET_KEY"
        add_var "CONFIG_LOGIN_MAX_ATTEMPTS" "$CONFIG_LOGIN_MAX_ATTEMPTS"
        add_var "CONFIG_HCAPTCHA_FAIL_OPEN" "$CONFIG_HCAPTCHA_FAIL_OPEN"
    fi
    
    # Lineage Query Module
    if [ "$edit_mode" = "false" ]; then
        add_section "LINEAGE QUERY MODULE"
    fi
    local existing_query_module=$(get_existing_value "LINEAGE_QUERY_MODULE" 2>/dev/null || echo "dreamv3")
    LINEAGE_QUERY_MODULE=$(ask_value "Módulo de query do Lineage" "$existing_query_module")
    if [ "$edit_mode" = "true" ]; then
        update_var "LINEAGE_QUERY_MODULE" "$LINEAGE_QUERY_MODULE"
    else
        add_var "LINEAGE_QUERY_MODULE" "$LINEAGE_QUERY_MODULE"
    fi
    
    # Localization
    if [ "$edit_mode" = "false" ]; then
        add_section "LOCALIZATION"
    fi
    local existing_lang=$(get_existing_value "CONFIG_LANGUAGE_CODE" 2>/dev/null | sed 's/"//g' || echo "pt")
    local existing_tz=$(get_existing_value "CONFIG_TIME_ZONE" 2>/dev/null | sed 's/"//g' || echo "America/Recife")
    local existing_decimal=$(get_existing_value "CONFIG_DECIMAL_SEPARATOR" 2>/dev/null | sed "s/'//g" || echo ",")
    local existing_thousand=$(get_existing_value "CONFIG_USE_THOUSAND_SEPARATOR" 2>/dev/null || echo "True")
    local existing_datetime=$(get_existing_value "CONFIG_DATETIME_FORMAT" 2>/dev/null | sed "s/'//g" || echo "d/m/Y H:i:s")
    local existing_date=$(get_existing_value "CONFIG_DATE_FORMAT" 2>/dev/null | sed "s/'//g" || echo "d/m/Y")
    local existing_time=$(get_existing_value "CONFIG_TIME_FORMAT" 2>/dev/null | sed "s/'//g" || echo "H:i:s")
    local existing_gmt=$(get_existing_value "CONFIG_GMT_OFFSET" 2>/dev/null || echo "-3")
    
    CONFIG_LANGUAGE_CODE=$(ask_value "Código do idioma (pt/en/es)" "$existing_lang")
    CONFIG_TIME_ZONE=$(ask_value "Fuso horário" "$existing_tz")
    CONFIG_DECIMAL_SEPARATOR=$(ask_value "Separador decimal" "$existing_decimal")
    CONFIG_USE_THOUSAND_SEPARATOR=$(ask_value "Usar separador de milhar? (True/False)" "$existing_thousand")
    CONFIG_DATETIME_FORMAT=$(ask_value "Formato de data/hora" "$existing_datetime")
    CONFIG_DATE_FORMAT=$(ask_value "Formato de data" "$existing_date")
    CONFIG_TIME_FORMAT=$(ask_value "Formato de hora" "$existing_time")
    CONFIG_GMT_OFFSET=$(ask_value "Offset GMT" "$existing_gmt")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "CONFIG_LANGUAGE_CODE" "\"$CONFIG_LANGUAGE_CODE\""
        update_var "CONFIG_TIME_ZONE" "\"$CONFIG_TIME_ZONE\""
        update_var "CONFIG_DECIMAL_SEPARATOR" "'$CONFIG_DECIMAL_SEPARATOR'"
        update_var "CONFIG_USE_THOUSAND_SEPARATOR" "$CONFIG_USE_THOUSAND_SEPARATOR"
        update_var "CONFIG_DATETIME_FORMAT" "'$CONFIG_DATETIME_FORMAT'"
        update_var "CONFIG_DATE_FORMAT" "'$CONFIG_DATE_FORMAT'"
        update_var "CONFIG_TIME_FORMAT" "'$CONFIG_TIME_FORMAT'"
        update_var "CONFIG_GMT_OFFSET" "$CONFIG_GMT_OFFSET"
    else
        add_var "CONFIG_LANGUAGE_CODE" "\"$CONFIG_LANGUAGE_CODE\""
        add_var "CONFIG_TIME_ZONE" "\"$CONFIG_TIME_ZONE\""
        add_var "CONFIG_DECIMAL_SEPARATOR" "'$CONFIG_DECIMAL_SEPARATOR'"
        add_var "CONFIG_USE_THOUSAND_SEPARATOR" "$CONFIG_USE_THOUSAND_SEPARATOR"
        add_var "CONFIG_DATETIME_FORMAT" "'$CONFIG_DATETIME_FORMAT'"
        add_var "CONFIG_DATE_FORMAT" "'$CONFIG_DATE_FORMAT'"
        add_var "CONFIG_TIME_FORMAT" "'$CONFIG_TIME_FORMAT'"
        add_var "CONFIG_GMT_OFFSET" "$CONFIG_GMT_OFFSET"
    fi
    
    # Project Info
    if [ "$edit_mode" = "false" ]; then
        add_section "PROJECT INFORMATION"
    fi
    local existing_title=$(get_existing_value "PROJECT_TITLE" 2>/dev/null || echo "Lineage 2 PDL")
    local existing_author=$(get_existing_value "PROJECT_AUTHOR" 2>/dev/null || echo "Lineage 2 PDL")
    local existing_desc=$(get_existing_value "PROJECT_DESCRIPTION" 2>/dev/null || echo "O PDL é um painel que nasceu com a missão de oferecer ferramentas poderosas para administradores de servidores privados de Lineage 2.")
    local existing_keywords=$(get_existing_value "PROJECT_KEYWORDS" 2>/dev/null || echo "lineage l2 painel servidor")
    local existing_url=$(get_existing_value "PROJECT_URL" 2>/dev/null || echo "https://pdl.denky.dev.br")
    local existing_logo=$(get_existing_value "PROJECT_LOGO_URL" 2>/dev/null || echo "/static/assets/img/logo_painel.png")
    local existing_favicon=$(get_existing_value "PROJECT_FAVICON_ICO" 2>/dev/null || echo "/static/assets/img/ico.jpg")
    local existing_manifest=$(get_existing_value "PROJECT_FAVICON_MANIFEST" 2>/dev/null || echo "/static/assets/img/favicon/site.webmanifest")
    local existing_theme=$(get_existing_value "PROJECT_THEME_COLOR" 2>/dev/null || echo "#ffffff")
    
    PROJECT_TITLE=$(ask_value "Título do projeto" "$existing_title")
    PROJECT_AUTHOR=$(ask_value "Autor do projeto" "$existing_author")
    PROJECT_DESCRIPTION=$(ask_value "Descrição do projeto" "$existing_desc")
    PROJECT_KEYWORDS=$(ask_value "Palavras-chave" "$existing_keywords")
    PROJECT_URL=$(ask_value "URL do projeto" "$existing_url")
    PROJECT_LOGO_URL=$(ask_value "URL do logo" "$existing_logo")
    PROJECT_FAVICON_ICO=$(ask_value "URL do favicon .ico" "$existing_favicon")
    PROJECT_FAVICON_MANIFEST=$(ask_value "URL do manifest" "$existing_manifest")
    PROJECT_THEME_COLOR=$(ask_value "Cor do tema" "$existing_theme")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "PROJECT_TITLE" "$PROJECT_TITLE"
        update_var "PROJECT_AUTHOR" "$PROJECT_AUTHOR"
        update_var "PROJECT_DESCRIPTION" "$PROJECT_DESCRIPTION"
        update_var "PROJECT_KEYWORDS" "$PROJECT_KEYWORDS"
        update_var "PROJECT_URL" "$PROJECT_URL"
        update_var "PROJECT_LOGO_URL" "$PROJECT_LOGO_URL"
        update_var "PROJECT_FAVICON_ICO" "$PROJECT_FAVICON_ICO"
        update_var "PROJECT_FAVICON_MANIFEST" "$PROJECT_FAVICON_MANIFEST"
        update_var "PROJECT_THEME_COLOR" "$PROJECT_THEME_COLOR"
    else
        add_var "PROJECT_TITLE" "$PROJECT_TITLE"
        add_var "PROJECT_AUTHOR" "$PROJECT_AUTHOR"
        add_var "PROJECT_DESCRIPTION" "$PROJECT_DESCRIPTION"
        add_var "PROJECT_KEYWORDS" "$PROJECT_KEYWORDS"
        add_var "PROJECT_URL" "$PROJECT_URL"
        add_var "PROJECT_LOGO_URL" "$PROJECT_LOGO_URL"
        add_var "PROJECT_FAVICON_ICO" "$PROJECT_FAVICON_ICO"
        add_var "PROJECT_FAVICON_MANIFEST" "$PROJECT_FAVICON_MANIFEST"
        add_var "PROJECT_THEME_COLOR" "$PROJECT_THEME_COLOR"
    fi
    
    # Social Media Links
    if [ "$edit_mode" = "false" ]; then
        add_section "SOCIAL MEDIA LINKS"
    fi
    local existing_discord=$(get_existing_value "PROJECT_DISCORD_URL" 2>/dev/null | sed "s/'//g" || echo "https://discord.gg/seu-link-aqui")
    local existing_youtube=$(get_existing_value "PROJECT_YOUTUBE_URL" 2>/dev/null | sed "s/'//g" || echo "https://www.youtube.com/@seu-canal")
    local existing_facebook=$(get_existing_value "PROJECT_FACEBOOK_URL" 2>/dev/null | sed "s/'//g" || echo "https://www.facebook.com/sua-pagina")
    local existing_instagram=$(get_existing_value "PROJECT_INSTAGRAM_URL" 2>/dev/null | sed "s/'//g" || echo "https://www.instagram.com/seu-perfil")
    
    PROJECT_DISCORD_URL=$(ask_value "URL do Discord" "$existing_discord")
    PROJECT_YOUTUBE_URL=$(ask_value "URL do YouTube" "$existing_youtube")
    PROJECT_FACEBOOK_URL=$(ask_value "URL do Facebook" "$existing_facebook")
    PROJECT_INSTAGRAM_URL=$(ask_value "URL do Instagram" "$existing_instagram")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "PROJECT_DISCORD_URL" "'$PROJECT_DISCORD_URL'"
        update_var "PROJECT_YOUTUBE_URL" "'$PROJECT_YOUTUBE_URL'"
        update_var "PROJECT_FACEBOOK_URL" "'$PROJECT_FACEBOOK_URL'"
        update_var "PROJECT_INSTAGRAM_URL" "'$PROJECT_INSTAGRAM_URL'"
    else
        add_var "PROJECT_DISCORD_URL" "'$PROJECT_DISCORD_URL'"
        add_var "PROJECT_YOUTUBE_URL" "'$PROJECT_YOUTUBE_URL'"
        add_var "PROJECT_FACEBOOK_URL" "'$PROJECT_FACEBOOK_URL'"
        add_var "PROJECT_INSTAGRAM_URL" "'$PROJECT_INSTAGRAM_URL'"
    fi
    
    # Basic Flags
    if [ "$edit_mode" = "false" ]; then
        add_section "BASIC FLAGS"
    fi
    local existing_docker=$(get_existing_value "RUNNING_IN_DOCKER" 2>/dev/null || echo "True")
    local existing_slogan=$(get_existing_value "SLOGAN" 2>/dev/null || echo "True")
    local existing_lineage_db=$(get_existing_value "LINEAGE_DB_ENABLED" 2>/dev/null || echo "False")
    local existing_theme_errors=$(get_existing_value "SHOW_THEME_ERRORS_TO_USERS" 2>/dev/null || echo "True")
    
    local existing_account_link_free_slots=$(get_existing_value "ACCOUNT_LINK_FREE_SLOTS" 2>/dev/null || echo "3")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "RUNNING_IN_DOCKER" "$existing_docker"
        update_var "SLOGAN" "$existing_slogan"
        update_var "LINEAGE_DB_ENABLED" "$existing_lineage_db"
        update_var "SHOW_THEME_ERRORS_TO_USERS" "$existing_theme_errors"
        update_var "ACCOUNT_LINK_FREE_SLOTS" "$existing_account_link_free_slots"
    else
        add_var "RUNNING_IN_DOCKER" "$existing_docker"
        add_var "SLOGAN" "$existing_slogan"
        add_var "LINEAGE_DB_ENABLED" "$existing_lineage_db"
        add_var "SHOW_THEME_ERRORS_TO_USERS" "$existing_theme_errors"
        add_var "ACCOUNT_LINK_FREE_SLOTS" "$existing_account_link_free_slots"
    fi
}

# Função para gerar configuração de Email
generate_email_config() {
    local edit_mode="${1:-false}"
    if [ "$edit_mode" = "false" ]; then
        add_section "EMAIL CONFIGURATION"
    fi
    
    local existing_email_enable=$(get_existing_value "CONFIG_EMAIL_ENABLE" 2>/dev/null || echo "False")
    local email_enable_default=$(echo "$existing_email_enable" | tr '[:upper:]' '[:lower:]')
    
    if ask_yes_no "Habilitar envio de emails?" "$email_enable_default"; then
        add_var "CONFIG_EMAIL_ENABLE" "True"
        local existing_tls=$(get_existing_value "CONFIG_EMAIL_USE_TLS" 2>/dev/null || echo "True")
        local existing_smtp=$(get_existing_value "CONFIG_EMAIL_HOST" 2>/dev/null || echo "smtp.domain.com")
        local existing_port=$(get_existing_value "CONFIG_EMAIL_PORT" 2>/dev/null || echo "587")
        local existing_user=$(get_existing_value "CONFIG_EMAIL_HOST_USER" 2>/dev/null || echo "mail@mail.dev.br")
        local existing_pass=$(get_existing_value "CONFIG_EMAIL_HOST_PASSWORD" 2>/dev/null || echo "password")
        local existing_from=$(get_existing_value "CONFIG_DEFAULT_FROM_EMAIL" 2>/dev/null || echo "$existing_user")
        
        CONFIG_EMAIL_USE_TLS=$(ask_yes_no "Usar TLS?" "$(echo "$existing_tls" | tr '[:upper:]' '[:lower:]')" && echo "True" || echo "False")
        CONFIG_EMAIL_HOST=$(ask_value "Servidor SMTP" "$existing_smtp")
        CONFIG_EMAIL_PORT=$(ask_value "Porta SMTP" "$existing_port")
        CONFIG_EMAIL_HOST_USER=$(ask_value "Usuário do email" "$existing_user")
        CONFIG_EMAIL_HOST_PASSWORD=$(ask_value "Senha do email" "$existing_pass")
        CONFIG_DEFAULT_FROM_EMAIL=$(ask_value "Email remetente padrão" "$existing_from")
        
        if [ "$edit_mode" = "true" ]; then
            update_var "CONFIG_EMAIL_USE_TLS" "$CONFIG_EMAIL_USE_TLS"
            update_var "CONFIG_EMAIL_HOST" "$CONFIG_EMAIL_HOST"
            update_var "CONFIG_EMAIL_PORT" "$CONFIG_EMAIL_PORT"
            update_var "CONFIG_EMAIL_HOST_USER" "$CONFIG_EMAIL_HOST_USER"
            update_var "CONFIG_EMAIL_HOST_PASSWORD" "$CONFIG_EMAIL_HOST_PASSWORD"
            update_var "CONFIG_DEFAULT_FROM_EMAIL" "$CONFIG_DEFAULT_FROM_EMAIL"
        else
            add_var "CONFIG_EMAIL_USE_TLS" "$CONFIG_EMAIL_USE_TLS"
            add_var "CONFIG_EMAIL_HOST" "$CONFIG_EMAIL_HOST"
            add_var "CONFIG_EMAIL_PORT" "$CONFIG_EMAIL_PORT"
            add_var "CONFIG_EMAIL_HOST_USER" "$CONFIG_EMAIL_HOST_USER"
            add_var "CONFIG_EMAIL_HOST_PASSWORD" "$CONFIG_EMAIL_HOST_PASSWORD"
            add_var "CONFIG_DEFAULT_FROM_EMAIL" "$CONFIG_DEFAULT_FROM_EMAIL"
        fi
    else
        if [ "$edit_mode" = "true" ]; then
            update_var "CONFIG_EMAIL_ENABLE" "False"
            update_var "CONFIG_EMAIL_USE_TLS" "True"
            update_var "CONFIG_EMAIL_HOST" "smtp.domain.com"
            update_var "CONFIG_EMAIL_PORT" "587"
            update_var "CONFIG_EMAIL_HOST_USER" "mail@mail.dev.br"
            update_var "CONFIG_EMAIL_HOST_PASSWORD" "password"
            update_var "CONFIG_DEFAULT_FROM_EMAIL" "mail@mail.dev.br"
        else
            add_var "CONFIG_EMAIL_ENABLE" "False"
            add_var "CONFIG_EMAIL_USE_TLS" "True"
            add_var "CONFIG_EMAIL_HOST" "smtp.domain.com"
            add_var "CONFIG_EMAIL_PORT" "587"
            add_var "CONFIG_EMAIL_HOST_USER" "mail@mail.dev.br"
            add_var "CONFIG_EMAIL_HOST_PASSWORD" "password"
            add_var "CONFIG_DEFAULT_FROM_EMAIL" "mail@mail.dev.br"
        fi
    fi
}

# Função para gerar configuração do Lineage DB
generate_lineage_db_config() {
    local edit_mode="${1:-false}"
    if [ "$edit_mode" = "false" ]; then
        add_section "LINEAGE DATABASE CONFIGURATION"
    fi
    
    local existing_db_name=$(get_existing_value "LINEAGE_DB_NAME" 2>/dev/null || echo "l2jdb")
    local existing_db_user=$(get_existing_value "LINEAGE_DB_USER" 2>/dev/null || echo "l2user")
    local existing_db_pass=$(get_existing_value "LINEAGE_DB_PASSWORD" 2>/dev/null || echo "suaSenhaAqui")
    local existing_db_host=$(get_existing_value "LINEAGE_DB_HOST" 2>/dev/null || echo "192.168.1.100")
    local existing_db_port=$(get_existing_value "LINEAGE_DB_PORT" 2>/dev/null || echo "3306")
    
    LINEAGE_DB_NAME=$(ask_value "Nome do banco Lineage" "$existing_db_name")
    LINEAGE_DB_USER=$(ask_value "Usuário do banco Lineage" "$existing_db_user")
    LINEAGE_DB_PASSWORD=$(ask_value "Senha do banco Lineage" "$existing_db_pass")
    LINEAGE_DB_HOST=$(ask_value "Host do banco Lineage" "$existing_db_host")
    LINEAGE_DB_PORT=$(ask_value "Porta do banco Lineage" "$existing_db_port")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "LINEAGE_DB_NAME" "$LINEAGE_DB_NAME"
        update_var "LINEAGE_DB_USER" "$LINEAGE_DB_USER"
        update_var "LINEAGE_DB_PASSWORD" "$LINEAGE_DB_PASSWORD"
        update_var "LINEAGE_DB_HOST" "$LINEAGE_DB_HOST"
        update_var "LINEAGE_DB_PORT" "$LINEAGE_DB_PORT"
    else
        add_var "LINEAGE_DB_NAME" "$LINEAGE_DB_NAME"
        add_var "LINEAGE_DB_USER" "$LINEAGE_DB_USER"
        add_var "LINEAGE_DB_PASSWORD" "$LINEAGE_DB_PASSWORD"
        add_var "LINEAGE_DB_HOST" "$LINEAGE_DB_HOST"
        add_var "LINEAGE_DB_PORT" "$LINEAGE_DB_PORT"
    fi
}

# Função para gerar configuração do AWS S3
generate_s3_config() {
    local edit_mode="${1:-false}"
    if [ "$edit_mode" = "false" ]; then
        add_section "AWS S3 CONFIGURATION"
    fi
    
    local existing_use_s3=$(get_existing_value "USE_S3" 2>/dev/null || echo "False")
    local s3_default=$(echo "$existing_use_s3" | tr '[:upper:]' '[:lower:]')
    
    if ask_yes_no "Usar AWS S3 para armazenamento?" "$s3_default"; then
        add_var "USE_S3" "True"
        AWS_ACCESS_KEY_ID=$(ask_value "AWS Access Key ID" "your_aws_access_key_id")
        AWS_SECRET_ACCESS_KEY=$(ask_value "AWS Secret Access Key" "your_aws_secret_access_key")
        AWS_STORAGE_BUCKET_NAME=$(ask_value "Nome do bucket S3" "your-bucket-name")
        AWS_S3_REGION_NAME=$(ask_value "Região do S3" "us-east-1")
        AWS_S3_CUSTOM_DOMAIN=$(ask_value "Domínio customizado do S3" "${AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com")
        
        add_var "AWS_ACCESS_KEY_ID" "$AWS_ACCESS_KEY_ID"
        add_var "AWS_SECRET_ACCESS_KEY" "$AWS_SECRET_ACCESS_KEY"
        add_var "AWS_STORAGE_BUCKET_NAME" "$AWS_STORAGE_BUCKET_NAME"
        add_var "AWS_S3_REGION_NAME" "$AWS_S3_REGION_NAME"
        add_var "AWS_S3_CUSTOM_DOMAIN" "$AWS_S3_CUSTOM_DOMAIN"
    else
        add_var "USE_S3" "False"
        add_var "AWS_ACCESS_KEY_ID" "your_aws_access_key_id"
        add_var "AWS_SECRET_ACCESS_KEY" "your_aws_secret_access_key"
        add_var "AWS_STORAGE_BUCKET_NAME" "your-bucket-name"
        add_var "AWS_S3_REGION_NAME" "us-east-1"
        add_var "AWS_S3_CUSTOM_DOMAIN" "your-bucket-name.s3.amazonaws.com"
    fi
}

# Função para gerar configuração de Pagamentos
generate_payments_config() {
    local edit_mode="${1:-false}"
    if [ "$edit_mode" = "false" ]; then
        add_section "PAYMENT CONFIGURATION"
    fi
    
    # Mercado Pago
    echo
    log_info "Configuração do Mercado Pago:"
    local existing_mp_activate=$(get_existing_value "CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS" 2>/dev/null || echo "False")
    local existing_mp_token=$(get_existing_value "CONFIG_MERCADO_PAGO_ACCESS_TOKEN" 2>/dev/null | sed 's/"//g' || echo "APP_USR-0000000000000000-000000-00000000000000000000000000000000-000000000")
    local existing_mp_public=$(get_existing_value "CONFIG_MERCADO_PAGO_PUBLIC_KEY" 2>/dev/null | sed 's/"//g' || echo "APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    local existing_mp_client=$(get_existing_value "CONFIG_MERCADO_PAGO_CLIENT_ID" 2>/dev/null | sed 's/"//g' || echo "0000000000000000")
    local existing_mp_secret=$(get_existing_value "CONFIG_MERCADO_PAGO_CLIENT_SECRET" 2>/dev/null | sed 's/"//g' || echo "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    local existing_mp_signature=$(get_existing_value "CONFIG_MERCADO_PAGO_SIGNATURE" 2>/dev/null | sed 's/"//g' || echo "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    local mp_activate_default=$(echo "$existing_mp_activate" | tr '[:upper:]' '[:lower:]')
    if ask_yes_no "Habilitar pagamentos via Mercado Pago?" "$mp_activate_default"; then
        CONFIG_MERCADO_PAGO_ACCESS_TOKEN=$(ask_value "Mercado Pago Access Token" "$existing_mp_token")
        CONFIG_MERCADO_PAGO_PUBLIC_KEY=$(ask_value "Mercado Pago Public Key" "$existing_mp_public")
        CONFIG_MERCADO_PAGO_CLIENT_ID=$(ask_value "Mercado Pago Client ID" "$existing_mp_client")
        CONFIG_MERCADO_PAGO_CLIENT_SECRET=$(ask_value "Mercado Pago Client Secret" "$existing_mp_secret")
        CONFIG_MERCADO_PAGO_SIGNATURE=$(ask_value "Mercado Pago Signature" "$existing_mp_signature")
        
        if [ "$edit_mode" = "true" ]; then
            update_var "CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS" "True"
            update_var "CONFIG_MERCADO_PAGO_ACCESS_TOKEN" "\"$CONFIG_MERCADO_PAGO_ACCESS_TOKEN\""
            update_var "CONFIG_MERCADO_PAGO_PUBLIC_KEY" "\"$CONFIG_MERCADO_PAGO_PUBLIC_KEY\""
            update_var "CONFIG_MERCADO_PAGO_CLIENT_ID" "\"$CONFIG_MERCADO_PAGO_CLIENT_ID\""
            update_var "CONFIG_MERCADO_PAGO_CLIENT_SECRET" "\"$CONFIG_MERCADO_PAGO_CLIENT_SECRET\""
            update_var "CONFIG_MERCADO_PAGO_SIGNATURE" "\"$CONFIG_MERCADO_PAGO_SIGNATURE\""
        else
            add_var "CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS" "True"
            add_var "CONFIG_MERCADO_PAGO_ACCESS_TOKEN" "\"$CONFIG_MERCADO_PAGO_ACCESS_TOKEN\""
            add_var "CONFIG_MERCADO_PAGO_PUBLIC_KEY" "\"$CONFIG_MERCADO_PAGO_PUBLIC_KEY\""
            add_var "CONFIG_MERCADO_PAGO_CLIENT_ID" "\"$CONFIG_MERCADO_PAGO_CLIENT_ID\""
            add_var "CONFIG_MERCADO_PAGO_CLIENT_SECRET" "\"$CONFIG_MERCADO_PAGO_CLIENT_SECRET\""
            add_var "CONFIG_MERCADO_PAGO_SIGNATURE" "\"$CONFIG_MERCADO_PAGO_SIGNATURE\""
        fi
    else
        if [ "$edit_mode" = "true" ]; then
            update_var "CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS" "False"
            update_var "CONFIG_MERCADO_PAGO_ACCESS_TOKEN" "\"$existing_mp_token\""
            update_var "CONFIG_MERCADO_PAGO_PUBLIC_KEY" "\"$existing_mp_public\""
            update_var "CONFIG_MERCADO_PAGO_CLIENT_ID" "\"$existing_mp_client\""
            update_var "CONFIG_MERCADO_PAGO_CLIENT_SECRET" "\"$existing_mp_secret\""
            update_var "CONFIG_MERCADO_PAGO_SIGNATURE" "\"$existing_mp_signature\""
        else
            add_var "CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS" "False"
            add_var "CONFIG_MERCADO_PAGO_ACCESS_TOKEN" "\"APP_USR-0000000000000000-000000-00000000000000000000000000000000-000000000\""
            add_var "CONFIG_MERCADO_PAGO_PUBLIC_KEY" "\"APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx\""
            add_var "CONFIG_MERCADO_PAGO_CLIENT_ID" "\"0000000000000000\""
            add_var "CONFIG_MERCADO_PAGO_CLIENT_SECRET" "\"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\""
            add_var "CONFIG_MERCADO_PAGO_SIGNATURE" "\"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\""
        fi
    fi
    
    # Stripe
    echo
    log_info "Configuração do Stripe:"
    local existing_stripe_activate=$(get_existing_value "CONFIG_STRIPE_ACTIVATE_PAYMENTS" 2>/dev/null || echo "False")
    local existing_stripe_secret=$(get_existing_value "CONFIG_STRIPE_SECRET_KEY" 2>/dev/null | sed "s/'//g" || echo "sk_test_51RK0cORmyaPSbmPDEMjN0DaasdasdadadasdafgagdhhfasdfsfnbgRrtdKRwHRakfrQub9SQ5jQEUNvTfrcFxbw00gsqFR09W")
    local existing_stripe_webhook=$(get_existing_value "CONFIG_STRIPE_WEBHOOK_SECRET" 2>/dev/null | sed "s/'//g" || echo "whsec_5dzjceF7LgeYzasdasdasdZpSuPq")
    
    local stripe_activate_default=$(echo "$existing_stripe_activate" | tr '[:upper:]' '[:lower:]')
    if ask_yes_no "Habilitar pagamentos via Stripe?" "$stripe_activate_default"; then
        CONFIG_STRIPE_SECRET_KEY=$(ask_value "Stripe Secret Key" "$existing_stripe_secret")
        CONFIG_STRIPE_WEBHOOK_SECRET=$(ask_value "Stripe Webhook Secret" "$existing_stripe_webhook")
        
        if [ "$edit_mode" = "true" ]; then
            update_var "CONFIG_STRIPE_ACTIVATE_PAYMENTS" "True"
            update_var "CONFIG_STRIPE_SECRET_KEY" "'$CONFIG_STRIPE_SECRET_KEY'"
            update_var "CONFIG_STRIPE_WEBHOOK_SECRET" "'$CONFIG_STRIPE_WEBHOOK_SECRET'"
        else
            add_var "CONFIG_STRIPE_ACTIVATE_PAYMENTS" "True"
            add_var "CONFIG_STRIPE_SECRET_KEY" "'$CONFIG_STRIPE_SECRET_KEY'"
            add_var "CONFIG_STRIPE_WEBHOOK_SECRET" "'$CONFIG_STRIPE_WEBHOOK_SECRET'"
        fi
    else
        if [ "$edit_mode" = "true" ]; then
            update_var "CONFIG_STRIPE_ACTIVATE_PAYMENTS" "False"
            update_var "CONFIG_STRIPE_SECRET_KEY" "'$existing_stripe_secret'"
            update_var "CONFIG_STRIPE_WEBHOOK_SECRET" "'$existing_stripe_webhook'"
        else
            add_var "CONFIG_STRIPE_ACTIVATE_PAYMENTS" "False"
            add_var "CONFIG_STRIPE_SECRET_KEY" "'sk_test_51RK0cORmyaPSbmPDEMjN0DaasdasdadadasdafgagdhhfasdfsfnbgRrtdKRwHRakfrQub9SQ5jQEUNvTfrcFxbw00gsqFR09W'"
            add_var "CONFIG_STRIPE_WEBHOOK_SECRET" "'whsec_5dzjceF7LgeYzasdasdasdZpSuPq'"
        fi
    fi
}

# Função para gerar configuração de Social Login
generate_social_login_config() {
    add_section "SOCIAL LOGIN CONFIGURATION"
    
    if ask_yes_no "Habilitar login social?" "n"; then
        add_var "SOCIAL_LOGIN_ENABLED" "True"
        
        # Google
        if ask_yes_no "Habilitar login com Google?" "n"; then
            add_var "SOCIAL_LOGIN_GOOGLE_ENABLED" "True"
            GOOGLE_CLIENT_ID=$(ask_value "Google Client ID" "3029asdasd17179-i4lfm6078nrov5lhv9628bch2o8vlqs8.apps.googleusercontent.com")
            GOOGLE_SECRET_KEY=$(ask_value "Google Secret Key" "GOCSPX-bWw9hU6Mb3pasdasdasd")
            add_var "GOOGLE_CLIENT_ID" "$GOOGLE_CLIENT_ID"
            add_var "GOOGLE_SECRET_KEY" "$GOOGLE_SECRET_KEY"
        else
            add_var "SOCIAL_LOGIN_GOOGLE_ENABLED" "False"
            add_var "GOOGLE_CLIENT_ID" "3029asdasd17179-i4lfm6078nrov5lhv9628bch2o8vlqs8.apps.googleusercontent.com"
            add_var "GOOGLE_SECRET_KEY" "GOCSPX-bWw9hU6Mb3pasdasdasd"
        fi
        
        # GitHub
        if ask_yes_no "Habilitar login com GitHub?" "n"; then
            add_var "SOCIAL_LOGIN_GITHUB_ENABLED" "True"
            GITHUB_CLIENT_ID=$(ask_value "GitHub Client ID" "Ov23liadadadwcXpjog38V")
            GITHUB_SECRET_KEY=$(ask_value "GitHub Secret Key" "ea0d1c77b910eadadadada65a7cbddee1bd07deb")
            add_var "GITHUB_CLINET_ID" "$GITHUB_CLIENT_ID"
            add_var "GITHUB_SECRET_KEY" "$GITHUB_SECRET_KEY"
        else
            add_var "SOCIAL_LOGIN_GITHUB_ENABLED" "False"
            add_var "GITHUB_CLINET_ID" "Ov23liadadadwcXpjog38V"
            add_var "GITHUB_SECRET_KEY" "ea0d1c77b910eadadadada65a7cbddee1bd07deb"
        fi
        
        # Discord
        if ask_yes_no "Habilitar login com Discord?" "n"; then
            add_var "SOCIAL_LOGIN_DISCORD_ENABLED" "True"
            DISCORD_CLIENT_ID=$(ask_value "Discord Client ID" "13836455adada77550336")
            DISCORD_SECRET_KEY=$(ask_value "Discord Secret Key" "Gs9db5OmQ9dadadadadad8CtOQuLKx42fdf")
            add_var "DISCORD_CLIENT_ID" "$DISCORD_CLIENT_ID"
            add_var "DISCORD_SECRET_KEY" "$DISCORD_SECRET_KEY"
        else
            add_var "SOCIAL_LOGIN_DISCORD_ENABLED" "False"
            add_var "DISCORD_CLIENT_ID" "13836455adada77550336"
            add_var "DISCORD_SECRET_KEY" "Gs9db5OmQ9dadadadadad8CtOQuLKx42fdf"
        fi
        
        if ask_yes_no "Mostrar seção de login social na interface?" "n"; then
            add_var "SOCIAL_LOGIN_SHOW_SECTION" "True"
        else
            add_var "SOCIAL_LOGIN_SHOW_SECTION" "False"
        fi
    else
        add_var "SOCIAL_LOGIN_ENABLED" "False"
        add_var "SOCIAL_LOGIN_GOOGLE_ENABLED" "False"
        add_var "SOCIAL_LOGIN_GITHUB_ENABLED" "False"
        add_var "SOCIAL_LOGIN_DISCORD_ENABLED" "False"
        add_var "SOCIAL_LOGIN_SHOW_SECTION" "False"
        add_var "GOOGLE_CLIENT_ID" "3029asdasd17179-i4lfm6078nrov5lhv9628bch2o8vlqs8.apps.googleusercontent.com"
        add_var "GOOGLE_SECRET_KEY" "GOCSPX-bWw9hU6Mb3pasdasdasd"
        add_var "GITHUB_CLINET_ID" "Ov23liadadadwcXpjog38V"
        add_var "GITHUB_SECRET_KEY" "ea0d1c77b910eadadadada65a7cbddee1bd07deb"
        add_var "DISCORD_CLIENT_ID" "13836455adada77550336"
        add_var "DISCORD_SECRET_KEY" "Gs9db5OmQ9dadadadadad8CtOQuLKx42fdf"
    fi
}

# Função para gerar configuração de Server Status
generate_server_status_config() {
    local edit_mode="${1:-false}"
    if [ "$edit_mode" = "false" ]; then
        add_section "SERVER STATUS CONFIGURATION"
    fi
    
    local existing_game_ip=$(get_existing_value "GAME_SERVER_IP" 2>/dev/null || echo "192.168.1.100")
    local existing_game_port=$(get_existing_value "GAME_SERVER_PORT" 2>/dev/null || echo "7777")
    local existing_login_port=$(get_existing_value "LOGIN_SERVER_PORT" 2>/dev/null || echo "2106")
    local existing_timeout=$(get_existing_value "SERVER_STATUS_TIMEOUT" 2>/dev/null || echo "1")
    local existing_force_game=$(get_existing_value "FORCE_GAME_SERVER_STATUS" 2>/dev/null || echo "auto")
    local existing_force_login=$(get_existing_value "FORCE_LOGIN_SERVER_STATUS" 2>/dev/null || echo "auto")
    
    GAME_SERVER_IP=$(ask_value "IP do servidor de jogo" "$existing_game_ip")
    GAME_SERVER_PORT=$(ask_value "Porta do servidor de jogo" "$existing_game_port")
    LOGIN_SERVER_PORT=$(ask_value "Porta do servidor de login" "$existing_login_port")
    SERVER_STATUS_TIMEOUT=$(ask_value "Timeout para verificação (segundos)" "$existing_timeout")
    FORCE_GAME_SERVER_STATUS=$(ask_value "Forçar status do servidor (auto/on/off)" "$existing_force_game")
    FORCE_LOGIN_SERVER_STATUS=$(ask_value "Forçar status do login (auto/on/off)" "$existing_force_login")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "GAME_SERVER_IP" "$GAME_SERVER_IP"
        update_var "GAME_SERVER_PORT" "$GAME_SERVER_PORT"
        update_var "LOGIN_SERVER_PORT" "$LOGIN_SERVER_PORT"
        update_var "SERVER_STATUS_TIMEOUT" "$SERVER_STATUS_TIMEOUT"
        update_var "FORCE_GAME_SERVER_STATUS" "$FORCE_GAME_SERVER_STATUS"
        update_var "FORCE_LOGIN_SERVER_STATUS" "$FORCE_LOGIN_SERVER_STATUS"
    else
        add_var "GAME_SERVER_IP" "$GAME_SERVER_IP"
        add_var "GAME_SERVER_PORT" "$GAME_SERVER_PORT"
        add_var "LOGIN_SERVER_PORT" "$LOGIN_SERVER_PORT"
        add_var "SERVER_STATUS_TIMEOUT" "$SERVER_STATUS_TIMEOUT"
        add_var "FORCE_GAME_SERVER_STATUS" "$FORCE_GAME_SERVER_STATUS"
        add_var "FORCE_LOGIN_SERVER_STATUS" "$FORCE_LOGIN_SERVER_STATUS"
    fi
}

# Função para gerar configuração de Fake Players
generate_fake_players_config() {
    local edit_mode="${1:-false}"
    if [ "$edit_mode" = "false" ]; then
        add_section "FAKE PLAYERS CONFIGURATION"
    fi
    
    local existing_factor=$(get_existing_value "FAKE_PLAYERS_FACTOR" 2>/dev/null || echo "1.0")
    local existing_min=$(get_existing_value "FAKE_PLAYERS_MIN" 2>/dev/null || echo "0")
    local existing_max=$(get_existing_value "FAKE_PLAYERS_MAX" 2>/dev/null || echo "0")
    
    FAKE_PLAYERS_FACTOR=$(ask_value "Multiplicador de jogadores (ex: 1.2 = +20%)" "$existing_factor")
    FAKE_PLAYERS_MIN=$(ask_value "Valor mínimo de jogadores (0 para ignorar)" "$existing_min")
    FAKE_PLAYERS_MAX=$(ask_value "Valor máximo de jogadores (0 para ignorar)" "$existing_max")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "FAKE_PLAYERS_FACTOR" "$FAKE_PLAYERS_FACTOR"
        update_var "FAKE_PLAYERS_MIN" "$FAKE_PLAYERS_MIN"
        update_var "FAKE_PLAYERS_MAX" "$FAKE_PLAYERS_MAX"
    else
        add_var "FAKE_PLAYERS_FACTOR" "$FAKE_PLAYERS_FACTOR"
        add_var "FAKE_PLAYERS_MIN" "$FAKE_PLAYERS_MIN"
        add_var "FAKE_PLAYERS_MAX" "$FAKE_PLAYERS_MAX"
    fi
}

# Função para gerar configuração de VAPID (Web Push)
generate_vapid_config() {
    add_section "VAPID CONFIGURATION (WEB PUSH)"
    
    if ask_yes_no "Configurar VAPID para Web Push?" "n"; then
        log_info "Gerando chaves VAPID..."
        # Nota: Em produção, você deve gerar chaves VAPID reais
        VAPID_PRIVATE_KEY=$(ask_value "VAPID Private Key" "7FDbpSlMB1UrNLWWgtTg5QGs9wC3-d1I6z7PdgplWP4")
        VAPID_PUBLIC_KEY=$(ask_value "VAPID Public Key" "BBQIgwfHEkr1LOgtUFwxm_bbb-h6tRMjxa7GCpVYKBsLdBQ-dkKPmkTidKKedNyWfaPgqQl1tV36yo7AyAhQ0J8")
        add_var "VAPID_PRIVATE_KEY" "$VAPID_PRIVATE_KEY"
        add_var "VAPID_PUBLIC_KEY" "$VAPID_PUBLIC_KEY"
    else
        add_var "VAPID_PRIVATE_KEY" "7FDbpSlMB1UrNLWWgtTg5QGs9wC3-d1I6z7PdgplWP4"
        add_var "VAPID_PUBLIC_KEY" "BBQIgwfHEkr1LOgtUFwxm_bbb-h6tRMjxa7GCpVYKBsLdBQ-dkKPmkTidKKedNyWfaPgqQl1tV36yo7AyAhQ0J8"
    fi
}

# Função para gerar configuração de Telemetria (Prometheus)
generate_telemetry_config() {
    local edit_mode="${1:-false}"
    if [ "$edit_mode" = "false" ]; then
        add_section "TELEMETRY CONFIGURATION"
    fi
    
    local existing_telemetry_enabled=$(get_existing_value "TELEMETRY_ENABLED" 2>/dev/null || echo "False")
    local telemetry_enabled_default=$(echo "$existing_telemetry_enabled" | tr '[:upper:]' '[:lower:]')
    
    if ask_yes_no "Habilitar Telemetria local e externa (Prometheus)?" "$telemetry_enabled_default"; then
        # Gerar chave aleatória caso não exista
        local default_token=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1 2>/dev/null || echo "secret-token-1234")
        local existing_token=$(get_existing_value "TELEMETRY_SCRAPE_TOKEN" 2>/dev/null | sed 's/"//g' | sed "s/'//g" || echo "$default_token")
        
        TELEMETRY_SCRAPE_TOKEN=$(ask_value "Token secreto de segurança para o Grafana (Scrape Token)" "$existing_token")
        
        if [ "$edit_mode" = "true" ]; then
            update_var "TELEMETRY_ENABLED" "True"
            update_var "TELEMETRY_SCRAPE_TOKEN" "'$TELEMETRY_SCRAPE_TOKEN'"
        else
            add_var "TELEMETRY_ENABLED" "True"
            add_var "TELEMETRY_SCRAPE_TOKEN" "'$TELEMETRY_SCRAPE_TOKEN'"
        fi
    else
        if [ "$edit_mode" = "true" ]; then
            update_var "TELEMETRY_ENABLED" "False"
        else
            add_var "TELEMETRY_ENABLED" "False"
        fi
    fi
}

# Função para gerar configuração de Regras de Jogo e Visuais
generate_game_rules_config() {
    local edit_mode="${1:-false}"
    if [ "$edit_mode" = "false" ]; then
        add_section "GAME RULES & VISUALS"
    fi
    
    local existing_players_online=$(get_existing_value "CONFIG_SHOW_PLAYERS_ONLINE" 2>/dev/null || echo "True")
    local players_online_default=$(echo "$existing_players_online" | tr '[:upper:]' '[:lower:]')
    
    if ask_yes_no "Exibir o contador de Jogadores Online na Homepage?" "$players_online_default"; then
        if [ "$edit_mode" = "true" ]; then update_var "CONFIG_SHOW_PLAYERS_ONLINE" "True"; else add_var "CONFIG_SHOW_PLAYERS_ONLINE" "True"; fi
    else
        if [ "$edit_mode" = "true" ]; then update_var "CONFIG_SHOW_PLAYERS_ONLINE" "False"; else add_var "CONFIG_SHOW_PLAYERS_ONLINE" "False"; fi
    fi
    
    local existing_boss_time=$(get_existing_value "CONFIG_GRANDBOSS_SHOW_TIME" 2>/dev/null || echo "True")
    local boss_time_default=$(echo "$existing_boss_time" | tr '[:upper:]' '[:lower:]')
    
    if ask_yes_no "Exibir a Hora e os Minutos precisos do respawn dos Grand Bosses? (Não criará mistério)" "$boss_time_default"; then
        if [ "$edit_mode" = "true" ]; then update_var "CONFIG_GRANDBOSS_SHOW_TIME" "True"; else add_var "CONFIG_GRANDBOSS_SHOW_TIME" "True"; fi
    else
        if [ "$edit_mode" = "true" ]; then update_var "CONFIG_GRANDBOSS_SHOW_TIME" "False"; else add_var "CONFIG_GRANDBOSS_SHOW_TIME" "False"; fi
    fi
    
    local existing_email_verif=$(get_existing_value "ACCOUNT_EMAIL_VERIFICATION" 2>/dev/null || echo "none")
    echo
    log_info "Regras de Email para Cadastro:"
    echo "  none: O jogador cadastra e entra no painel na mesma hora."
    echo "  mandatory: O jogador precisa clicar no link enviado por email."
    ACCOUNT_EMAIL_VERIFICATION=$(ask_value "Digite a regra de verificação" "$existing_email_verif")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "ACCOUNT_EMAIL_VERIFICATION" "$ACCOUNT_EMAIL_VERIFICATION"
    else
        add_var "ACCOUNT_EMAIL_VERIFICATION" "$ACCOUNT_EMAIL_VERIFICATION"
    fi
    
    local existing_account_link_free_slots=$(get_existing_value "ACCOUNT_LINK_FREE_SLOTS" 2>/dev/null || echo "3")
    ACCOUNT_LINK_FREE_SLOTS=$(ask_value "Quantidade máxima de contas Master que cada Painel pode abrigar" "$existing_account_link_free_slots")
    
    if [ "$edit_mode" = "true" ]; then
        update_var "ACCOUNT_LINK_FREE_SLOTS" "$ACCOUNT_LINK_FREE_SLOTS"
    else
        add_var "ACCOUNT_LINK_FREE_SLOTS" "$ACCOUNT_LINK_FREE_SLOTS"
    fi
}

# Função principal
main() {
    clear
    
    echo "========================================================="
    echo "  ⚙️  Gerador de Arquivo .env - PDL"
    echo "========================================================="
    echo
    
    # Verificar se estamos no diretório correto
    if [ ! -f "${PROJECT_DIR}/manage.py" ] && [ ! -f "${PROJECT_DIR}/../manage.py" ]; then
        log_error "Não foi possível encontrar o diretório do projeto Django."
        log_info "Execute este script da raiz do projeto ou de dentro do diretório 'lineage'."
        exit 1
    fi
    
    # Ajustar PROJECT_DIR se necessário
    if [ ! -f "${PROJECT_DIR}/manage.py" ] && [ -f "${PROJECT_DIR}/../manage.py" ]; then
        PROJECT_DIR="${PROJECT_DIR}/.."
        ENV_FILE="${PROJECT_DIR}/.env"
    fi
    
    # Verificar se .env já existe
    local edit_mode=false
    if [ -f "$ENV_FILE" ]; then
        log_warning "Arquivo .env já existe: $ENV_FILE"
        echo
        echo "Escolha uma opção:"
        echo "  1) Editar o arquivo existente (preserva valores atuais)"
        echo "  2) Sobrescrever completamente (cria novo arquivo)"
        echo "  3) Cancelar"
        echo
        read -p "Opção (1/2/3): " OPCAO
        
        case "$OPCAO" in
            1)
                edit_mode=true
                log_info "Fazendo backup do .env existente..."
                cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
                log_success "Modo de edição ativado. Valores existentes serão preservados como padrão."
                ;;
            2)
                edit_mode=false
                log_info "Fazendo backup do .env existente..."
                cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
                # Criar arquivo .env vazio
                > "$ENV_FILE"
                ;;
            3)
                log_info "Operação cancelada."
                exit 0
                ;;
            *)
                log_error "Opção inválida."
                exit 1
                ;;
        esac
    else
        # Criar arquivo .env vazio
        > "$ENV_FILE"
    fi
    
    log_info "Gerando variáveis obrigatórias..."
    generate_required "$edit_mode"
    
    echo
    log_info "Agora vamos configurar as categorias opcionais:"
    echo
    
    # Email
    if ask_yes_no "Incluir configuração de Email?" "n"; then
        generate_email_config "$edit_mode"
    fi
    
    # Lineage DB
    if ask_yes_no "Incluir configuração do Banco de Dados Lineage?" "n"; then
        generate_lineage_db_config "$edit_mode"
    fi
    
    # AWS S3
    if ask_yes_no "Incluir configuração do AWS S3?" "n"; then
        generate_s3_config "$edit_mode"
    fi
    
    # Pagamentos
    if ask_yes_no "Incluir configuração de Pagamentos (Mercado Pago/Stripe)?" "n"; then
        generate_payments_config "$edit_mode"
    fi
    
    # Social Login
    if ask_yes_no "Incluir configuração de Login Social?" "n"; then
        generate_social_login_config "$edit_mode"
    fi
    
    # Server Status
    if ask_yes_no "Incluir configuração de Status do Servidor?" "n"; then
        generate_server_status_config "$edit_mode"
    fi
    
    # Fake Players
    if ask_yes_no "Incluir configuração de Jogadores Falsos?" "n"; then
        generate_fake_players_config "$edit_mode"
    fi
    
    # VAPID
    if ask_yes_no "Incluir configuração de VAPID (Web Push)?" "n"; then
        generate_vapid_config "$edit_mode"
    fi
    
    # Game Rules & Visuals
    if ask_yes_no "Incluir configuração de Regras de Jogo e Estética Visual?" "y"; then
        generate_game_rules_config "$edit_mode"
    fi
    
    # Telemetria / Prometheus
    if ask_yes_no "Incluir configuração de Telemetria (Monitoria de Eventos e HTTP)?" "n"; then
        generate_telemetry_config "$edit_mode"
    fi
    
    echo
    if [ "$edit_mode" = "true" ]; then
        log_success "Arquivo .env atualizado com sucesso!"
    else
        log_success "Arquivo .env gerado com sucesso!"
    fi
    log_info "Localização: $ENV_FILE"
    echo
    log_warning "IMPORTANTE: Revise o arquivo .env e ajuste os valores conforme necessário!"
    echo
}

# Executar função principal
main "$@"

