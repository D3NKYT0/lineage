# Guia de Uso do install.sh

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Instalação Completa](#instalação-completa)
- [Comandos Disponíveis](#comandos-disponíveis)
- [Scripts do Setup](#scripts-do-setup)
- [Exemplos de Uso](#exemplos-de-uso)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## 🎯 Visão Geral

O `install.sh` é o script principal de instalação e gerenciamento do **Painel Definitivo Lineage (PDL)**. Ele serve como um ponto central para executar todos os scripts de configuração e instalação do projeto.

### Características Principais

- ✅ **Centralizado**: Um único ponto de entrada para todos os scripts
- ✅ **Flexível**: Execute scripts individuais ou a instalação completa
- ✅ **Intuitivo**: Menu interativo e ajuda integrada
- ✅ **Seguro**: Detecta e solicita privilégios quando necessário
- ✅ **Documentado**: Cada script tem descrição clara

---

## 📦 Pré-requisitos

Antes de usar o `install.sh`, certifique-se de ter:

1. **Sistema Operacional**: Ubuntu 20.04 (Focal), 22.04 (Jammy) ou 24.04 (Noble)
2. **Git**: Instalado e configurado
3. **Acesso à Internet**: Para clonar o repositório e baixar dependências
4. **Privilégios**: Acesso sudo para scripts que requerem root

### Verificar Pré-requisitos

```bash
# Verificar versão do Ubuntu
lsb_release -a

# Verificar Git
git --version

# Verificar acesso sudo
sudo -v
```

---

## 🚀 Instalação Completa

A forma mais simples de instalar o PDL é executar o `install.sh` sem argumentos:

```bash
# Tornar o script executável (se necessário)
chmod +x install.sh

# Executar instalação completa
./install.sh
```

### O que acontece durante a instalação:

1. ✅ Verificação de pré-requisitos
2. ✅ Clonagem do repositório (se necessário)
3. ✅ Execução do `setup.sh` (instalação inicial)
4. ✅ Execução do `build.sh` (build e deploy)

### Fluxo de Instalação

```
┌─────────────────┐
│   ./install.sh  │
└────────┬────────┘
         │
         ├─► Verifica pré-requisitos
         │
         ├─► Clona repositório (se necessário)
         │
         ├─► Executa setup.sh
         │   ├─► Instala Docker
         │   ├─► Instala Python
         │   ├─► Configura ambiente
         │   └─► Gera .env
         │
         └─► Executa build.sh
             ├─► Build Docker images
             ├─► Inicia containers
             └─► Aplica migrações
```

---

## 🎮 Comandos Disponíveis

### Comando: `install` (Padrão)

Instalação completa do PDL.

```bash
./install.sh
# ou
./install.sh install
```

**Quando usar**: Primeira instalação do projeto.

---

### Comando: `menu`

Menu interativo para escolher qual script executar.

```bash
./install.sh menu
```

**Opções do menu**:
1. Instalação completa (setup.sh + build.sh)
2. Apenas setup.sh
3. Apenas build.sh
4. Backup do banco de dados
5. Configurar proxy reverso (nginx-proxy.sh)
6. Instalar Nginx (install-nginx.sh)
7. Gerar arquivo .env (generate-env.sh)
8. Listar scripts disponíveis
9. Sair

---

### Comando: `setup`

Executa apenas o `setup.sh` (instalação inicial).

```bash
./install.sh setup
```

**Quando usar**: Quando você já tem o projeto configurado e só precisa refazer a instalação inicial.

---

### Comando: `build`

Executa apenas o `build.sh` (build e deploy).

```bash
./install.sh build
```

**Quando usar**: 
- Após atualizar o código do repositório
- Para fazer rebuild dos containers Docker
- Para aplicar migrações do banco de dados

---

### Comando: `backup`

Executa o script de backup do banco de dados.

```bash
# Criar backup
./install.sh backup

# Listar backups
./install.sh backup list

# Restaurar backup
./install.sh backup restore
```

**Quando usar**: 
- Antes de atualizações importantes
- Para fazer backup periódico
- Para restaurar dados anteriores

---

### Comando: `nginx-proxy`

Configura o proxy reverso do Nginx com domínio personalizado.

```bash
./install.sh nginx-proxy
```

**Quando usar**: Quando você quer configurar um domínio personalizado para acessar o PDL.

**Nota**: Este comando requer privilégios de root (sudo será solicitado automaticamente).

---

### Comando: `install-nginx`

Instala o Nginx do repositório oficial.

```bash
# Instalar versão mainline (padrão)
./install.sh install-nginx

# Instalar versão stable
./install.sh install-nginx stable

# Instalar versão mainline (explícito)
./install.sh install-nginx mainline
```

**Quando usar**: Quando você precisa instalar ou atualizar o Nginx no servidor.

**Nota**: Este comando requer privilégios de root (sudo será solicitado automaticamente).

---

### Comando: `generate-env`

Gera o arquivo `.env` de forma interativa.

```bash
./install.sh generate-env
```

**Quando usar**: 
- Primeira configuração do projeto
- Quando você precisa recriar o `.env`
- Para adicionar novas configurações

**O que faz**:
- Gera variáveis obrigatórias automaticamente
- Pergunta quais categorias opcionais incluir:
  - Email
  - Lineage DB
  - AWS S3
  - Pagamentos (Mercado Pago/Stripe)
  - Social Login
  - Server Status
  - Fake Players
  - VAPID (Web Push)

---

### Comando: `list`

Lista todos os scripts disponíveis na pasta `setup/`.

```bash
./install.sh list
```

**Saída esperada**:
```
[INFO] Scripts disponíveis na pasta setup/:

  📦 setup.sh           - Instalação inicial completa (Docker, Python, etc.)
  🔨 build.sh           - Build e deploy do projeto
  💾 backup.sh          - Backup do banco de dados
  🌐 nginx-proxy.sh      - Configurar proxy reverso com domínio
  🔧 install-nginx.sh    - Instalar Nginx do repositório oficial
  ⚙️  generate-env.sh    - Gerar arquivo .env interativamente
```

---

### Comando: `help`

Mostra a ajuda com todos os comandos disponíveis.

```bash
./install.sh help
# ou
./install.sh --help
# ou
./install.sh -h
```

---

## 📚 Scripts do Setup

O `install.sh` gerencia os seguintes scripts da pasta `setup/`:

| Script | Descrição | Requer Root |
|--------|-----------|-------------|
| `setup.sh` | Instalação inicial completa | Não |
| `build.sh` | Build e deploy | Não |
| `backup.sh` | Backup do banco de dados | Não |
| `nginx-proxy.sh` | Configurar proxy reverso | Sim |
| `install-nginx.sh` | Instalar Nginx | Sim |
| `generate-env.sh` | Gerar arquivo .env | Não |

---

## 💡 Exemplos de Uso

### Exemplo 1: Primeira Instalação

```bash
# Clone o repositório
git clone https://github.com/D3NKYT0/lineage.git
cd lineage

# Execute a instalação completa
chmod +x install.sh
./install.sh
```

### Exemplo 2: Atualizar o Projeto

```bash
# Atualizar código
git pull origin main

# Rebuild e deploy
./install.sh build
```

### Exemplo 3: Configurar Domínio Personalizado

```bash
# 1. Instalar Nginx (se ainda não instalado)
./install.sh install-nginx

# 2. Configurar proxy reverso
./install.sh nginx-proxy
# Digite o domínio quando solicitado
```

### Exemplo 4: Fazer Backup Antes de Atualizar

```bash
# 1. Criar backup
./install.sh backup

# 2. Atualizar código
git pull origin main

# 3. Rebuild
./install.sh build
```

### Exemplo 5: Recriar Arquivo .env

```bash
# Gerar novo .env interativamente
./install.sh generate-env

# O script fará backup do .env existente automaticamente
```

### Exemplo 6: Usar Menu Interativo

```bash
./install.sh menu

# Escolha a opção desejada no menu
```

---

## 🔧 Troubleshooting

### Problema: "Pasta setup/ não encontrada!"

**Solução**: Certifique-se de estar executando o script da raiz do projeto.

```bash
# Verificar se está no diretório correto
ls -la setup/

# Se não estiver, navegue até a raiz do projeto
cd /caminho/para/lineage
```

---

### Problema: "Git não está instalado"

**Solução**: Instale o Git.

```bash
sudo apt update
sudo apt install -y git
```

---

### Problema: "Este script não deve ser executado como root"

**Solução**: Execute o script sem sudo (ele pedirá quando necessário).

```bash
# ❌ ERRADO
sudo ./install.sh

# ✅ CORRETO
./install.sh
```

---

### Problema: "Falha ao clonar repositório"

**Soluções**:
1. Verifique sua conexão com a internet
2. Verifique se o Git está instalado
3. Verifique se você tem acesso ao repositório

```bash
# Testar conexão
ping github.com

# Testar Git
git clone https://github.com/D3NKYT0/lineage.git
```

---

### Problema: "Container não está rodando"

**Solução**: Inicie os containers Docker.

```bash
# Verificar status
docker compose ps

# Iniciar containers
docker compose up -d
```

---

### Problema: "Network não pode ser deletada"

**Solução**: Este problema foi corrigido no `build.sh`. Se ainda ocorrer:

```bash
# Remover network manualmente (se não estiver em uso)
docker network rm lineage_network

# Executar build novamente
./install.sh build
```

---

## ❓ FAQ

### P: Posso executar o install.sh várias vezes?

**R**: Sim! O script verifica se já foi instalado e oferece opções:
- Rodar apenas o build
- Refazer instalação completa
- Sair

---

### P: O install.sh modifica os scripts do setup?

**R**: Não! O `install.sh` apenas **executa** os scripts do `setup/`. Quando você atualizar os scripts do `setup/`, o `install.sh` automaticamente usará as versões mais recentes.

---

### P: Preciso executar como root?

**R**: Não! Execute sem sudo. O script detecta quando precisa de privilégios e solicita automaticamente (para scripts como `nginx-proxy.sh` e `install-nginx.sh`).

---

### P: Como desinstalar o PDL?

**R**: Para remover os containers e volumes:

```bash
cd /caminho/para/lineage
docker compose down -v
```

Para remover completamente, delete o diretório do projeto.

---

### P: Posso usar o install.sh em produção?

**R**: Sim! O script foi projetado para ser usado tanto em desenvolvimento quanto em produção. Certifique-se de:
- Configurar o `.env` corretamente
- Configurar o proxy reverso com SSL
- Fazer backups regulares

---

### P: Como atualizar o install.sh?

**R**: O `install.sh` está no repositório. Para atualizar:

```bash
git pull origin main
```

---

### P: O que fazer se a instalação falhar?

**R**: 
1. Verifique os logs de erro
2. Verifique os pré-requisitos
3. Execute o script novamente (ele é idempotente)
4. Consulte a seção [Troubleshooting](#troubleshooting)

---

## 📖 Recursos Adicionais

- [README.md](../README.md) - Documentação principal do projeto
- [INSTALLATION_AND_DEPLOY.md](INSTALLATION_AND_DEPLOY.md) - Guia de instalação detalhado
- [VARIABLES_ENVIRONMENT.md](VARIABLES_ENVIRONMENT.md) - Variáveis de ambiente

---

## 🤝 Contribuindo

Se encontrar problemas ou tiver sugestões para melhorar o `install.sh`, abra uma issue no repositório:

https://github.com/D3NKYT0/lineage/issues

---

## 📝 Changelog

### Versão Atual

- ✅ Suporte a todos os scripts do setup
- ✅ Menu interativo
- ✅ Detecção automática de privilégios
- ✅ Tratamento robusto de erros
- ✅ Interface com cores e mensagens claras

---

**Última atualização**: 2025-01-27

