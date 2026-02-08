#!/bin/bash

################################################################################
# Script de Setup do Painel Definitivo Lineage (PDL)
# 
# Este script prepara o ambiente completo para o PDL, incluindo:
# - Instalação de dependências do sistema
# - Instalação do Docker e Docker Compose
# - Configuração do ambiente Python
# - Criação de arquivos de configuração
################################################################################

set -euo pipefail

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
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

# Função para criar backup do .env antes de modificações
backup_env_file() {
    local env_file="${1:-.env}"
    
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

# Função para verificar se .env está completo
check_env_complete() {
    local env_file="$1"
    local required_vars=(
        "DEBUG"
        "SECRET_KEY"
        "DB_ENGINE"
        "ENCRYPTION_KEY"
        "RENDER_EXTERNAL_HOSTNAME"
        "CONFIG_HCAPTCHA_SITE_KEY"
        "CONFIG_LANGUAGE_CODE"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$env_file" 2>/dev/null; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        return 1  # Incompleto
    fi
    
    return 0  # Completo
}

INSTALL_DIR="$(pwd)/.install_status"
mkdir -p "$INSTALL_DIR"

clear

echo "========================================================="
echo "  🚀 Bem-vindo ao Instalador do Projeto Lineage 2 PDL!   "
echo "========================================================="
echo

# Detect Ubuntu version
UBUNTU_VERSION=$(lsb_release -cs)
echo "📦 Detectada versão do Ubuntu: $UBUNTU_VERSION"

# Set Docker Compose command based on Ubuntu version
if [ "$UBUNTU_VERSION" = "focal" ]; then
  DOCKER_COMPOSE="docker-compose"
else
  DOCKER_COMPOSE="docker compose"
fi

# Map Ubuntu versions to Docker repository versions
case $UBUNTU_VERSION in
  "focal")
    DOCKER_REPO="focal"
    ;;
  "jammy")
    DOCKER_REPO="jammy"
    ;;
  "noble")
    DOCKER_REPO="jammy"  # Ubuntu 24.04 uses jammy repository for now
    ;;
  *)
    echo "❌ Versão do Ubuntu não suportada: $UBUNTU_VERSION"
    echo "Por favor, use Ubuntu 20.04 (Focal), 22.04 (Jammy) ou 24.04 (Noble)"
    exit 1
    ;;
esac

if [ -f "$INSTALL_DIR/.install_done" ]; then
  echo "⚠️  Instalação já foi concluída anteriormente."
  echo
  read -p "Deseja rodar os containers (s) ou refazer a instalação (r)? (s/r): " OPCAO

  if [[ "$OPCAO" == "s" || "$OPCAO" == "S" ]]; then
    pushd lineage > /dev/null
    $DOCKER_COMPOSE up -d
    popd > /dev/null
    echo "✅ Containers iniciados."
    exit 0
  elif [[ "$OPCAO" == "r" || "$OPCAO" == "R" ]]; then
    echo "🔄 Refazendo instalação..."
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
  else
    echo "❌ Opção inválida."
    exit 1
  fi
fi

echo "Este script vai preparar todo o ambiente para você."
echo
read -p "Deseja continuar com a instalação? (s/n): " CONTINUE

if [[ "$CONTINUE" != "s" && "$CONTINUE" != "S" ]]; then
  echo "Instalação cancelada."
  exit 0
fi

if ! command -v git &> /dev/null; then
  echo "❌ Git não está instalado. Instalando..."
  sudo apt install -y git
fi

if [ ! -f "$INSTALL_DIR/system_ready" ]; then
  echo
  echo "🔄 Atualizando pacotes e instalando dependências..."
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y software-properties-common
  sudo add-apt-repository -y ppa:deadsnakes/ppa
  sudo apt update
  
  # Verificar versão atual do Python
  SYSTEM_PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' 2>/dev/null || echo "0.0.0")
  PYTHON_MAJOR=$(echo "$SYSTEM_PYTHON_VERSION" | cut -d. -f1)
  PYTHON_MINOR=$(echo "$SYSTEM_PYTHON_VERSION" | cut -d. -f2)
  
  echo "Python atual detectado: $SYSTEM_PYTHON_VERSION"
  
  # Verificar se Python é menor que 3.11 ou instalar Python 3.13 de qualquer forma para garantir
  INSTALL_PYTHON313=true
  if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "Python $SYSTEM_PYTHON_VERSION é menor que 3.11 (requerido para autobahn==25.11.1)"
    echo "Instalando Python 3.13..."
  else
    echo "Python $SYSTEM_PYTHON_VERSION atende aos requisitos, mas instalando Python 3.13 para garantir compatibilidade..."
  fi
  
  sudo apt install -y python3.13 python3.13-venv python3.13-dev
  sudo apt install -y apt-transport-https ca-certificates curl gettext
  
  # Instalar bcrypt e passlib no Python do sistema para uso em scripts
  echo "📦 Instalando bcrypt e passlib no Python do sistema..."
  # Instalar bcrypt (versão mais recente) e passlib como fallback
  python3 -m pip install --user --break-system-packages bcrypt "passlib==1.7.4" 2>/dev/null || \
  python3 -m pip install --user bcrypt "passlib==1.7.4" 2>/dev/null || \
  sudo python3 -m pip install bcrypt "passlib==1.7.4" 2>/dev/null || true
  
  # Instalar htpasswd do sistema como alternativa
  sudo apt install -y apache2-utils 2>/dev/null || true
  
  if python3 -c "import bcrypt" 2>/dev/null || python3 -c "import passlib" 2>/dev/null; then
    echo "✅ bcrypt/passlib instalado no Python do sistema"
  else
    echo "⚠️  Não foi possível instalar bcrypt/passlib no Python do sistema (será instalado no venv ou usado htpasswd)"
  fi
  
  # NÃO configurar Python 3.13 como padrão do sistema
  # O sistema operacional deve continuar usando Python 3.10 (ou 3.11) para ferramentas do sistema
  # Python 3.13 será usado apenas explicitamente no virtual environment do projeto
  
  # Garantir que Python 3.10 (ou versão do sistema) continue como padrão
  SYSTEM_PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' 2>/dev/null || echo "")
  SYSTEM_PYTHON_MAJOR=$(echo "$SYSTEM_PYTHON_VERSION" | cut -d. -f1)
  SYSTEM_PYTHON_MINOR=$(echo "$SYSTEM_PYTHON_VERSION" | cut -d. -f2)
  
  # Se Python 3.13 foi configurado como padrão anteriormente, reverter
  if [ "$SYSTEM_PYTHON_MAJOR" = "3" ] && [ "$SYSTEM_PYTHON_MINOR" = "13" ]; then
    echo "⚠️  Python 3.13 está configurado como padrão do sistema"
    echo "Revertendo para Python do sistema (3.10/3.11) para manter compatibilidade com ferramentas do sistema..."
    
    # Encontrar Python do sistema (3.10 ou 3.11)
    SYSTEM_PYTHON_ORIGINAL=$(ls -1 /usr/bin/python3.* 2>/dev/null | grep -E "python3\.(10|11)" | head -1 | xargs basename 2>/dev/null || echo "python3.10")
    
    if [ -f "/usr/bin/$SYSTEM_PYTHON_ORIGINAL" ]; then
      if command -v update-alternatives &> /dev/null; then
        # Adicionar Python do sistema como alternativa se não existir
        sudo update-alternatives --install /usr/bin/python3 python3 "/usr/bin/$SYSTEM_PYTHON_ORIGINAL" 10 2>/dev/null || true
        # Configurar Python do sistema como padrão
        sudo update-alternatives --set python3 "/usr/bin/$SYSTEM_PYTHON_ORIGINAL" 2>/dev/null || true
        echo "✅ Python do sistema ($SYSTEM_PYTHON_ORIGINAL) configurado como padrão"
      else
        # Se update-alternatives não estiver disponível, criar symlink direto
        sudo ln -sf "/usr/bin/$SYSTEM_PYTHON_ORIGINAL" /usr/bin/python3 2>/dev/null || true
        echo "✅ Python do sistema ($SYSTEM_PYTHON_ORIGINAL) configurado como padrão via symlink"
      fi
    fi
  fi
  
  # Verificar versão final do Python padrão
  FINAL_PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' 2>/dev/null || echo "desconhecida")
  echo "ℹ️  Python padrão do sistema: $FINAL_PYTHON_VERSION (para ferramentas do sistema)"
  echo "ℹ️  Python 3.13 instalado e disponível via 'python3.13' (será usado no virtual environment do projeto)"
  
  touch "$INSTALL_DIR/system_ready"
fi

if [ ! -f "$INSTALL_DIR/docker_ready" ]; then
  echo
  echo "🐳 Instalando Docker e Docker Compose..."
  
  # Remove old versions if they exist
  sudo apt remove -y docker docker-engine docker.io containerd runc || true
  
  # Install prerequisites
  sudo apt update
  sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

  if [ "$UBUNTU_VERSION" = "focal" ]; then
    echo "📦 Instalando Docker do repositório do Ubuntu para Ubuntu 20.04..."
    sudo apt install -y docker.io
  else
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $DOCKER_REPO stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Update package index
    sudo apt update

    # Install Docker Engine
    sudo apt install -y docker-ce docker-ce-cli containerd.io
  fi

  # Start and enable Docker
  sudo systemctl start docker
  sudo systemctl enable docker

  # Verify installation
  if ! docker info &> /dev/null; then
    echo "❌ Docker não está rodando corretamente. Verifique a instalação."
    exit 1
  fi

  # Install Docker Compose
  if ! $DOCKER_COMPOSE version &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instalando..."
    if [ "$UBUNTU_VERSION" = "focal" ]; then
      echo "📦 Instalando Docker Compose standalone para Ubuntu 20.04..."
      sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      sudo chmod +x /usr/local/bin/docker-compose
      sudo rm -f /usr/bin/docker-compose
      sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
      $DOCKER_COMPOSE --version
    else
      echo "📦 Instalando Docker Compose plugin para Ubuntu 22.04/24.04..."
      sudo apt-get update
      sudo apt-get install -y docker-compose-plugin
      $DOCKER_COMPOSE version
    fi
  else
    $DOCKER_COMPOSE version
  fi

  touch "$INSTALL_DIR/docker_ready"
fi

if [ ! -f "$INSTALL_DIR/repo_cloned" ]; then
  echo
  log_info "📂 Verificando repositório do projeto..."
  
  # Se já estamos dentro do repositório (manage.py existe), não precisa clonar
  if [ -f "manage.py" ]; then
    log_success "Repositório já está presente (manage.py encontrado)."
    touch "$INSTALL_DIR/repo_cloned"
  elif [ -d "lineage" ] && [ -f "lineage/manage.py" ]; then
    log_info "Repositório encontrado em subdiretório 'lineage'."
    touch "$INSTALL_DIR/repo_cloned"
  else
    log_info "Clonando repositório do projeto..."
    git clone https://github.com/D3NKYT0/lineage.git || {
      log_error "Falha ao clonar repositório."
      log_info "Certifique-se de que o Git está instalado e você tem acesso à internet."
      exit 1
    }
    log_success "Repositório clonado com sucesso."
    touch "$INSTALL_DIR/repo_cloned"
  fi
fi

# Entrar no diretório do projeto se necessário
if [ -d "lineage" ] && [ -f "lineage/manage.py" ] && [ ! -f "manage.py" ]; then
  pushd lineage > /dev/null
elif [ -f "manage.py" ]; then
  # Já estamos no diretório correto
  :
else
  log_error "Não foi possível encontrar o diretório do projeto."
  exit 1
fi

if [ ! -f "$INSTALL_DIR/python_ready" ]; then
  echo
  echo "🐍 Configurando ambiente Python (virtualenv)..."
  
  # Verificar se python3.13 está disponível, caso contrário usar python3
  if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
  else
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
      echo "❌ Python $PYTHON_VERSION é menor que 3.11 e Python 3.13 não está disponível."
      echo "Execute o script novamente para instalar Python 3.13."
      exit 1
    fi
  fi
  
  $PYTHON_CMD -m venv .venv
  source .venv/bin/activate
  
  # Verificar versão do Python no venv
  VENV_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
  echo "Python no venv: $VENV_PYTHON_VERSION"
  
  pip install --upgrade pip
  pip install --upgrade setuptools wheel

  # Modificar requirements.txt para incluir o repositório do GitHub
  echo "📦 Atualizando requirements.txt..."
  
  # Verificar se o arquivo já está correto (UTF-8, sem caracteres nulos, tem o repositório do GitHub)
  NEEDS_CLEANUP=false
  HAS_GITHUB_REPO=false
  
  if [ -f "requirements.txt" ]; then
    # Verificar se tem caracteres nulos (UTF-16) - ler primeiros bytes
    if python3 -c "with open('requirements.txt', 'rb') as f: data=f.read(1000); exit(0 if b'\x00' in data else 1)" 2>/dev/null; then
      NEEDS_CLEANUP=true
      echo "⚠️  Detectado encoding UTF-16 ou caracteres inválidos, será necessário limpar o arquivo"
    fi
    
    # Verificar se já tem o repositório do GitHub
    if grep -q "git+https://github.com/D3NKYT0/django-encrypted-fields.git" requirements.txt 2>/dev/null; then
      HAS_GITHUB_REPO=true
    fi
    
    # Verificar se tem django-encrypted-fields-and-files (precisa remover)
    if grep -q "django-encrypted-fields-and-files" requirements.txt 2>/dev/null; then
      NEEDS_CLEANUP=true
      echo "ℹ️  Precisa remover django-encrypted-fields-and-files e adicionar repositório do GitHub"
    fi
  fi
  
  # Se não precisa limpar e já tem o repositório, apenas pular
  if [ "$NEEDS_CLEANUP" = "false" ] && [ "$HAS_GITHUB_REPO" = "true" ]; then
    echo "✅ requirements.txt já está atualizado, não é necessário modificar"
  else
    # Precisa limpar ou adicionar repositório
    # Fazer backup do requirements.txt original
    if [ ! -f "requirements.txt.bak" ]; then
      cp requirements.txt requirements.txt.bak 2>/dev/null || true
    fi
    
    if [ "$NEEDS_CLEANUP" = "true" ]; then
  
  # Limpar o arquivo usando Python para garantir encoding correto
  python3 << 'PYTHON_CLEAN'
import sys
import re

def detect_encoding(file_path):
    """Detecta o encoding do arquivo"""
    encodings = ['utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'latin-1', 'cp1252']
    
    # Verificar BOM (Byte Order Mark)
    try:
        with open(file_path, 'rb') as f:
            bom = f.read(4)
            if bom.startswith(b'\xff\xfe'):
                return 'utf-16le'
            elif bom.startswith(b'\xfe\xff'):
                return 'utf-16be'
            elif bom.startswith(b'\xef\xbb\xbf'):
                return 'utf-8-sig'
    except:
        pass
    
    # Tentar cada encoding
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return 'utf-8'  # fallback

def clean_line(line):
    """Remove caracteres nulos e normaliza a linha"""
    # Remover caracteres nulos (\x00)
    line = line.replace('\x00', '')
    # Remover BOM se presente
    if line.startswith('\ufeff'):
        line = line[1:]
    return line.strip()

def is_valid_requirement_line(line):
    """Verifica se a linha é válida para requirements.txt"""
    line = clean_line(line)
    if not line:  # Linha vazia é válida (mas vamos remover no final)
        return True
    # Linha válida deve começar com letra, número, #, -, git+, ou http
    if re.match(r'^[a-zA-Z0-9#\-]|^git\+|^http', line):
        # Verificar se não contém caracteres de controle inválidos (exceto \n, \r, \t)
        if all(ord(c) >= 32 or c in '\n\r\t' for c in line):
            return True
    return False

try:
    # Detectar encoding do arquivo
    detected_encoding = detect_encoding('requirements.txt')
    
    # Ler arquivo com encoding detectado
    try:
        with open('requirements.txt', 'r', encoding=detected_encoding) as f:
            raw_content = f.read()
    except Exception as e:
        # Se falhar, tentar com errors='replace' para substituir caracteres inválidos
        with open('requirements.txt', 'r', encoding=detected_encoding, errors='replace') as f:
            raw_content = f.read()
    
    # Dividir em linhas e limpar
    lines = raw_content.splitlines()
    
    # Filtrar e limpar linhas válidas
    valid_lines = []
    for line in lines:
        cleaned_line = clean_line(line)
        if is_valid_requirement_line(cleaned_line):
            valid_lines.append(cleaned_line)
    
    # Remover django-encrypted-fields-and-files se existir
    valid_lines = [l for l in valid_lines if 'django-encrypted-fields-and-files' not in l]
    
    # Remover linhas vazias no final
    while valid_lines and not valid_lines[-1].strip():
        valid_lines.pop()
    
    # Adicionar linha vazia e o repositório do GitHub se não estiver presente
    github_repo = "git+https://github.com/D3NKYT0/django-encrypted-fields.git"
    if github_repo not in valid_lines:
        valid_lines.append("")
        valid_lines.append(github_repo)
    
    # Escrever arquivo limpo em UTF-8
    with open('requirements.txt', 'w', encoding='utf-8', newline='\n') as f:
        for line in valid_lines:
            f.write(line + '\n')
    
    print(f"✅ requirements.txt limpo e atualizado ({len(valid_lines)} linhas válidas, encoding convertido de {detected_encoding} para UTF-8)")
    sys.exit(0)
except Exception as e:
    print(f"❌ Erro ao limpar requirements.txt: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_CLEAN
  
    if [ $? -ne 0 ]; then
    log_warning "Falha ao limpar requirements.txt com Python, tentando método alternativo..."
    
    # Método alternativo: converter encoding e limpar
    if [ -f "requirements.txt.bak" ]; then
      # Tentar converter de UTF-16 para UTF-8 usando iconv (se disponível)
      if command -v iconv &> /dev/null; then
        # Tentar UTF-16LE primeiro (mais comum no Windows)
        iconv -f UTF-16LE -t UTF-8 requirements.txt.bak 2>/dev/null | \
          tr -d '\x00' > requirements.txt.clean 2>/dev/null || \
        iconv -f UTF-16 -t UTF-8 requirements.txt.bak 2>/dev/null | \
          tr -d '\x00' > requirements.txt.clean 2>/dev/null || true
      fi
      
      # Se iconv não funcionou ou não está disponível, usar tr para remover \x00
      if [ ! -f "requirements.txt.clean" ] || [ ! -s "requirements.txt.clean" ]; then
        tr -d '\x00' < requirements.txt.bak > requirements.txt.clean 2>/dev/null || true
      fi
      
      # Filtrar linhas válidas
      if [ -f "requirements.txt.clean" ] && [ -s "requirements.txt.clean" ]; then
        # Manter apenas linhas que começam com caracteres válidos
        grep -E '^[a-zA-Z0-9#\-]|^git\+|^http' requirements.txt.clean | \
          grep -v 'django-encrypted-fields-and-files' > requirements.txt.tmp 2>/dev/null || true
        
        if [ -f "requirements.txt.tmp" ] && [ -s "requirements.txt.tmp" ]; then
          mv requirements.txt.tmp requirements.txt
          echo "" >> requirements.txt
          echo "git+https://github.com/D3NKYT0/django-encrypted-fields.git" >> requirements.txt
          log_info "requirements.txt limpo usando método alternativo (encoding convertido)"
        else
          log_error "Não foi possível extrair linhas válidas do requirements.txt"
          exit 1
        fi
      else
        log_error "Não foi possível converter encoding do requirements.txt"
        exit 1
      fi
    else
      log_error "Backup do requirements.txt não encontrado"
      exit 1
    fi
    fi
    else
      # Não precisa limpar, apenas adicionar repositório do GitHub se não estiver presente
      if [ "$HAS_GITHUB_REPO" = "false" ]; then
        echo "ℹ️  Adicionando repositório do GitHub ao requirements.txt..."
        # Remover django-encrypted-fields-and-files se existir
        sed -i '/django-encrypted-fields-and-files/d' requirements.txt 2>/dev/null || true
        # Adicionar repositório do GitHub no final
        echo "" >> requirements.txt
        echo "git+https://github.com/D3NKYT0/django-encrypted-fields.git" >> requirements.txt
        echo "✅ Repositório do GitHub adicionado ao requirements.txt"
      fi
    fi
  fi

  # Instalar dependências
  echo "📦 Instalando dependências Python..."
  pip install -r requirements.txt

  # Criar diretórios necessários
  echo "📁 Criando diretórios necessários..."
  mkdir -p logs
  mkdir -p themes
  touch "$INSTALL_DIR/python_ready"
else
  # Verificar se o venv existe e se o Python é >= 3.11
  if [ -d ".venv" ]; then
    source .venv/bin/activate
    
    # Verificar versão do Python no venv
    VENV_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' 2>/dev/null || echo "0.0.0")
    VENV_MAJOR=$(echo "$VENV_PYTHON_VERSION" | cut -d. -f1)
    VENV_MINOR=$(echo "$VENV_PYTHON_VERSION" | cut -d. -f2)
    
    if [ "$VENV_MAJOR" -lt 3 ] || ([ "$VENV_MAJOR" -eq 3 ] && [ "$VENV_MINOR" -lt 11 ]); then
      echo "⚠️  Python no venv ($VENV_PYTHON_VERSION) é menor que 3.11"
      echo "Removendo venv antigo e recriando com Python 3.13..."
      deactivate 2>/dev/null || true
      rm -rf .venv
      
      if command -v python3.13 &> /dev/null; then
        python3.13 -m venv .venv
        source .venv/bin/activate
        echo "✅ Virtual environment recriado com Python 3.13"
      else
        echo "❌ Python 3.13 não encontrado. Execute o script novamente para instalar."
        exit 1
      fi
    fi
  else
    # Se não existe venv, criar com Python 3.13
    if command -v python3.13 &> /dev/null; then
      python3.13 -m venv .venv
      source .venv/bin/activate
    else
      python3 -m venv .venv
      source .venv/bin/activate
    fi
  fi
fi

if [ ! -f "$INSTALL_DIR/env_created" ]; then
  echo
  log_info "⚙️ Criando arquivo .env..."
  if [ ! -f ".env" ]; then
    log_info "Executando script de geração do .env..."
    if [ -f "setup/generate-env.sh" ]; then
      bash setup/generate-env.sh || {
        log_error "Falha ao gerar arquivo .env"
        log_info "Você pode executar manualmente depois com: bash setup/generate-env.sh"
        exit 1
      }
    else
      log_error "Script setup/generate-env.sh não encontrado!"
      exit 1
    fi
  else
    log_warning "Arquivo .env já existe. Verificando se está completo..."
    
    # Verificar se o .env está completo
    if ! check_env_complete ".env"; then
      log_warning "O arquivo .env parece estar incompleto (faltam variáveis obrigatórias)."
      echo
      read -p "Deseja executar o script generate-env.sh para completar o .env? (s/n): " EXEC_GENERATE
      if [[ "$EXEC_GENERATE" =~ ^[sS]$ ]]; then
        log_info "Executando script de geração do .env..."
        if [ -f "setup/generate-env.sh" ]; then
          # Fazer backup do .env existente antes de executar generate-env.sh
          backup_env_file ".env"
          
          # Executar generate-env.sh (ele vai perguntar se quer sobrescrever)
          bash setup/generate-env.sh || {
            log_error "Falha ao gerar arquivo .env"
            log_info "Você pode executar manualmente depois com: bash setup/generate-env.sh"
            exit 1
          }
        else
          log_error "Script setup/generate-env.sh não encontrado!"
          exit 1
        fi
      else
        log_warning "Continuando com o .env existente. Certifique-se de que todas as variáveis necessárias estão configuradas."
      fi
    else
      log_success "Arquivo .env parece estar completo."
    fi
  fi
  
  # Verificar e garantir ENCRYPTION_KEY (obrigatório)
  # IMPORTANTE: NÃO sobrescreve chaves existentes para evitar quebrar dados criptografados
  if ! grep -qE "^ENCRYPTION_KEY\s*=" .env 2>/dev/null; then
    log_warning "ENCRYPTION_KEY não encontrada no .env. Gerando..."
    backup_env_file ".env"
    
    # Usar Python do venv se disponível
    if [ -f ".venv/bin/python" ]; then
      PYTHON_ENV_CMD=".venv/bin/python"
    elif command -v python &> /dev/null; then
      PYTHON_ENV_CMD="python"
    else
      PYTHON_ENV_CMD="python3"
    fi
    
    FERNET_KEY=$($PYTHON_ENV_CMD - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
)
    if [ -n "$FERNET_KEY" ]; then
      echo "" >> .env
      echo "ENCRYPTION_KEY = '$FERNET_KEY'" >> .env
      log_success "ENCRYPTION_KEY adicionada ao .env."
    else
      log_error "Não foi possível gerar ENCRYPTION_KEY."
      log_error "Adicione manualmente ao .env: ENCRYPTION_KEY='sua_chave_aqui'"
      exit 1
    fi
  else
    log_info "ENCRYPTION_KEY já existe no .env (não será sobrescrita para preservar dados criptografados)."
  fi
  
  # Verificar se SECRET_KEY existe no .env
  if ! grep -q "^SECRET_KEY=" .env 2>/dev/null; then
    log_warning "SECRET_KEY não encontrada no .env. Gerando..."
    backup_env_file ".env"
    
    # Usar Python do venv se disponível
    if [ -f ".venv/bin/python" ]; then
      PYTHON_ENV_CMD=".venv/bin/python"
    elif command -v python &> /dev/null; then
      PYTHON_ENV_CMD="python"
    else
      PYTHON_ENV_CMD="python3"
    fi
    
    SECRET_KEY=$($PYTHON_ENV_CMD - <<EOF
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
EOF
)
    if [ -n "$SECRET_KEY" ]; then
      sed -i "1i SECRET_KEY=$SECRET_KEY" .env
      log_success "SECRET_KEY adicionada ao .env."
    fi
  fi
  
  # Validação final - garantir que ENCRYPTION_KEY existe
  if ! grep -qE "^ENCRYPTION_KEY\s*=" .env 2>/dev/null; then
    log_error "ENCRYPTION_KEY não foi criada corretamente!"
    exit 1
  fi
  
  # Garantir ACCOUNT_LINK_FREE_SLOTS (slots gratuitos de vinculação de contas)
  if ! grep -qE "^ACCOUNT_LINK_FREE_SLOTS\s*=" .env 2>/dev/null; then
    echo "" >> .env
    echo "# Slots gratuitos de vinculação de contas por usuário" >> .env
    echo "ACCOUNT_LINK_FREE_SLOTS=3" >> .env
    log_success "ACCOUNT_LINK_FREE_SLOTS adicionada ao .env (padrão: 3)."
  fi
  
  touch "$INSTALL_DIR/env_created"
  log_success "Arquivo .env criado e validado com sucesso."
fi

# Garantir ENCRYPTION_KEY mesmo se .env já existia (para casos onde foi criado manualmente)
# IMPORTANTE: Só adiciona se não existir, NUNCA substitui chaves existentes
if [ -f ".env" ] && ! grep -qE "^ENCRYPTION_KEY\s*=" .env 2>/dev/null; then
  log_warning "ENCRYPTION_KEY não encontrada no .env existente. Gerando..."
  backup_env_file ".env"
  
  # Usar Python do venv se disponível
  if [ -f ".venv/bin/python" ]; then
    PYTHON_ENV_CMD=".venv/bin/python"
  elif command -v python &> /dev/null; then
    PYTHON_ENV_CMD="python"
  else
    PYTHON_ENV_CMD="python3"
  fi
  
  FERNET_KEY=$($PYTHON_ENV_CMD - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
)
  if [ -n "$FERNET_KEY" ]; then
    echo "" >> .env
    echo "ENCRYPTION_KEY = '$FERNET_KEY'" >> .env
    log_success "ENCRYPTION_KEY adicionada ao .env existente."
  else
    log_error "Não foi possível gerar ENCRYPTION_KEY."
    log_error "Adicione manualmente ao .env: ENCRYPTION_KEY='sua_chave_aqui'"
    exit 1
  fi
elif [ -f ".env" ] && grep -qE "^ENCRYPTION_KEY\s*=" .env 2>/dev/null; then
  log_info "ENCRYPTION_KEY já existe no .env (preservada para manter dados criptografados)."
fi

# Garantir ACCOUNT_LINK_FREE_SLOTS mesmo se .env já existia (instalações antigas ou upgrades)
if [ -f ".env" ] && ! grep -qE "^ACCOUNT_LINK_FREE_SLOTS\s*=" .env 2>/dev/null; then
  echo "" >> .env
  echo "# Slots gratuitos de vinculação de contas por usuário" >> .env
  echo "ACCOUNT_LINK_FREE_SLOTS=3" >> .env
  log_success "ACCOUNT_LINK_FREE_SLOTS adicionada ao .env existente (padrão: 3)."
fi

if [ ! -f "$INSTALL_DIR/htpasswd_created" ]; then
  echo
  echo "🔐 Configurando autenticação básica (.htpasswd)..."
  
  # Garantir que o venv está ativado
  if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
  fi
  
  # Determinar qual Python usar e garantir que bcrypt/passlib está disponível
  PYTHON_CMD=""
  
  # Tentar Python do venv primeiro (verificar bcrypt primeiro, mais confiável)
  if [ -f ".venv/bin/python" ] && .venv/bin/python -c "import bcrypt" 2>/dev/null; then
    PYTHON_CMD=".venv/bin/python"
    echo "ℹ️  Usando Python do virtual environment (bcrypt disponível)"
  elif [ -f ".venv/bin/python" ] && .venv/bin/python -c "import passlib" 2>/dev/null; then
    PYTHON_CMD=".venv/bin/python"
    echo "ℹ️  Usando Python do virtual environment (passlib disponível)"
  elif command -v python &> /dev/null && python -c "import bcrypt" 2>/dev/null; then
    PYTHON_CMD="python"
    echo "ℹ️  Usando Python do venv (ativado, bcrypt disponível)"
  elif command -v python &> /dev/null && python -c "import passlib" 2>/dev/null; then
    PYTHON_CMD="python"
    echo "ℹ️  Usando Python do venv (ativado, passlib disponível)"
  elif python3 -c "import bcrypt" 2>/dev/null; then
    PYTHON_CMD="python3"
    echo "ℹ️  Usando Python do sistema (bcrypt disponível)"
  elif python3 -c "import passlib" 2>/dev/null; then
    PYTHON_CMD="python3"
    echo "ℹ️  Usando Python do sistema (passlib disponível)"
  else
    # bcrypt/passlib não está disponível, tentar instalar
    echo "📦 bcrypt/passlib não encontrado, instalando..."
    
    # Tentar instalar no venv primeiro
    if [ -f ".venv/bin/python" ]; then
      .venv/bin/python -m pip install bcrypt "passlib==1.7.4" 2>/dev/null && \
      (.venv/bin/python -c "import bcrypt" 2>/dev/null || .venv/bin/python -c "import passlib" 2>/dev/null) && \
      PYTHON_CMD=".venv/bin/python" && \
      echo "✅ bcrypt/passlib instalado no virtual environment"
    fi
    
    # Se não funcionou, tentar instalar no sistema
    if [ -z "$PYTHON_CMD" ]; then
      python3 -m pip install --user --break-system-packages bcrypt "passlib==1.7.4" 2>/dev/null || \
      python3 -m pip install --user bcrypt "passlib==1.7.4" 2>/dev/null || \
      sudo python3 -m pip install bcrypt "passlib==1.7.4" 2>/dev/null || true
      
      if python3 -c "import bcrypt" 2>/dev/null || python3 -c "import passlib" 2>/dev/null; then
        PYTHON_CMD="python3"
        echo "✅ bcrypt/passlib instalado no Python do sistema"
      else
        # Fallback: usar htpasswd do sistema
        if command -v htpasswd &> /dev/null; then
          PYTHON_CMD="htpasswd"
          echo "ℹ️  Usando htpasswd do sistema como alternativa"
        else
          log_error "Não foi possível instalar bcrypt/passlib. Instale manualmente: pip install bcrypt passlib"
          exit 1
        fi
      fi
    fi
  fi
  
  read -p "👤 Digite o login para o admin: " ADMIN_USER
  read -s -p "🔒 Digite a senha para o admin: " ADMIN_PASS
  echo
  mkdir -p nginx
  
  # Gerar hash da senha
  if [ "$PYTHON_CMD" = "htpasswd" ]; then
    # Usar htpasswd do sistema
    echo "$ADMIN_PASS" | htpasswd -ciB nginx/.htpasswd "$ADMIN_USER" 2>/dev/null || \
    htpasswd -cbB nginx/.htpasswd "$ADMIN_USER" "$ADMIN_PASS" 2>/dev/null
    if [ $? -eq 0 ]; then
      echo "✅ Hash gerado usando htpasswd do sistema"
    else
      log_error "Falha ao gerar hash com htpasswd"
      exit 1
    fi
  else
    # Usar Python - tentar bcrypt direto primeiro (mais confiável)
    HASHED_PASS=$($PYTHON_CMD - <<EOF
import sys
try:
    # Tentar usar bcrypt diretamente (mais confiável e compatível)
    import bcrypt
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw("$ADMIN_PASS".encode('utf-8'), salt)
    print(hashed.decode('utf-8'))
except ImportError:
    # Se bcrypt não estiver disponível, tentar passlib
    try:
        from passlib.hash import bcrypt as passlib_bcrypt
        print(passlib_bcrypt.using(rounds=10).hash("$ADMIN_PASS"))
    except Exception as e2:
        print(f"ERROR: Não foi possível importar bcrypt ou passlib: {e2}", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF
)
    
    if [ -z "$HASHED_PASS" ] || echo "$HASHED_PASS" | grep -q "ERROR"; then
      log_error "Falha ao gerar hash da senha. Tentando com htpasswd do sistema..."
      if command -v htpasswd &> /dev/null; then
        echo "$ADMIN_PASS" | htpasswd -ciB nginx/.htpasswd "$ADMIN_USER" 2>/dev/null || \
        htpasswd -cbB nginx/.htpasswd "$ADMIN_USER" "$ADMIN_PASS" 2>/dev/null
        if [ $? -ne 0 ]; then
          log_error "Falha ao gerar hash da senha com ambos os métodos."
          exit 1
        fi
      else
        log_error "Falha ao gerar hash da senha e htpasswd não está disponível."
        exit 1
      fi
    else
      echo "$ADMIN_USER:$HASHED_PASS" > nginx/.htpasswd
    fi
  fi
  echo "✅ Arquivo nginx/.htpasswd criado."
  touch "$INSTALL_DIR/htpasswd_created"
fi

if [ ! -f "$INSTALL_DIR/fernet_key_generated" ]; then
  # Verificar se ENCRYPTION_KEY já foi gerado pelo generate-env.sh
  # IMPORTANTE: NÃO substitui chaves existentes para evitar quebrar dados criptografados
  # Só substitui a chave placeholder padrão na primeira instalação (quando não há dados ainda)
  if ! grep -qE "^ENCRYPTION_KEY\s*=" .env 2>/dev/null; then
    log_info "ENCRYPTION_KEY não encontrada. Gerando..."
    
    # Usar Python do venv se disponível
    if [ -f ".venv/bin/python" ]; then
      PYTHON_ENV_CMD=".venv/bin/python"
    elif command -v python &> /dev/null; then
      PYTHON_ENV_CMD="python"
    else
      PYTHON_ENV_CMD="python3"
    fi
    
    FERNET_KEY=$($PYTHON_ENV_CMD - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
)
    if [ -n "$FERNET_KEY" ]; then
      echo "" >> .env
      echo "ENCRYPTION_KEY = '$FERNET_KEY'" >> .env
      log_success "ENCRYPTION_KEY adicionada ao .env."
    else
      log_warning "Não foi possível gerar ENCRYPTION_KEY."
    fi
  elif grep -qE "^ENCRYPTION_KEY\s*=\s*['\"]?iOg0mMfE54rqvAOZKxhmb-Rq0sgmRC4p1TBGu_JqHac=" .env 2>/dev/null; then
    # Só substitui se for a chave padrão/placeholder E se for a primeira instalação
    # Verificar se já foi feita instalação anterior (se sim, não substituir!)
    # Verificar também se há containers Docker rodando (instalação antiga)
    local has_running_containers=false
    if command -v docker &> /dev/null; then
      if docker ps --format '{{.Names}}' 2>/dev/null | grep -qE "(site_http|site_wsgi|postgres|celery)"; then
        has_running_containers=true
      fi
    fi
    
    # Verificar se há chave preservada no install.sh
    local has_preserved_key=false
    if [ -f "$INSTALL_DIR/.encryption_key_preserved" ]; then
      has_preserved_key=true
    fi
    
    # Verificar se é primeira instalação (não há instalação anterior)
    if [ ! -f "$INSTALL_DIR/.install_done" ] && [ ! -f "$INSTALL_DIR/build_executed" ] && [ "$has_running_containers" = "false" ] && [ "$has_preserved_key" = "false" ]; then
      log_warning "ENCRYPTION_KEY é a chave padrão/placeholder. Gerando nova chave (primeira instalação)..."
      backup_env_file ".env"
      
      # Usar Python do venv se disponível
      if [ -f ".venv/bin/python" ]; then
        PYTHON_ENV_CMD=".venv/bin/python"
      elif command -v python &> /dev/null; then
        PYTHON_ENV_CMD="python"
      else
        PYTHON_ENV_CMD="python3"
      fi
      
      FERNET_KEY=$($PYTHON_ENV_CMD - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
)
      if [ -n "$FERNET_KEY" ]; then
        sed -i "/^ENCRYPTION_KEY\s*=/c\ENCRYPTION_KEY='$FERNET_KEY'" .env
        log_success "ENCRYPTION_KEY atualizada no .env (chave padrão substituída)."
      else
        log_warning "Não foi possível gerar ENCRYPTION_KEY. Mantendo valor padrão."
      fi
    else
      log_warning "ENCRYPTION_KEY é a chave padrão, mas foi detectada instalação anterior."
      if [ "$has_running_containers" = "true" ]; then
        log_warning "Containers Docker estão rodando - preservando chave para manter dados criptografados."
      fi
      if [ "$has_preserved_key" = "true" ]; then
        log_warning "Chave preservada detectada - não será substituída."
      fi
      log_warning "NÃO será substituída para preservar dados criptografados."
      log_info "Se você realmente precisa substituir, faça backup do banco primeiro e remova os arquivos de status!"
    fi
  else
    log_info "ENCRYPTION_KEY já foi configurada (não será sobrescrita para preservar dados criptografados)."
  fi
  touch "$INSTALL_DIR/fernet_key_generated"
fi

if [ ! -f "$INSTALL_DIR/build_executed" ]; then
  echo
  log_info "🔨 Preparando build.sh..."
  
  # Validar que .env existe e tem ENCRYPTION_KEY antes de executar build.sh
  if [ ! -f ".env" ]; then
    log_error "Arquivo .env não encontrado! Execute primeiro: bash setup/generate-env.sh"
    exit 1
  fi
  
  # Verificar se ENCRYPTION_KEY existe (não gerar aqui, já foi verificado antes)
  if ! grep -qE "^ENCRYPTION_KEY\s*=" .env 2>/dev/null; then
    log_error "ENCRYPTION_KEY não encontrada no .env!"
    log_error "A chave deve ter sido gerada anteriormente. Verifique o .env."
    log_info "Você pode adicionar manualmente ao .env: ENCRYPTION_KEY='sua_chave_aqui'"
    exit 1
  fi
  
  # Não copia mais o build.sh, apenas referencia
  # O build.sh deve ser executado da pasta setup/
  if [ ! -f "setup/build.sh" ]; then
    log_error "Arquivo setup/build.sh não encontrado!"
    exit 1
  fi
  
  chmod +x setup/build.sh || true

  echo
  log_info "🚀 Executando build.sh..."
  bash setup/build.sh || { 
    log_error "Falha ao executar build.sh"
    log_info "Você pode executar manualmente depois com: bash setup/build.sh"
    exit 1
  }

  touch "$INSTALL_DIR/build_executed"
fi

if [ ! -f "$INSTALL_DIR/superuser_created" ]; then
  echo
  log_info "👤 Criando usuário administrador no Django..."
  
  # Perguntar se deseja criar o superuser agora
  read -p "Deseja criar o usuário administrador agora? (s/n): " CREATE_SUPERUSER
  
  if [[ ! "$CREATE_SUPERUSER" =~ ^[sS]$ ]]; then
    log_info "Criação do superuser pulada. Você pode criar depois com:"
    echo "  $DOCKER_COMPOSE exec site_http python3 manage.py createsuperuser"
    touch "$INSTALL_DIR/superuser_created"
  # Verificar se os containers estão rodando
  elif ! $DOCKER_COMPOSE ps | grep -q "site_http.*Up"; then
    log_warning "Containers não estão rodando. Pulando criação de superuser."
    log_info "Você pode criar o superuser depois com:"
    echo "  $DOCKER_COMPOSE exec site_http python3 manage.py createsuperuser"
    touch "$INSTALL_DIR/superuser_created"
  else
    read -p "Username: " DJANGO_SUPERUSER_USERNAME
    read -p "Email: " DJANGO_SUPERUSER_EMAIL
    read -s -p "Password: " DJANGO_SUPERUSER_PASSWORD
    echo
    read -s -p "Confirme a senha: " DJANGO_SUPERUSER_PASSWORD_CONFIRM
    echo

    if [ "$DJANGO_SUPERUSER_PASSWORD" != "$DJANGO_SUPERUSER_PASSWORD_CONFIRM" ]; then
      log_error "As senhas não conferem. Abortando."
      exit 1
    fi

    # Detectar qual serviço usar
    APP_SERVICE=""
    APP_CANDIDATES=("site_http" "site_wsgi" "app" "web" "site" "django" "backend")
    for svc in "${APP_CANDIDATES[@]}"; do
      if $DOCKER_COMPOSE ps --services 2>/dev/null | grep -q "^${svc}$"; then
        if $DOCKER_COMPOSE exec -T "$svc" python3 manage.py --version > /dev/null 2>&1; then
          APP_SERVICE="$svc"
          break
        fi
      fi
    done

    if [ -z "$APP_SERVICE" ]; then
      log_warning "Não foi possível detectar o serviço Django. Pulando criação de superuser."
      log_info "Você pode criar manualmente depois com:"
      echo "  $DOCKER_COMPOSE exec site_http python3 manage.py createsuperuser"
    else
      log_info "Usando serviço: $APP_SERVICE"
      if $DOCKER_COMPOSE exec -T "$APP_SERVICE" python3 manage.py shell <<PYTHON_SCRIPT
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('✅ Superuser \"$DJANGO_SUPERUSER_USERNAME\" criado com sucesso.')
else:
    print('ℹ️ O usuário \"$DJANGO_SUPERUSER_USERNAME\" já existe.')
PYTHON_SCRIPT
      then
        log_success "Superuser criado ou já existente."
      else
        log_warning "Falha ao criar superuser via script. Tente manualmente."
        log_info "Você pode criar manualmente depois com:"
        echo "  $DOCKER_COMPOSE exec $APP_SERVICE python3 manage.py createsuperuser"
      fi
    fi
  fi
  
  touch "$INSTALL_DIR/superuser_created"
fi

# Voltar ao diretório anterior se necessário
if [ "$(pwd)" != "$(dirname "$INSTALL_DIR")" ] && [ -d "lineage" ]; then
  popd > /dev/null 2>&1 || true
fi

touch "$INSTALL_DIR/.install_done"

echo
log_success "🎉 Instalação concluída com sucesso!"
echo
log_info "Informações importantes:"
echo "  - Acesse: http://localhost:6085"
echo "  - Para atualizar: bash setup/build.sh"
echo "  - Para parar: $DOCKER_COMPOSE down"
echo "  - Para iniciar: $DOCKER_COMPOSE up -d"
echo
log_info "Para configurar domínio personalizado:"
echo "  - Execute: sudo bash setup/nginx-proxy.sh"
echo