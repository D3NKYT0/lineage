# Comandos para Limpeza de Arquivos de Mídia Órfãos

## 🎯 Problema

Com o tempo, arquivos de mídia podem ficar "órfãos" no storage - arquivos que existem fisicamente mas não estão mais referenciados no banco de dados. Isso pode acontecer por:

- Edições de posts que substituem imagens
- Exclusões de registros no banco
- Erros durante uploads
- Migrações ou importações de dados

## 🔧 Solução: Comandos Django

Criei **3 comandos Django** para gerenciar arquivos órfãos:

### 1. `cleanup_orphaned_media` - Comando Principal

**Funcionalidades:**
- Busca arquivos órfãos em todo o sistema
- Suporte a storage local e remoto (S3, etc.)
- Modo dry-run para simulação
- Exclusão de caminhos específicos
- Análise detalhada com tamanhos

#### Uso Básico

```bash
# Simular limpeza (não remove nada)
python manage.py cleanup_orphaned_media --dry-run

# Remover arquivos órfãos (com confirmação)
python manage.py cleanup_orphaned_media --delete

# Remover sem pedir confirmação
python manage.py cleanup_orphaned_media --delete --confirm

# Mostrar detalhes de cada arquivo
python manage.py cleanup_orphaned_media --dry-run --verbose
```

#### Uso Avançado

```bash
# Limpar apenas um diretório específico
python manage.py cleanup_orphaned_media --delete --path "media/social/posts/"

# Excluir diretórios específicos da limpeza
python manage.py cleanup_orphaned_media --delete --exclude "media/static/" "media/admin/"

# Combinação de opções
python manage.py cleanup_orphaned_media --delete --verbose --exclude "media/static/"
```

#### Exemplo de Saída

```
🔍 Iniciando busca por arquivos de mídia órfãos...

📊 Total de arquivos referenciados no banco: 1,247
📁 Total de arquivos físicos encontrados: 1,289

⚠️  Encontrados 42 arquivos órfãos:
📊 Tamanho total: 15.67 MB

  1. social/posts/old_image_1.jpg (245.3 KB)
  2. social/posts/old_image_2.jpg (189.7 KB)
  3. social/avatars/old_avatar.jpg (156.2 KB)
  ... e mais 39 arquivos

🔍 Modo DRY-RUN: Nenhum arquivo foi removido
```

### 2. `cleanup_storage` - Comando Simplificado

**Funcionalidades:**
- Análise rápida do storage
- Estatísticas por modelo
- Limpeza simples
- Interface mais amigável

#### Uso

```bash
# Mostrar estatísticas do storage
python manage.py cleanup_storage --stats

# Analisar arquivos órfãos
python manage.py cleanup_storage --analyze

# Limpar arquivos órfãos
python manage.py cleanup_storage --clean

# Limpar sem pedir confirmação
python manage.py cleanup_storage --clean --confirm
```

#### Exemplo de Saída

```
📊 Estatísticas do Storage

📁 Modelos com arquivos de mídia:
  • Post: 245 registros
    - Campo: image
    - Campo: video
  • UserProfile: 89 registros
    - Campo: avatar
    - Campo: cover_image
  • Comment: 156 registros
    - Campo: image

📊 Total de registros com mídia: 490
```

### 3. `backup_media` - Backup e Restauração

**Funcionalidades:**
- Backup completo dos arquivos de mídia
- Restauração de backups
- Listagem de backups disponíveis
- Suporte a caminhos específicos

#### Uso

```bash
# Criar backup completo
python manage.py backup_media --create

# Criar backup de diretório específico
python manage.py backup_media --create --path "media/social/"

# Listar backups disponíveis
python manage.py backup_media --list

# Restaurar backup
python manage.py backup_media --restore "media_backup_20241201_143022.zip"

# Especificar diretório de backup customizado
python manage.py backup_media --create --backup-dir "/path/to/backups"
```

#### Exemplo de Saída

```
📦 Criando backup: media_backup_20241201_143022.zip

📁 1,289 arquivos adicionados ao backup

✅ Backup criado com sucesso!
📁 Arquivo: backups/media/media_backup_20241201_143022.zip
📊 Tamanho: 247.83 MB
```

## 🚀 Fluxo Recomendado de Limpeza

### 1. Análise Inicial
```bash
# Ver estatísticas do storage
python manage.py cleanup_storage --stats

# Analisar arquivos órfãos
python manage.py cleanup_storage --analyze
```

### 2. Backup Preventivo (Recomendado)
```bash
# Criar backup antes da limpeza
python manage.py backup_media --create
```

### 3. Simulação da Limpeza
```bash
# Simular remoção (não remove nada)
python manage.py cleanup_orphaned_media --dry-run --verbose
```

### 4. Execução da Limpeza
```bash
# Remover arquivos órfãos
python manage.py cleanup_orphaned_media --delete --confirm
```

### 5. Verificação Final
```bash
# Verificar se a limpeza funcionou
python manage.py cleanup_storage --analyze
```

## ⚙️ Configurações e Opções

### Exclusões Padrão
Os comandos excluem automaticamente:
- `media/static/` - Arquivos estáticos
- `media/admin/` - Arquivos do admin do Django
- `media/default/` - Arquivos padrão

### Caminhos Customizados
```bash
# Excluir caminhos específicos
python manage.py cleanup_orphaned_media --delete \
  --exclude "media/cache/" "media/temp/" "media/logs/"
```

### Storage Remoto (S3)
Os comandos funcionam automaticamente com:
- AWS S3
- Google Cloud Storage
- Qualquer storage compatível com Django

## 🔒 Segurança e Boas Práticas

### 1. Sempre Faça Backup
```bash
# Antes de qualquer limpeza
python manage.py backup_media --create
```

### 2. Use Dry-Run Primeiro
```bash
# Sempre simule antes de executar
python manage.py cleanup_orphaned_media --dry-run
```

### 3. Verifique os Resultados
```bash
# Após a limpeza, verifique se está tudo ok
python manage.py cleanup_storage --analyze
```

### 4. Agende Limpezas Regulares
```bash
# Adicione ao crontab para execução automática
# Exemplo: toda segunda-feira às 2h da manhã
0 2 * * 1 cd /path/to/project && python manage.py cleanup_orphaned_media --delete --confirm
```

## 🎯 Casos de Uso Específicos

### Limpeza Após Migração
```bash
# Backup antes da migração
python manage.py backup_media --create

# Após migração, limpar órfãos
python manage.py cleanup_orphaned_media --delete --confirm
```

### Limpeza de Diretório Específico
```bash
# Limpar apenas posts antigos
python manage.py cleanup_orphaned_media --delete \
  --path "media/social/posts/" \
  --exclude "media/social/posts/featured/"
```

### Análise de Espaço
```bash
# Ver quanto espaço pode ser liberado
python manage.py cleanup_orphaned_media --dry-run --verbose | grep "Tamanho total"
```

## 🎉 Benefícios

### ✅ **Storage Limpo**
- Remove arquivos desnecessários
- Libera espaço em disco
- Reduz custos de storage (especialmente S3)

### ✅ **Performance**
- Menos arquivos para processar
- Backups mais rápidos
- Navegação mais eficiente

### ✅ **Organização**
- Storage mais organizado
- Fácil identificação de problemas
- Melhor manutenção

### ✅ **Segurança**
- Backup automático
- Verificação antes da remoção
- Logs detalhados

## 📝 Logs e Monitoramento

Os comandos geram logs detalhados que podem ser usados para:
- Monitoramento de espaço
- Identificação de padrões
- Auditoria de limpezas
- Alertas automáticos

## 🚨 Troubleshooting

### Erro de Permissão
```bash
# Verificar permissões do diretório de mídia
ls -la media/
chmod 755 media/
```

### Storage Remoto Não Funciona
```bash
# Verificar configurações do S3
python manage.py shell
>>> from django.core.files.storage import default_storage
>>> default_storage.listdir('/')
```

### Backup Falha
```bash
# Verificar espaço em disco
df -h
# Verificar permissões
ls -la backups/
```

## 🎯 Conclusão

Estes comandos fornecem uma solução completa para gerenciamento de arquivos de mídia órfãos:

1. **Análise**: Identifica arquivos órfãos
2. **Backup**: Protege dados importantes
3. **Limpeza**: Remove arquivos desnecessários
4. **Monitoramento**: Acompanha o status do storage

Use-os regularmente para manter seu storage limpo e organizado! 🚀
