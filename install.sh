#!/bin/bash

################################################################################
# Painel Definitivo Lineage (PDL) - Script de Instalação
# 
# Este script automatiza a instalação completa do PDL usando os scripts
# da pasta setup/. Quando os scripts do setup forem atualizados, este
# script não precisa ser alterado, pois sempre usa os scripts mais recentes.
#
# Repositório: https://github.com/D3NKYT0/lineage
# Autor: Daniel Amaral
################################################################################

set -euo pipefail

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Diretórios
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SETUP_DIR="${SCRIPT_DIR}/setup"
readonly INSTALL_DIR="${SCRIPT_DIR}/.install_status"

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

# Preservar install.sh original para evitar problemas com git
# Esta função garante que o arquivo não seja modificado durante a execução
# Restaura o arquivo do repositório se houver mudanças (normalmente line endings)
preserve_install_sh() {
    local install_sh_path="${SCRIPT_DIR}/install.sh"
    if [ -f "$install_sh_path" ] && [ -d "${SCRIPT_DIR}/.git" ]; then
        # Verificar se há mudanças não commitadas no install.sh
        if ! git -C "${SCRIPT_DIR}" diff --quiet "$install_sh_path" 2>/dev/null; then
            # Há mudanças (provavelmente line endings), restaurar do git
            log_warning "Detectadas mudanças no install.sh (provavelmente line endings)."
            log_info "Restaurando do repositório para evitar conflitos com git pull..."
            if git -C "${SCRIPT_DIR}" checkout -- "$install_sh_path" 2>/dev/null; then
                chmod +x "$install_sh_path" 2>/dev/null || true
                log_success "install.sh restaurado."
            else
                log_warning "Não foi possível restaurar automaticamente. Execute: git checkout -- install.sh"
            fi
        fi
    fi
}

# Função para verificar se o comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para verificar se está rodando como root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_warning "⚠️  Executando como root detectado."
        log_info "Nota: Em servidores, é comum executar como root."
        log_info "O script continuará normalmente. Alguns comandos podem não precisar de sudo."
        echo
    fi
}

# Função para verificar pré-requisitos
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
    if ! command_exists git; then
        log_error "Git não está instalado. Por favor, instale o Git primeiro."
        exit 1
    fi
    
    if [ ! -d "${SETUP_DIR}" ]; then
        log_error "Pasta setup/ não encontrada!"
        log_info "Certifique-se de que você está executando este script na raiz do projeto."
        exit 1
    fi
    
    # Verificar se os scripts necessários existem
    local required_scripts=("setup.sh" "build.sh")
    for script in "${required_scripts[@]}"; do
        if [ ! -f "${SETUP_DIR}/${script}" ]; then
            log_error "Script necessário não encontrado: ${SETUP_DIR}/${script}"
            exit 1
        fi
    done
    
    log_success "Pré-requisitos verificados."
}

# Função para detectar versão do Ubuntu
detect_ubuntu_version() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [ "$ID" = "ubuntu" ]; then
            echo "$VERSION_CODENAME"
        else
            log_warning "Sistema não é Ubuntu. Algumas funcionalidades podem não funcionar."
            echo "unknown"
        fi
    else
        log_warning "Não foi possível detectar a versão do sistema."
        echo "unknown"
    fi
}

# Função para detectar instalações antigas (feitas com scripts anteriores)
detect_existing_installation() {
    local project_dir="${SCRIPT_DIR}"
    
    # Se já existe arquivo de status, é instalação nova
    if [ -f "${INSTALL_DIR}/.install_done" ]; then
        return 0  # Instalação detectada
    fi
    
    # Verificar se existe diretório de status com arquivos do script antigo
    # O script antigo criava: system_ready, docker_ready, repo_cloned, python_ready, env_created, htpasswd_created, fernet_key_generated, build_executed, superuser_created
    if [ -d "$INSTALL_DIR" ]; then
        local old_script_markers=("system_ready" "docker_ready" "repo_cloned" "python_ready" "env_created" "htpasswd_created" "fernet_key_generated" "build_executed" "superuser_created")
        for marker in "${old_script_markers[@]}"; do
            if [ -f "${INSTALL_DIR}/${marker}" ]; then
                log_info "Detectado arquivo de status do script antigo: ${marker}"
                log_info "Instalação antiga detectada (script anterior executado)."
                return 0  # Instalação detectada
            fi
        done
        
        # Se existe qualquer arquivo no diretório de status, considera instalado
        if [ "$(find "$INSTALL_DIR" -type f 2>/dev/null | wc -l)" -gt 0 ]; then
            log_info "Detectado diretório de status com arquivos (instalação antiga)."
            return 0  # Instalação detectada
        fi
    fi
    
    # Verificar se existe .env com ENCRYPTION_KEY configurada (não placeholder)
    local env_file="${project_dir}/.env"
    if [ -d "${project_dir}/lineage" ]; then
        env_file="${project_dir}/lineage/.env"
    fi
    
    if [ -f "$env_file" ]; then
        local encryption_key=$(grep -E "^ENCRYPTION_KEY\s*=" "$env_file" 2>/dev/null | head -1 | sed -E "s/^ENCRYPTION_KEY\s*=\s*['\"]?([^'\"]+)['\"]?.*$/\1/" | tr -d '[:space:]')
        local default_key="iOg0mMfE54rqvAOZKxhmb-Rq0sgmRC4p1TBGu_JqHac="
        
        # Se existe ENCRYPTION_KEY e não é a chave padrão/placeholder, é instalação antiga
        if [ -n "$encryption_key" ] && [ "$encryption_key" != "$default_key" ]; then
            log_info "Detectada ENCRYPTION_KEY existente no .env (instalação antiga)."
            return 0  # Instalação detectada
        fi
    fi
    
    # Verificar se existem containers Docker rodando
    if command_exists docker; then
        local running_containers=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -E "(site_http|site_wsgi|postgres|celery)" | wc -l)
        if [ "$running_containers" -gt 0 ]; then
            log_info "Detectados containers Docker rodando (instalação antiga)."
            return 0  # Instalação detectada
        fi
    fi
    
    # Verificar se existe manage.py (projeto configurado)
    if [ -f "${project_dir}/manage.py" ] || [ -f "${project_dir}/lineage/manage.py" ]; then
        # Se existe .env com variáveis importantes, considera instalado
        if [ -f "$env_file" ]; then
            local has_secret_key=$(grep -qE "^SECRET_KEY\s*=" "$env_file" 2>/dev/null && echo "yes" || echo "no")
            local has_db_config=$(grep -qE "^DB_ENGINE\s*=" "$env_file" 2>/dev/null && echo "yes" || echo "no")
            
            if [ "$has_secret_key" = "yes" ] && [ "$has_db_config" = "yes" ]; then
                log_info "Detectado projeto configurado com .env completo (instalação antiga)."
                return 0  # Instalação detectada
            fi
        fi
    fi
    
    # Verificar se existe diretório lineage com estrutura configurada (script antigo clonava para lineage/)
    if [ -d "${project_dir}/lineage" ]; then
        if [ -f "${project_dir}/lineage/manage.py" ] && [ -d "${project_dir}/lineage/.venv" ]; then
            log_info "Detectado projeto lineage com ambiente virtual configurado (instalação antiga)."
            return 0  # Instalação detectada
        fi
    fi
    
    return 1  # Não é instalação existente
}

# Função para preservar ENCRYPTION_KEY existente
preserve_encryption_key() {
    local env_file="${SCRIPT_DIR}/.env"
    
    # O script antigo clonava para lineage/, então verificar ambos os locais
    if [ ! -f "$env_file" ] && [ -d "${SCRIPT_DIR}/lineage" ]; then
        env_file="${SCRIPT_DIR}/lineage/.env"
    fi
    
    if [ ! -f "$env_file" ]; then
        return 0  # Sem .env, não precisa preservar
    fi
    
    # Extrair ENCRYPTION_KEY atual (se existir)
    local current_key=$(grep -E "^ENCRYPTION_KEY\s*=" "$env_file" 2>/dev/null | head -1 | sed -E "s/^ENCRYPTION_KEY\s*=\s*['\"]?([^'\"]+)['\"]?.*$/\1/" | tr -d '[:space:]')
    local default_key="iOg0mMfE54rqvAOZKxhmb-Rq0sgmRC4p1TBGu_JqHac="
    
    # Se existe chave e não é placeholder, preservar
    if [ -n "$current_key" ] && [ "$current_key" != "$default_key" ]; then
        log_warning "⚠️  ENCRYPTION_KEY existente detectada em: $env_file"
        log_warning "Chave: ${current_key:0:20}..."
        log_warning "Esta chave será preservada para manter dados criptografados."
        log_warning "⚠️  IMPORTANTE: Nenhum script sobrescreverá esta chave."
        
        # Criar arquivo de marcação para garantir que a chave não seja substituída
        mkdir -p "$INSTALL_DIR"
        echo "$current_key" > "${INSTALL_DIR}/.encryption_key_preserved"
        echo "$env_file" > "${INSTALL_DIR}/.encryption_key_location"
        return 0
    fi
    
    return 1  # Não há chave para preservar
}

# Função para restaurar ENCRYPTION_KEY preservada se foi modificada
restore_encryption_key() {
    local preserved_key_file="${INSTALL_DIR}/.encryption_key_preserved"
    local preserved_location_file="${INSTALL_DIR}/.encryption_key_location"
    
    # Se não há chave preservada, não precisa restaurar
    if [ ! -f "$preserved_key_file" ]; then
        return 0
    fi
    
    local preserved_key=$(cat "$preserved_key_file" | tr -d '[:space:]')
    if [ -z "$preserved_key" ]; then
        return 0  # Chave preservada vazia, não restaurar
    fi
    
    # Determinar localização do .env (onde estava originalmente ou onde deveria estar agora)
    local env_file="${SCRIPT_DIR}/.env"
    if [ -f "$preserved_location_file" ]; then
        local original_location=$(cat "$preserved_location_file")
        if [ -f "$original_location" ]; then
            env_file="$original_location"
        fi
    fi
    
    # Também verificar em lineage/.env (script antigo)
    if [ ! -f "$env_file" ] && [ -f "${SCRIPT_DIR}/lineage/.env" ]; then
        env_file="${SCRIPT_DIR}/lineage/.env"
    fi
    
    if [ ! -f "$env_file" ]; then
        return 0  # Arquivo .env não encontrado, não restaurar
    fi
    
    # Extrair ENCRYPTION_KEY atual do .env
    local current_key=$(grep -E "^ENCRYPTION_KEY\s*=" "$env_file" 2>/dev/null | head -1 | sed -E "s/^ENCRYPTION_KEY\s*=\s*['\"]?([^'\"]+)['\"]?.*$/\1/" | tr -d '[:space:]')
    local default_key="iOg0mMfE54rqvAOZKxhmb-Rq0sgmRC4p1TBGu_JqHac="
    
    # Se a chave atual é diferente da preservada (e não é apenas placeholder sendo substituída)
    if [ "$current_key" != "$preserved_key" ]; then
        # Se a chave preservada não é placeholder, restaurá-la
        if [ "$preserved_key" != "$default_key" ]; then
            log_warning "⚠️  ENCRYPTION_KEY foi modificada, restaurando chave preservada em: $env_file"
            
            # Fazer backup antes de restaurar
            if [ -f "$env_file" ]; then
                cp "$env_file" "${env_file}.before_key_restore.bkp" 2>/dev/null || true
            fi
            
            # Restaurar a chave preservada
            if grep -qE "^ENCRYPTION_KEY\s*=" "$env_file" 2>/dev/null; then
                # Substituir linha existente (suporta diferentes formatos)
                sed -i "s|^ENCRYPTION_KEY\s*=.*|ENCRYPTION_KEY = '$preserved_key'|" "$env_file" 2>/dev/null || \
                sed -i "s|^ENCRYPTION_KEY\s*=.*|ENCRYPTION_KEY='$preserved_key'|" "$env_file" 2>/dev/null || \
                sed -i "/^ENCRYPTION_KEY\s*=/c\ENCRYPTION_KEY='$preserved_key'" "$env_file" 2>/dev/null || true
            else
                # Adicionar se não existe
                echo "" >> "$env_file"
                echo "ENCRYPTION_KEY = '$preserved_key'" >> "$env_file"
            fi
            
            log_success "✓ ENCRYPTION_KEY restaurada com sucesso."
            log_warning "⚠️  Backup criado: ${env_file}.before_key_restore.bkp"
        fi
    else
        log_info "✓ ENCRYPTION_KEY preservada corretamente em: $env_file"
    fi
}

# Função para verificar se é um repositório git
is_git_repository() {
    [ -d "${SCRIPT_DIR}/.git" ]
}

# Função para atualizar repositório (git stash + git pull)
update_repository() {
    if ! is_git_repository; then
        log_error "Este diretório não é um repositório git."
        return 1
    fi
    
    log_info "Atualizando repositório..."
    
    cd "${SCRIPT_DIR}" || {
        log_error "Não foi possível acessar o diretório do script."
        return 1
    }
    
    # Verificar se há mudanças locais antes de fazer stash
    if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
        log_info "Fazendo stash das mudanças locais..."
        if git stash push -m "Stash automático antes de atualizar - $(date +%Y-%m-%d\ %H:%M:%S)"; then
            log_success "Mudanças locais salvas no stash."
        else
            log_warning "Falha ao fazer stash. Continuando mesmo assim..."
        fi
    else
        log_info "Nenhuma mudança local para fazer stash."
    fi
    
    # Fazer pull das atualizações
    log_info "Atualizando do repositório remoto..."
    if git pull; then
        log_success "Repositório atualizado com sucesso."
        return 0
    else
        log_error "Falha ao atualizar repositório."
        # Tentar restaurar stash se houve mudanças
        if git stash list | grep -q .; then
            log_info "Tentando restaurar mudanças do stash..."
            git stash pop >/dev/null 2>&1 || true
        fi
        return 1
    fi
}

# Função para clonar repositório se necessário
clone_repository() {
    # Verificar se estamos dentro de um repositório (manage.py na raiz ou em subdiretório)
    if [ -f "${SCRIPT_DIR}/manage.py" ] || [ -f "${SCRIPT_DIR}/lineage/manage.py" ] || [ -d "${SCRIPT_DIR}/.git" ]; then
        log_success "Repositório já existe."
        return 0
    fi
    
    log_info "Repositório não encontrado. Clonando do GitHub..."
    
    local repo_url="https://github.com/D3NKYT0/lineage.git"
    local clone_dir="${SCRIPT_DIR}/lineage"
    
    if [ -d "${clone_dir}" ]; then
        log_warning "Diretório ${clone_dir} já existe. Pulando clone."
        log_info "Se este é o repositório do projeto, você pode continuar."
    else
        git clone "${repo_url}" "${clone_dir}" || {
            log_error "Falha ao clonar repositório."
            exit 1
        }
        log_success "Repositório clonado com sucesso."
    fi
    
    # Verificar se o repositório foi clonado corretamente
    if [ -d "${clone_dir}" ] && [ -f "${clone_dir}/manage.py" ]; then
        log_success "Repositório encontrado em: ${clone_dir}"
        # Não sai mais aqui - permite continuar a instalação
    elif [ -d "${clone_dir}" ] && [ ! -f "${SCRIPT_DIR}/manage.py" ] && [ ! -f "${clone_dir}/manage.py" ]; then
        log_warning "Diretório ${clone_dir} existe mas não parece ser o repositório completo."
        log_info "Certifique-se de que está executando este script na raiz do projeto."
    fi
}

# Função para mostrar menu de scripts disponíveis
show_scripts_menu() {
    echo
    log_info "Scripts disponíveis na pasta setup/:"
    echo
    echo "  📦 setup.sh                - Instalação inicial completa (Docker, Python, etc.)"
    echo "  🔨 build.sh                - Build e deploy do projeto"
    echo "  💾 backup.sh               - Backup do banco de dados"
    echo "  🌐 nginx-proxy.sh           - Configurar proxy reverso com domínio"
    echo "  🔧 install-nginx.sh         - Instalar Nginx do repositório oficial"
    echo "  ⚙️  generate-env.sh         - Gerar arquivo .env interativamente"
    echo "  📁 setup-ftp.sh             - Configurar servidor FTP para launcher"
    echo "  🌐 setup-nginx-launcher.sh  - Configurar Nginx com index of para launcher"
    echo
}

# Função para executar script específico
run_setup_script() {
    local script_name="$1"
    local script_path="${SETUP_DIR}/${script_name}"
    
    if [ ! -f "$script_path" ]; then
        log_error "Script não encontrado: $script_path"
        return 1
    fi
    
    log_info "Executando: $script_name"
    log_info "=========================================="
    
    # Verificar se precisa de sudo
    case "$script_name" in
        nginx-proxy.sh|install-nginx.sh|setup-ftp.sh|setup-nginx-launcher.sh)
            if [ "$EUID" -ne 0 ]; then
                log_info "Este script requer privilégios de root."
                log_info "Executando com sudo..."
                sudo bash "$script_path" || {
                    log_error "Falha ao executar $script_name"
                    return 1
                }
            else
                bash "$script_path" || {
                    log_error "Falha ao executar $script_name"
                    return 1
                }
            fi
            ;;
        *)
            bash "$script_path" || {
                log_error "Falha ao executar $script_name"
                return 1
            }
            ;;
    esac
    
    log_success "Script $script_name executado com sucesso."
}

# Função principal de instalação
main() {
    local action="${1:-install}"
    
    # Preservar install.sh ANTES de qualquer coisa para evitar problemas com git
    preserve_install_sh
    
    clear
    
    echo "========================================================="
    echo "  🚀 Painel Definitivo Lineage (PDL) - Instalador"
    echo "========================================================="
    echo
    
    case "$action" in
        install|"")
            echo "Este script irá:"
            echo "  1. Verificar pré-requisitos"
            echo "  2. Executar setup.sh (instalação inicial + build e deploy)"
            echo
            echo "Repositório: https://github.com/D3NKYT0/lineage"
            echo
            ;;
        menu)
            show_scripts_menu
            echo
            log_info "Escolha uma opção:"
            echo "  1) Instalação completa (setup.sh + build.sh)"
            echo "  2) Apenas setup.sh"
            echo "  3) Apenas build.sh"
            if is_git_repository; then
                echo "  4) Atualizar repositório (git pull)"
                echo "  5) Backup do banco de dados"
                echo "  6) Configurar proxy reverso (nginx-proxy)"
                echo "  7) Instalar Nginx (install-nginx)"
                echo "  8) Gerar arquivo .env (generate-env)"
                echo "  9) Configurar FTP para launcher (setup-ftp)"
                echo "  10) Configurar Nginx para launcher (setup-nginx-launcher)"
                echo "  11) Listar scripts disponíveis"
                echo "  12) Sair"
                echo
                read -p "Opção: " menu_option
                
                case "$menu_option" in
                    1) action="install" ;;
                    2) action="setup" ;;
                    3) action="build" ;;
                    4) action="update" ;;
                    5) action="backup" ;;
                    6) action="nginx-proxy" ;;
                    7) action="install-nginx" ;;
                    8) action="generate-env" ;;
                    9) action="setup-ftp" ;;
                    10) action="setup-nginx-launcher" ;;
                    11) show_scripts_menu; exit 0 ;;
                    12) exit 0 ;;
                    *) log_error "Opção inválida."; exit 1 ;;
                esac
            else
                echo "  4) Backup do banco de dados"
                echo "  5) Configurar proxy reverso (nginx-proxy)"
                echo "  6) Instalar Nginx (install-nginx)"
                echo "  7) Gerar arquivo .env (generate-env)"
                echo "  8) Configurar FTP para launcher (setup-ftp)"
                echo "  9) Configurar Nginx para launcher (setup-nginx-launcher)"
                echo "  10) Listar scripts disponíveis"
                echo "  11) Sair"
                echo
                read -p "Opção: " menu_option
                
                case "$menu_option" in
                    1) action="install" ;;
                    2) action="setup" ;;
                    3) action="build" ;;
                    4) action="backup" ;;
                    5) action="nginx-proxy" ;;
                    6) action="install-nginx" ;;
                    7) action="generate-env" ;;
                    8) action="setup-ftp" ;;
                    9) action="setup-nginx-launcher" ;;
                    10) show_scripts_menu; exit 0 ;;
                    11) exit 0 ;;
                    *) log_error "Opção inválida."; exit 1 ;;
                esac
            fi
            ;;
        setup)
            log_info "Executando apenas setup.sh..."
            check_root
            check_prerequisites
            clone_repository
            cd "${SCRIPT_DIR}"
            run_setup_script "setup.sh"
            exit 0
            ;;
        build)
            log_info "Executando apenas build.sh..."
            if [ ! -d "${SETUP_DIR}" ]; then
                log_error "Pasta setup/ não encontrada!"
                exit 1
            fi
            cd "${SCRIPT_DIR}"
            run_setup_script "build.sh"
            exit 0
            ;;
        update)
            log_info "Atualizando repositório..."
            if ! is_git_repository; then
                log_error "Este diretório não é um repositório git."
                exit 1
            fi
            if update_repository; then
                log_success "Repositório atualizado com sucesso!"
            else
                log_error "Falha ao atualizar repositório."
                exit 1
            fi
            exit 0
            ;;
        backup)
            log_info "Executando backup.sh..."
            if [ ! -d "${SETUP_DIR}" ]; then
                log_error "Pasta setup/ não encontrada!"
                exit 1
            fi
            cd "${SCRIPT_DIR}"
            run_setup_script "backup.sh" "${@:2}"
            exit 0
            ;;
        nginx-proxy)
            log_info "Executando nginx-proxy.sh..."
            if [ ! -d "${SETUP_DIR}" ]; then
                log_error "Pasta setup/ não encontrada!"
                exit 1
            fi
            cd "${SCRIPT_DIR}"
            run_setup_script "nginx-proxy.sh"
            exit 0
            ;;
        install-nginx)
            log_info "Executando install-nginx.sh..."
            if [ ! -d "${SETUP_DIR}" ]; then
                log_error "Pasta setup/ não encontrada!"
                exit 1
            fi
            cd "${SCRIPT_DIR}"
            run_setup_script "install-nginx.sh" "${@:2}"
            exit 0
            ;;
        generate-env)
            log_info "Executando generate-env.sh..."
            if [ ! -d "${SETUP_DIR}" ]; then
                log_error "Pasta setup/ não encontrada!"
                exit 1
            fi
            cd "${SCRIPT_DIR}"
            run_setup_script "generate-env.sh"
            exit 0
            ;;
        setup-ftp)
            log_info "Executando setup-ftp.sh..."
            if [ ! -d "${SETUP_DIR}" ]; then
                log_error "Pasta setup/ não encontrada!"
                exit 1
            fi
            cd "${SCRIPT_DIR}"
            run_setup_script "setup-ftp.sh"
            exit 0
            ;;
        setup-nginx-launcher)
            log_info "Executando setup-nginx-launcher.sh..."
            if [ ! -d "${SETUP_DIR}" ]; then
                log_error "Pasta setup/ não encontrada!"
                exit 1
            fi
            cd "${SCRIPT_DIR}"
            run_setup_script "setup-nginx-launcher.sh"
            exit 0
            ;;
        list|scripts)
            show_scripts_menu
            exit 0
            ;;
        help|--help|-h)
            echo "Uso: $0 [comando]"
            echo
            echo "Comandos:"
            echo "  install          - Instalação completa (setup.sh + build.sh) [padrão]"
            echo "  menu             - Menu interativo para escolher script"
            echo "  setup            - Executar apenas setup.sh"
            echo "  build            - Executar apenas build.sh"
            echo "  update           - Atualizar repositório (git stash + git pull)"
            echo "  backup [args]         - Executar backup.sh (aceita argumentos: list, restore)"
            echo "  nginx-proxy           - Configurar proxy reverso"
            echo "  install-nginx         - Instalar Nginx (aceita: stable, mainline)"
            echo "  generate-env          - Gerar arquivo .env interativamente"
            echo "  setup-ftp             - Configurar servidor FTP para launcher"
            echo "  setup-nginx-launcher  - Configurar Nginx com index of para launcher"
            echo "  list                  - Listar todos os scripts disponíveis"
            echo "  help                  - Mostrar esta ajuda"
            echo
            echo "Exemplos:"
            echo "  $0                    # Instalação completa"
            echo "  $0 menu                # Menu interativo"
            echo "  $0 update              # Atualizar repositório"
            echo "  $0 backup list         # Listar backups"
            echo "  $0 install-nginx stable  # Instalar Nginx stable"
            echo
            exit 0
            ;;
        *)
            log_error "Comando desconhecido: $action"
            echo "Use '$0 help' para ver os comandos disponíveis."
            exit 1
            ;;
    esac
    
    # Continuar com instalação completa se action ainda for "install"
    if [ "$action" = "install" ]; then
        # Verificar se está rodando como root (apenas aviso, não bloqueia)
        check_root
    
        # Verificar pré-requisitos
        check_prerequisites
        
        # Detectar versão do Ubuntu
        local ubuntu_version
        ubuntu_version=$(detect_ubuntu_version)
        log_info "Versão detectada: ${ubuntu_version}"
        
        # Clonar repositório se necessário
        clone_repository
        
        # Criar diretório de status
        mkdir -p "${INSTALL_DIR}"
        
        # Preservar ENCRYPTION_KEY ANTES de qualquer verificação
        log_info "Verificando instalações existentes e preservando configurações..."
        preserve_encryption_key || true  # Continua mesmo se não encontrar chave
        
        # Verificar se já foi instalado (incluindo instalações antigas)
        local is_existing=false
        if detect_existing_installation || [ -f "${INSTALL_DIR}/.install_done" ]; then
            is_existing=true
        fi
        
        if [ "$is_existing" = "true" ]; then
            log_warning "⚠️  Instalação existente detectada!"
            log_info "Foi detectado que o sistema já foi instalado anteriormente."
            echo
            
            # Verificar se ENCRYPTION_KEY está preservada
            if [ -f "${INSTALL_DIR}/.encryption_key_preserved" ]; then
                log_success "✓ ENCRYPTION_KEY será preservada (dados criptografados serão mantidos)."
            fi
            
            echo
            log_info "O que deseja fazer?"
            echo "  (b) Rodar apenas build (atualizar código sem reinstalar)"
            echo "  (r) Refazer instalação completa (ATENÇÃO: pode sobrescrever configurações)"
            echo "  (s) Sair"
            echo
            read -p "Escolha (b/r/s): " OPCAO </dev/tty || read OPCAO
            
            case "${OPCAO}" in
                b|B)
                    log_info "Executando apenas build.sh..."
                    cd "${SCRIPT_DIR}"
                    bash "${SETUP_DIR}/build.sh"
                    exit 0
                    ;;
                r|R)
                    log_warning "⚠️  ATENÇÃO: Você escolheu refazer a instalação completa."
                    log_warning "Isso pode sobrescrever configurações existentes."
                    echo
                    read -p "Tem CERTEZA que deseja continuar? (digite 'SIM' para confirmar): " CONFIRM
                    if [ "$CONFIRM" != "SIM" ]; then
                        log_info "Operação cancelada."
                        exit 0
                    fi
                    log_info "Refazendo instalação completa..."
                    # NÃO remover o arquivo de preservação da chave se existir
                    if [ -f "${INSTALL_DIR}/.encryption_key_preserved" ]; then
                        local preserved_key=$(cat "${INSTALL_DIR}/.encryption_key_preserved")
                        rm -rf "${INSTALL_DIR}"
                        mkdir -p "${INSTALL_DIR}"
                        echo "$preserved_key" > "${INSTALL_DIR}/.encryption_key_preserved"
                        log_info "ENCRYPTION_KEY preservada mesmo com reinstalação."
                    else
                        rm -rf "${INSTALL_DIR}"
                        mkdir -p "${INSTALL_DIR}"
                    fi
                    ;;
                s|S)
                    log_info "Saindo..."
                    exit 0
                    ;;
                *)
                    log_error "Opção inválida."
                    exit 1
                    ;;
            esac
        fi
        
        # Confirmar instalação
        echo
        read -p "Deseja continuar com a instalação? (s/n): " CONTINUE
        
        if [[ ! "${CONTINUE}" =~ ^[sS]$ ]]; then
            log_info "Instalação cancelada."
            exit 0
        fi
        
        # Executar setup.sh (que já executa build.sh internamente)
        log_info "Executando setup.sh..."
        log_info "=========================================="
        cd "${SCRIPT_DIR}"
        run_setup_script "setup.sh"
        
        # Restaurar ENCRYPTION_KEY preservada se necessário (proteção contra sobrescrita)
        restore_encryption_key
        
        # Marcar instalação como concluída
        touch "${INSTALL_DIR}/.install_done"
        
        echo
        log_success "Instalação concluída com sucesso!"
        echo
        log_info "Próximos passos:"
        echo "  - Acesse: http://localhost:6085"
        echo "  - Para atualizar: bash setup/build.sh"
        echo "  - Para parar: docker compose down"
        echo
        log_info "Scripts adicionais disponíveis:"
        echo "  - Backup: $0 backup [list|restore]"
        echo "  - Proxy reverso: $0 nginx-proxy"
        echo "  - Instalar Nginx: $0 install-nginx [stable|mainline]"
        echo "  - Configurar FTP: $0 setup-ftp"
        echo "  - Configurar Nginx Launcher: $0 setup-nginx-launcher"
        echo
        log_info "Para ver todos os scripts: $0 list"
        echo
    fi
}

# Executar função principal
main "$@"

