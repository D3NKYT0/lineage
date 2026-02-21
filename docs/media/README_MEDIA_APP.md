# Media Storage - Sistema de Gerenciamento de Mídia

> **Última atualização:** 21/02/2026

Um aplicativo Django completo para gerenciamento de arquivos de mídia com interface administrativa e de usuário.

## 🚀 Funcionalidades

### ✨ Principais Recursos
- **Upload de Arquivos**: Upload individual e em lote
- **Gerenciamento Completo**: Visualização, edição e exclusão de arquivos
- **Categorização**: Organização por categorias personalizadas
- **Preview Inteligente**: Visualização de imagens, vídeos e áudios
- **Controle de Acesso**: Arquivos públicos e privados
- **Busca Avançada**: Filtros por tipo, categoria, tags e texto
- **Limpeza Automática**: Identificação e remoção de arquivos não utilizados
- **Interface Responsiva**: Funciona perfeitamente em desktop e mobile

### 📁 Tipos de Arquivo Suportados
- **Imagens**: JPG, JPEG, PNG, GIF, WebP, SVG
- **Vídeos**: MP4, AVI, MOV, WMV, FLV, WebM
- **Áudios**: MP3, WAV, OGG, FLAC, AAC
- **Documentos**: PDF, DOC, DOCX, TXT, RTF
- **Arquivos**: ZIP, RAR, 7Z, TAR, GZ

## 📦 Instalação

### 1. O app já foi adicionado ao `INSTALLED_APPS`
```python
# core/settings.py
INSTALLED_APPS = [
    # ... outros apps
    "apps.media_storage",
    # ... resto dos apps
]
```

### 2. URLs já foram configuradas
```python
# core/urls.py
urlpatterns = [
    # ... outras URLs
    path('app/media/', include('apps.media_storage.urls')),
    # ... resto das URLs
]
```

### 3. Executar as migrações
```bash
# Ativar o ambiente virtual (se existir)
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Criar e aplicar migrações
python manage.py makemigrations media_storage
python manage.py migrate
```

### 4. Criar um superusuário (se necessário)
```bash
python manage.py createsuperuser
```

## 🎯 Como Usar

### 📊 Painel Administrativo Django
1. Acesse `/admin/`
2. Navegue para **Media Storage**
3. Gerencie **Categorias de Mídia** e **Arquivos de Mídia**

### 🖥️ Interface de Usuário
1. Acesse `/app/media/` (requer login de staff)
2. **Listagem**: Visualize todos os arquivos com filtros
3. **Upload**: Faça upload de arquivos individuais
4. **Upload em Lote**: Envie múltiplos arquivos de uma vez
5. **Limpeza**: Identifique e remova arquivos não utilizados

### 📋 Funcionalidades Principais

#### Upload de Arquivos
- Drag & drop suportado
- Preview automático
- Validação de tipo e tamanho
- Geração automática de metadados

#### Gerenciamento
- Edição de informações (título, descrição, tags)
- Controle de visibilidade (público/privado)
- Categorização
- Cópia de URLs

#### Busca e Filtros
- Busca por texto (título, descrição, tags)
- Filtro por categoria
- Filtro por tipo de arquivo
- Filtro por visibilidade

## 🗂️ Estrutura do Projeto

```
apps/media_storage/
├── __init__.py
├── admin.py              # Interface administrativa
├── apps.py               # Configuração do app
├── forms.py              # Formulários
├── models.py             # Modelos de dados
├── tests.py              # Testes unitários
├── urls.py               # URLs do app
├── views.py              # Views e lógica
├── migrations/           # Migrações do banco
├── templates/            # Templates HTML
│   └── media_storage/
│       ├── base.html
│       ├── list.html
│       ├── detail.html
│       ├── upload.html
│       ├── edit.html
│       ├── bulk_upload.html
│       ├── cleanup.html
│       └── cleanup_confirm.html
└── README.md
```

## 🔧 Modelos de Dados

### MediaCategory
- `name`: Nome da categoria
- `description`: Descrição
- `created_at`: Data de criação

### MediaFile
- `title`: Título do arquivo
- `description`: Descrição
- `file`: Arquivo físico
- `file_type`: Tipo (image, video, audio, document, other)
- `category`: Categoria (ForeignKey)
- `file_size`: Tamanho em bytes
- `mime_type`: Tipo MIME
- `width/height`: Dimensões (para imagens)
- `duration`: Duração (para vídeos/áudios)
- `uploaded_by`: Usuário que fez upload
- `uploaded_at/updated_at`: Timestamps
- `is_public`: Visibilidade
- `is_active`: Status ativo
- `tags`: Tags para busca

### MediaUsage
- `media_file`: Arquivo de mídia
- `content_type`: Tipo de conteúdo que usa o arquivo
- `object_id`: ID do objeto
- `field_name`: Nome do campo
- `created_at`: Data de uso

## 🛠️ APIs e Endpoints

### Views Principais
- `/app/media/` - Listagem de arquivos
- `/app/media/upload/` - Upload individual
- `/app/media/bulk-upload/` - Upload em lote
- `/app/media/<id>/` - Detalhes do arquivo
- `/app/media/<id>/edit/` - Editar arquivo
- `/app/media/<id>/delete/` - Deletar arquivo

### APIs AJAX
- `/app/media/ajax/upload/` - Upload via AJAX
- `/app/media/api/<id>/` - Informações do arquivo
- `/app/media/browser/` - Navegador de mídia (popup)

### Utilitários
- `/app/media/cleanup/` - Limpeza de arquivos
- `/app/media/serve/<path>/` - Servir arquivos (desenvolvimento)

## 🔒 Segurança

- **Autenticação**: Requer usuário staff
- **Validação**: Tipos de arquivo e tamanhos
- **Sanitização**: Limpeza de nomes de arquivo
- **Controle de Acesso**: Arquivos públicos/privados
- **CSRF Protection**: Proteção contra ataques CSRF

## 🎨 Interface

### Características da UI
- **Design Responsivo**: Bootstrap 5
- **Drag & Drop**: Upload intuitivo
- **Preview**: Visualização de arquivos
- **Filtros Dinâmicos**: Busca em tempo real
- **Feedback Visual**: Confirmações e erros
- **Copy-to-Clipboard**: URLs dos arquivos

### Componentes
- Cards de mídia com preview
- Modal de confirmação para exclusões
- Progress bars para uploads
- Badges de tipo de arquivo
- Estatísticas de uso

## 🧪 Testes

Execute os testes com:
```bash
python manage.py test apps.media_storage
```

### Cobertura de Testes
- Criação de arquivos de mídia
- Upload via formulário
- Views de listagem e detalhes
- Propriedades dos modelos
- Validações de formulário

## 📈 Performance

### Otimizações Implementadas
- **Indexes**: Campos frequentemente consultados
- **Select Related**: Redução de queries
- **Paginação**: Listagens grandes
- **Cache**: Headers de cache para arquivos
- **Lazy Loading**: Carregamento sob demanda

### Monitoramento
- Tamanho total de arquivos
- Contadores por tipo
- Arquivos não utilizados
- Estatísticas de uso

## 🔧 Configurações Avançadas

### Personalização de Upload
```python
# Em settings.py, você pode configurar:
MEDIA_ROOT = 'media/'
MEDIA_URL = '/media/'

# Tamanho máximo de arquivo (padrão: 100MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
```

### Integração com Outros Apps
O sistema de `MediaUsage` permite rastrear onde os arquivos são utilizados:

```python
from apps.media_storage.models import MediaUsage

# Registrar uso de um arquivo
MediaUsage.objects.create(
    media_file=media_file,
    content_type='news',
    object_id=news_id,
    field_name='featured_image'
)
```

## 🚀 Próximos Passos

1. **Execute as migrações** para criar as tabelas
2. **Acesse o admin** para criar categorias
3. **Teste o upload** de alguns arquivos
4. **Configure permissões** conforme necessário
5. **Integre com outros apps** do seu sistema

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do Django
2. Confirme as permissões de arquivo
3. Teste com diferentes tipos de arquivo
4. Verifique as configurações de MEDIA_ROOT

---

**Desenvolvido para o sistema PDL** - Sistema completo de gerenciamento de mídia para aplicações Django.

---

[ Voltar ao Índice](../INDEX.md)

