# Comandos Customizados do Projeto PDL

> **Última atualização:** 21/02/2026

Este documento lista todos os comandos Django customizados disponíveis no projeto PDL, organizados por categoria e funcionalidade.

## 📋 Índice

- [Comandos de Mídia e Storage](#comandos-de-mídia-e-storage)
- [Comandos de Licenciamento](#comandos-de-licenciamento)
- [Comandos de Moderação Social](#comandos-de-moderação-social)
- [Comandos de Recursos do Sistema](#comandos-de-recursos-do-sistema)
- [Comandos de Servidor e API](#comandos-de-servidor-e-api)
- [Comandos de Minigames (Jogos)](#comandos-de-minigames-jogos)
- [Comandos de Marketplace](#comandos-de-marketplace)
- [Comandos de Pagamentos](#comandos-de-pagamentos)
- [Comandos de FAQ e Conteúdo](#comandos-de-faq-e-conteúdo)
- [Comandos de Usuários e Autenticação](#comandos-de-usuários-e-autenticação)
- [Comandos de Limpeza e Manutenção](#comandos-de-limpeza-e-manutenção)

---

## 📁 Comandos de Mídia e Storage

### `sync_existing_media`
**Localização:** `apps/media_storage/management/commands/sync_existing_media.py`

Sincroniza arquivos existentes na pasta media com o banco de dados.

```bash
python manage.py sync_existing_media [opções]
```

**Opções:**
- `--folder`: Pasta específica dentro de media/ para sincronizar
- `--category`: Nome da categoria para os arquivos importados
- `--dry-run`: Apenas mostra os arquivos que seriam importados

**Exemplos:**
```bash
# Sincronizar todos os arquivos
python manage.py sync_existing_media

# Sincronizar apenas uma pasta específica
python manage.py sync_existing_media --folder avatars --category "Avatares"

# Simular importação
python manage.py sync_existing_media --dry-run
```

---

### `scan_media_usage`
**Localização:** `apps/media_storage/management/commands/scan_media_usage.py`

Escaneia o projeto e registra automaticamente o uso de arquivos de mídia.

```bash
python manage.py scan_media_usage [opções]
```

**Opções:**
- `--scan`: Escaneia modelos e registra usos de mídia
- `--stats`: Mostra estatísticas de uso de mídia
- `--orphaned`: Lista arquivos órfãos (físicos sem registro)
- `--cleanup-orphaned`: Remove arquivos órfãos do sistema de arquivos
- `--dry-run`: Apenas simula as ações sem executar

**Exemplos:**
```bash
# Escanear uso de mídia
python manage.py scan_media_usage --scan

# Ver estatísticas
python manage.py scan_media_usage --stats

# Listar arquivos órfãos
python manage.py scan_media_usage --orphaned

# Limpar arquivos órfãos
python manage.py scan_media_usage --cleanup-orphaned --dry-run
```

---

### `generate_thumbnails`
**Localização:** `apps/media_storage/management/commands/generate_thumbnails.py`

Gera thumbnails para imagens existentes que não possuem.

```bash
python manage.py generate_thumbnails [opções]
```

**Opções:**
- `--force`: Regenera thumbnails mesmo se já existirem
- `--size`: Tamanho do thumbnail (padrão: 300px)

**Exemplos:**
```bash
# Gerar thumbnails padrão
python manage.py generate_thumbnails

# Forçar regeneração
python manage.py generate_thumbnails --force

# Tamanho customizado
python manage.py generate_thumbnails --size 500
```

---

### `create_default_categories`
**Localização:** `apps/media_storage/management/commands/create_default_categories.py`

Cria categorias padrão para o sistema de mídia.

```bash
python manage.py create_default_categories
```

**Categorias criadas:**
- Imagens
- Documentos
- Vídeos
- Áudios
- Notícias
- Banners
- Avatares
- Logos
- Arquivos

---

### `cleanup_media`
**Localização:** `apps/media_storage/management/commands/cleanup_media.py`

Limpa arquivos de mídia não utilizados.

```bash
python manage.py cleanup_media [opções]
```

**Opções:**
- `--dry-run`: Apenas mostra os arquivos que seriam deletados
- `--force`: Força a remoção sem confirmação

**Exemplos:**
```bash
# Simular limpeza
python manage.py cleanup_media --dry-run

# Executar limpeza
python manage.py cleanup_media --force
```

---

## 🔐 Comandos de Licenciamento

### `generate_encryption_key`
**Localização:** `apps/main/licence/management/commands/generate_encryption_key.py`

Gera uma nova chave de criptografia para licenças.

```bash
python manage.py generate_encryption_key
```

**Saída:**
- Nova chave de criptografia
- Instruções para configuração no arquivo .env

---

### `create_test_license`
**Localização:** `apps/main/licence/management/commands/create_test_license.py`

Cria uma licença de teste para verificar o sistema.

```bash
python manage.py create_test_license
```

**Funcionalidades:**
- Cria licença FREE de teste
- Testa verificação automática
- Mostra status da licença

---

### `create_license`
**Localização:** `apps/main/licence/management/commands/create_license.py`

Cria uma nova licença PDL.

```bash
python manage.py create_license [opções]
```

**Opções:**
- `--type`: Tipo de licença (free ou pro)
- `--domain`: Domínio para ativação (obrigatório)
- `--email`: E-mail de contato (obrigatório)
- `--company`: Nome da empresa/cliente
- `--phone`: Telefone de contato
- `--contract`: Número do contrato (apenas para PDL PRO)
- `--days`: Dias de validade (apenas para PDL PRO)

**Exemplos:**
```bash
# Licença FREE
python manage.py create_license --type free --domain exemplo.com --email contato@exemplo.com

# Licença PRO
python manage.py create_license --type pro --domain exemplo.com --email contato@exemplo.com --company "Empresa XYZ" --contract "CONTR-2024-001" --days 365
```

---

### `check_license`
**Localização:** `apps/main/licence/management/commands/check_license.py`

Verifica o status das licenças PDL.

```bash
python manage.py check_license [opções]
```

**Opções:**
- `--detailed`: Exibe informações detalhadas
- `--domain`: Verifica apenas uma licença específica por domínio

**Exemplos:**
```bash
# Verificação básica
python manage.py check_license

# Verificação detalhada
python manage.py check_license --detailed

# Verificar domínio específico
python manage.py check_license --domain exemplo.com
```

---

## 🛡️ Comandos de Moderação Social

### `setup_moderation`
**Localização:** `apps/main/social/management/commands/setup_moderation.py`

Configura filtros otimizados de moderação específicos e eficazes.

```bash
python manage.py setup_moderation
```

**Filtros criados:**
- **Spam e Marketing** (3 filtros precisos)
- **Palavrões** (3 níveis de severidade)
- **Conteúdo Pornográfico** (2 filtros específicos)
- **URLs Suspeitas** (3 filtros inteligentes)
- **Discurso de Ódio** (2 filtros específicos)
- **Fake News** (1 filtro médico)
- **Comportamentos Suspeitos** (3 filtros inteligentes)
- **Golpes Brasileiros** (2 filtros específicos)

---

### `clear_moderation_filters`
**Localização:** `apps/main/social/management/commands/clear_moderation_filters.py`

Remove todos os filtros de moderação do sistema.

```bash
python manage.py clear_moderation_filters [opções]
```

**Opções:**
- `--force`: Força a remoção sem confirmação
- `--keep-defaults`: Mantém apenas os filtros padrão do sistema
- `--dry-run`: Mostra quais filtros seriam removidos sem executar

**Exemplos:**
```bash
# Simular remoção
python manage.py clear_moderation_filters --dry-run

# Remover filtros personalizados (manter padrões)
python manage.py clear_moderation_filters --keep-defaults

# Remover todos os filtros
python manage.py clear_moderation_filters --force
```

---

### `apply_filters_retroactive`
**Localização:** `apps/main/social/management/commands/apply_filters_retroactive.py`

Aplica filtros de moderação a todo o conteúdo existente (posts e comentários retroativos).

```bash
python manage.py apply_filters_retroactive [opções]
```

**Opções:**
- `--dry-run`: Executa sem aplicar mudanças (apenas simulação)
- `--batch-size`: Número de itens processados por lote (padrão: 100)
- `--filter-id`: ID específico do filtro para aplicar
- `--content-type`: Tipo de conteúdo para processar (posts, comments, all)

**Exemplos:**
```bash
# Simular aplicação retroativa
python manage.py apply_filters_retroactive --dry-run

# Aplicar a posts apenas
python manage.py apply_filters_retroactive --content-type posts

# Aplicar filtro específico
python manage.py apply_filters_retroactive --filter-id 5
```

---

## 🎯 Comandos de Recursos do Sistema

### `populate_resources`
**Localização:** `apps/main/resources/management/commands/populate_resources.py`

Popula o banco de dados com os recursos padrão do sistema.

```bash
python manage.py populate_resources
```

**Recursos criados:**
- **Loja** (7 recursos)
- **Carteira** (4 recursos)
- **Rede Social** (4 recursos)
- **Jogos** (4 recursos)
- **Leilões** (3 recursos)
- **Inventário** (2 recursos)
- **Pagamentos** (3 recursos)
- **Notificações** (1 recurso)
- **API** (1 recurso)
- **Administração** (1 recurso)

---

## 🖥️ Comandos de Servidor e API

### `migrate_l2_accounts`
**Localização:** `apps/lineage/server/management/commands/migrate_l2_accounts.py`

Migra contas do banco do L2 para o PDL seguindo regras específicas.

```bash
python manage.py migrate_l2_accounts [opções]
```

**Opções:**
- `--dry-run`: Executa em modo de teste sem criar usuários
- `--prefix`: Prefixo para emails duplicados (padrão: L2_)
- `--password-length`: Comprimento da senha aleatória (padrão: 64)
- `--batch-size`: Tamanho do lote para processamento (padrão: 100)

**Exemplos:**
```bash
# Simular migração
python manage.py migrate_l2_accounts --dry-run

# Migração com configurações customizadas
python manage.py migrate_l2_accounts --prefix "MIGR_" --password-length 32 --batch-size 50
```

---

### `generate_api_token`
**Localização:** `apps/lineage/server/management/commands/generate_api_token.py`

Gera ou exibe o token de autenticação DRF para um usuário.

```bash
python manage.py generate_api_token --username NOME_USUARIO [--password SENHA]
```

**Exemplos:**
```bash
# Gerar token para usuário existente
python manage.py generate_api_token --username admin

# Criar usuário e gerar token
python manage.py generate_api_token --username api_user --password senha123
```

---

### `test_queries`
**Localização:** `apps/lineage/server/management/commands/test_queries.py`

Comando essencial para desenvolvimento, testa todas as 7 classes do arquivo gerado `query_*.py` no banco L2 e garante que nenhuma quebra ocorra entre a bridge Django -> Lineage 2 DB. Executa em torno de 46 testes.

```bash
python manage.py test_queries [opções]
```

**Opções:**
- `--verbose`: Mostra detalhes expansivos do resultado de cada chamada.

**Exemplos:**
```bash
# Execução padrão
python manage.py test_queries

# Executar exibindo o dump das respostas JSON/Dict no terminal
python manage.py test_queries --verbose
```

---

## 🎮 Comandos de Minigames (Jogos)

### `populate_new_games`
**Localização:** `apps/lineage/games/management/commands/populate_new_games.py`

Popula os três novos modos de Jogo (Slot Machine, Dice Game e Fishing Game) com as configurações iniciais de apostas, prêmios, icones, multiplicadores e raridade de itens (Gera a Base do Fishing).

```bash
python manage.py populate_new_games
```

---

### `fix_duplicate_configs`
**Localização:** `apps/lineage/games/management/commands/fix_duplicate_configs.py`

Remove lixo e configurações duplicadas geradas acidentalmente nas tabelas dos jogos (Mantendo apenas UMA configuração principal ativa para Dice, Slots e Fishing).

```bash
python manage.py fix_duplicate_configs
```

---

## 🛒 Comandos de Marketplace

### `create_marketplace_master_account`
**Localização:** `apps/lineage/marketplace/management/commands/create_marketplace_master_account.py`

Cria a conta MASTER no banco do Lineage2 (L2 DB) que armazenará temporariamente os personagens offline listados a venda no Marketplace até seu respectivo comprador.

```bash
python manage.py create_marketplace_master_account [opções]
```

**Opções:**
- `--account-name [NOME]`: Nome customizado (Padrão/Default: MARKETPLACE_SYSTEM)
- `--force`: Recria a account forçadamente ignorando existências

---

### `cancel_old_marketplace_sales`
**Localização:** `apps/lineage/marketplace/management/commands/cancel_old_marketplace_sales.py`

Audita, estorna e processa listings pendentes ou vendas presas do sistema de Marketplace para o banco de dados L2 Master, ou cancelando do Database em caso de incongruência.

```bash
python manage.py cancel_old_marketplace_sales [opções]
```

**Opções:**
- `--dry-run`: Somente relata o que aconteceria.
- `--force`: Cancela sem prompt (Y/N) input.
- `--move-to-master`: Tenta resgatar preservando os personagens ativos listados pra conta mestre

---

## 💳 Comandos de Pagamentos

### `processar_aprovados`
**Localização:** `apps/lineage/payment/management/commands/processar_aprovados.py`

Varre o status dos pacotes na gateway pra finalizar transações e debitar as coins ao jogador no jogo.

```bash
python manage.py processar_aprovados
```

---

### `reconciliar_pendentes`
**Localização:** `apps/lineage/payment/management/commands/reconciliar_pendentes.py`

Força um "Pull" das credenciais via IPN/API do Mercado Pago, reconciliando faturas esquecidas.

```bash
python manage.py reconciliar_pendentes [opções]
```

**Opções:**
- `--cutoff-minutes [INT]`: Minutos de corte em relação ao timestamp de criação da transação. Padrão 5.

---

## 📖 Comandos de FAQ e Conteúdo

### `populate_pdl_faqs`
**Localização:** `apps/main/faq/management/commands/populate_pdl_faqs.py`

Gera dezenas de sessões FAQ informativas base explicando detalhadamente (por traduções) como os jogadores podem extrair o máximo do site e do PDL, com links úteis.

```bash
python manage.py populate_pdl_faqs [opções]
```

**Opções:**
- `--clear`: Remove todas as faqs customizaveis antes do Seed.
- `--language [pt|en|es|all]`: Cria/Ajusta em idiomas selecionados. Padrão pt.

---

## 👤 Comandos de Usuários e Autenticação

### `test_suspension_login`
**Localização:** `apps/main/home/management/commands/test_suspension_login.py`

Testa o sistema de login com usuários suspensos.

```bash
python manage.py test_suspension_login --username NOME_USUARIO [opções]
```

**Opções:**
- `--action`: Ação a ser executada (suspend, ban, reactivate)
- `--duration`: Duração da suspensão em dias (padrão: 7)
- `--reason`: Motivo da suspensão

**Exemplos:**
```bash
# Ver status do usuário
python manage.py test_suspension_login --username joao

# Suspender usuário
python manage.py test_suspension_login --username joao --action suspend --duration 30 --reason "Violação das regras"

# Banir usuário
python manage.py test_suspension_login --username joao --action ban --reason "Comportamento inadequado"

# Reativar usuário
python manage.py test_suspension_login --username joao --action reactivate
```

---

## 🧹 Comandos de Limpeza e Manutenção

### `cleanup_storage`
**Localização:** `apps/main/management/commands/cleanup_storage.py`

Utilitário para análise e limpeza do storage de mídia.

```bash
python manage.py cleanup_storage [opções]
```

**Opções:**
- `--analyze`: Analisa o storage e mostra arquivos órfãos
- `--clean`: Remove arquivos órfãos
- `--stats`: Mostra estatísticas do storage
- `--confirm`: Executa limpeza sem pedir confirmação

**Exemplos:**
```bash
# Ver estatísticas
python manage.py cleanup_storage --stats

# Analisar storage
python manage.py cleanup_storage --analyze

# Limpar arquivos órfãos
python manage.py cleanup_storage --clean --confirm
```

---

### `cleanup_orphaned_media`
**Localização:** `apps/main/management/commands/cleanup_orphaned_media.py`

Remove arquivos de mídia órfãos (não referenciados no banco de dados).

```bash
python manage.py cleanup_orphaned_media [opções]
```

**Opções:**
- `--dry-run`: Apenas mostra quais arquivos seriam removidos
- `--delete`: Remove os arquivos órfãos encontrados
- `--confirm`: Remove arquivos sem pedir confirmação
- `--path`: Caminho específico para limpar
- `--exclude`: Caminhos para excluir da limpeza
- `--verbose`: Mostra informações detalhadas sobre cada arquivo

**Exemplos:**
```bash
# Simular limpeza
python manage.py cleanup_orphaned_media --dry-run

# Limpar com confirmação
python manage.py cleanup_orphaned_media --delete

# Limpar sem confirmação
python manage.py cleanup_orphaned_media --delete --confirm

# Limpar pasta específica
python manage.py cleanup_orphaned_media --delete --path media/social/posts/
```

---

### `backup_media`
**Localização:** `apps/main/management/commands/backup_media.py`

Utilitário para backup de arquivos de mídia.

```bash
python manage.py backup_media [opções]
```

**Opções:**
- `--create`: Cria um backup dos arquivos de mídia
- `--restore`: Restaura backup do arquivo especificado
- `--list`: Lista backups disponíveis
- `--path`: Caminho específico para backup
- `--backup-dir`: Diretório para salvar backups (padrão: backups/media)

**Exemplos:**
```bash
# Criar backup
python manage.py backup_media --create

# Listar backups
python manage.py backup_media --list

# Restaurar backup
python manage.py backup_media --restore media_backup_20241201_143022.zip

# Backup de pasta específica
python manage.py backup_media --create --path media/avatars
```

---

## 📊 Resumo dos Comandos por Categoria

| Categoria | Quantidade | Comandos |
|-----------|------------|----------|
| **Mídia e Storage** | 5 | sync_existing_media, scan_media_usage, generate_thumbnails, create_default_categories, cleanup_media |
| **Licenciamento** | 4 | generate_encryption_key, create_test_license, create_license, check_license |
| **Moderação Social** | 3 | setup_moderation, clear_moderation_filters, apply_filters_retroactive |
| **Recursos do Sistema** | 1 | populate_resources |
| **Servidor e API** | 3 | migrate_l2_accounts, generate_api_token, test_queries |
| **Minigames (Jogos)** | 2 | populate_new_games, fix_duplicate_configs |
| **Marketplace** | 2 | create_marketplace_master_account, cancel_old_marketplace_sales |
| **Pagamentos** | 2 | processar_aprovados, reconciliar_pendentes |
| **FAQ e Conteúdo** | 1 | populate_pdl_faqs |
| **Usuários e Autenticação** | 1 | test_suspension_login |
| **Limpeza e Manutenção** | 3 | cleanup_storage, cleanup_orphaned_media, backup_media |

**Total: 27 comandos customizados**

---

## 🚀 Comandos Mais Utilizados

### Para Desenvolvimento
```bash
# Configurar sistema básico
python manage.py create_default_categories
python manage.py populate_resources
python manage.py setup_moderation

# Criar licença de teste
python manage.py create_test_license
```

### Para Produção
```bash
# Verificar status
python manage.py check_license --detailed
python manage.py scan_media_usage --stats

# Limpeza e manutenção
python manage.py cleanup_orphaned_media --dry-run
python manage.py backup_media --create
```

### Para Migração
```bash
# Migrar contas do L2
python manage.py migrate_l2_accounts --dry-run
python manage.py migrate_l2_accounts
```

---

## ⚠️ Observações Importantes

1. **Sempre use `--dry-run` primeiro** para comandos que fazem alterações
2. **Faça backup** antes de executar comandos de limpeza
3. **Teste em ambiente de desenvolvimento** antes de usar em produção
4. **Monitore logs** durante execução de comandos longos
5. **Use `--help`** para ver opções específicas de cada comando

---

## 📝 Histórico de Versões

- **v1.0** - Documentação inicial com 19 comandos
- **v1.1** - Adicionados exemplos de uso e categorização
- **v1.2** - Incluídas observações importantes e resumo estatístico

---

[ Voltar ao Índice](../INDEX.md)
