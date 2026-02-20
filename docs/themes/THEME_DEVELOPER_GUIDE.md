# Guia do Desenvolvedor: Recursos do Sistema de Temas PDL

## 📋 Índice
1. [Variáveis do Sistema](#variaveis-sistema)
2. [Context Processors](#context-processors)
3. [URLs e Views Disponíveis](#urls-views)
4. [Templates e Herança](#templates-heranca)
5. [Sistema de Renderização](#sistema-renderizacao)
6. [Assets e Recursos Estáticos](#assets-recursos)
7. [Internacionalização](#internacionalizacao)
8. [Configurações do Projeto](#configuracoes-projeto)
9. [Funcionalidades Especiais](#funcionalidades-especiais)
10. [Limitações e Restrições](#limitacoes-restricoes)

---

## 🔧 Variáveis do Sistema {#variaveis-sistema}

### Variáveis Automáticas do Context Processor

O sistema injeta automaticamente estas variáveis em todos os templates:

```django
<!-- Informações do Tema Ativo -->
{{ active_theme }}          # Slug do tema ativo (ex: "l2-ethernal-templar")
{{ theme_slug }}            # Mesmo que active_theme
{{ path_theme }}            # Caminho para assets do tema (/themes/installed/nome-tema)
{{ base_template }}         # Template base a ser usado
{{ theme_files }}           # Dict com arquivos do tema

<!-- Background Ativo -->
{{ background_url }}        # URL da imagem de background ativa

<!-- Configurações do Projeto -->
{{ PROJECT_TITLE }}         # Título do projeto
{{ PROJECT_AUTHOR }}        # Autor do projeto
{{ PROJECT_DESCRIPTION }}   # Descrição do projeto
{{ PROJECT_KEYWORDS }}      # Palavras-chave
{{ PROJECT_URL }}           # URL base do projeto
{{ PROJECT_LOGO_URL }}      # URL do logo
{{ PROJECT_FAVICON_ICO }}   # URL do favicon
{{ PROJECT_FAVICON_MANIFEST }} # URL do manifest
{{ PROJECT_THEME_COLOR }}   # Cor do tema
{{ PROJECT_DISCORD_URL }}   # URL do Discord
{{ PROJECT_YOUTUBE_URL }}   # URL do YouTube
{{ PROJECT_FACEBOOK_URL }}  # URL do Facebook
{{ PROJECT_INSTAGRAM_URL }} # URL do Instagram
{{ project_name }}          # Nome do projeto
{{ version }}               # Versão do sistema

<!-- Configurações de Login Social -->
{{ SOCIAL_LOGIN_ENABLED }}           # Login social habilitado
{{ SOCIAL_LOGIN_GOOGLE_ENABLED }}    # Google habilitado
{{ SOCIAL_LOGIN_GITHUB_ENABLED }}    # GitHub habilitado
{{ SOCIAL_LOGIN_DISCORD_ENABLED }}   # Discord habilitado
{{ SOCIAL_LOGIN_SHOW_SECTION }}      # Mostrar seção de login social

<!-- Slogan -->
{{ SHOW_SLOGAN }}           # Mostrar slogan
```

### Variáveis do Tema (Customizadas)

Suas variáveis definidas no `theme.json` ficam disponíveis com o prefixo do slug:

```django
<!-- Se seu tema tem slug "meu-tema" -->
{{ meu_tema_nome_da_variavel }}
{{ meu_tema_primary_color }}
{{ meu_tema_welcome_text }}
{{ meu_tema_show_hero }}

<!-- Exemplo prático -->
<h1>{{ meu_tema_hero_title }}</h1>
<div style="color: {{ meu_tema_primary_color }}">Texto colorido</div>
{% if meu_tema_show_server_status %}
    <div class="server-status">Online</div>
{% endif %}
```

---

## 🎯 Context Processors {#context-processors}

### active_theme
Injeta informações do tema ativo:
```python
{
    'active_theme': 'nome-do-tema',
    'base_template': 'installed/nome-do-tema/base.html',
    'theme_slug': 'nome-do-tema',
    'path_theme': '/themes/installed/nome-do-tema',
    'theme_files': {...}
}
```

### theme_variables
Injeta todas as variáveis do tema com conversão de tipo:
```python
# Para cada variável no theme.json
{
    'meu_tema_texto': 'valor em texto',
    'meu_tema_numero': 123,  # Convertido para int
    'meu_tema_booleano': True  # Convertido para boolean
}
```

### project_metadata
Injeta configurações do projeto:
```python
{
    'PROJECT_TITLE': '...',
    'PROJECT_DESCRIPTION': '...',
    # ... todas as configurações
}
```

### background_setting
Injeta background ativo:
```python
{
    'background_url': '/media/backgrounds/bg.jpg'
}
```

---

## 🔗 URLs e Views Disponíveis {#urls-views}

### URLs Públicas Principais
```django
{% url 'index' %}                    # Página inicial
{% url 'public_news_list' %}         # Lista de notícias
{% url 'public_faq_list' %}          # Lista de FAQ
{% url 'downloads:download_list' %}  # Lista de downloads
{% url 'register' %}                 # Registro
{% url 'login' %}                    # Login
{% url 'dashboard' %}                # Dashboard (se autenticado)
```

### URLs de Apps Específicos
```django
<!-- Lineage Apps -->
{% url 'lineage:server:server_list' %}      # Lista de servidores
{% url 'lineage:games:game_list' %}         # Lista de jogos
{% url 'lineage:shop:shop_list' %}          # Loja
{% url 'lineage:auction:auction_list' %}    # Leilões
{% url 'lineage:wiki:wiki_list' %}          # Wiki
{% url 'lineage:tops:tops_list' %}          # Rankings
{% url 'lineage:wallet:wallet_view' %}      # Carteira
{% url 'lineage:payment:payment_list' %}    # Pagamentos

<!-- Main Apps -->
{% url 'main:news:news_list' %}             # Notícias
{% url 'main:faq:faq_list' %}               # FAQ
{% url 'main:downloads:download_list' %}    # Downloads
{% url 'main:message:message_list' %}       # Mensagens
{% url 'main:notification:notification_list' %} # Notificações
```

### Verificação de Autenticação
```django
{% if user.is_authenticated %}
    <!-- Usuário logado -->
    <a href="{% url 'dashboard' %}">Dashboard</a>
    <a href="{% url 'logout' %}">Sair</a>
{% else %}
    <!-- Usuário não logado -->
    <a href="{% url 'login' %}">Entrar</a>
    <a href="{% url 'register' %}">Registrar</a>
{% endif %}
```

---

## 📄 Templates e Herança {#templates-heranca}

### Sistema de Herança
```django
<!-- Seu template herda do template base do tema -->
{% extends 'layouts/public.html' %}

<!-- O layouts/public.html herda do base_template -->
<!-- Que pode ser: -->
<!-- - installed/nome-tema/base.html (se tema ativo) -->
<!-- - layouts/base-default.html (se sem tema) -->
```

### Blocos Disponíveis
```django
{% block extrahead %}
    <!-- CSS adicional, meta tags, etc -->
{% endblock %}

{% block content %}
    <!-- Conteúdo principal da página -->
{% endblock %}

{% block extrajs %}
    <!-- JavaScript adicional -->
{% endblock %}

{% block extrastyle %}
    <!-- CSS inline adicional -->
{% endblock %}
```

### Renderização Condicional
```django
<!-- Verifica se arquivo existe no tema -->
{% if 'custom-page.html' in theme_files %}
    {% include 'installed/'|add:theme_slug|add:'/custom-page.html' %}
{% else %}
    <!-- Fallback para template padrão -->
    {% include 'public/custom-page.html' %}
{% endif %}
```

---

## 🎨 Sistema de Renderização {#sistema-renderizacao}

### Função render_theme_page
```python
# Em suas views
from utils.render_theme_page import render_theme_page

def minha_view(request):
    context = {
        'dados': meus_dados,
        'outras_variaveis': valores
    }
    
    # Tenta renderizar do tema, fallback para padrão
    return render_theme_page(request, 'public', 'minha-pagina.html', context)
```

### Comportamento
1. **Tema Ativo**: Renderiza `installed/nome-tema/minha-pagina.html`
2. **Sem Tema**: Renderiza `public/minha-pagina.html`
3. **Contexto**: Combina seu context + context processors

### View serve_theme_file
```python
# Serve arquivos HTML do tema ativo
# URL: /admin/serve-theme-file/<nome_arquivo>/
# Exemplo: /admin/serve-theme-file/terms/
```

---

## 🖼️ Assets e Recursos Estáticos {#assets-recursos}

### Caminhos de Assets
```django
<!-- CSS -->
<link href="{{ path_theme }}/css/style.css" rel="stylesheet">
<link href="{{ path_theme }}/css/main.css" rel="stylesheet">

<!-- JavaScript -->
<script src="{{ path_theme }}/js/script.js"></script>
<script src="{{ path_theme }}/js/custom.js"></script>

<!-- Imagens -->
<img src="{{ path_theme }}/images/logo.png" alt="Logo">
<img src="{{ path_theme }}/images/bg/main.jpg" alt="Background">

<!-- Fontes -->
@font-face {
    font-family: 'CustomFont';
    src: url('{{ path_theme }}/font/custom-font.woff2') format('woff2');
}
```

### Extensões Suportadas
- **HTML**: `.html`, `.htm`
- **CSS**: `.css`, `.scss`, `.sass`, `.less`
- **JS**: `.js`, `.ts`, `.map`, `.mjs`, `.cjs`
- **Imagens**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`, `.tiff`
- **Fontes**: `.woff`, `.woff2`, `.ttf`, `.otf`, `.eot`
- **Multimídia**: `.mp4`, `.webm`, `.mp3`, `.ogg`
- **Outros**: `.md`, `.txt`, `.pdf`

### Estrutura Recomendada
```
seu-tema/
├── css/
│   ├── style.css
│   ├── main.css
│   └── media.css
├── js/
│   ├── script.js
│   └── custom.js
├── images/
│   ├── logo.png
│   ├── bg/
│   └── icons/
├── font/
└── scss/ (opcional)
```

---

## 🌍 Internacionalização {#internacionalizacao}

### Variáveis Multilíngue
```json
{
    "variables": [
        {
            "name": "welcome_text",
            "tipo": "string",
            "valor_pt": "Bem-vindo",
            "valor_en": "Welcome",
            "valor_es": "Bienvenido"
        }
    ]
}
```

### Uso nos Templates
```django
<!-- O sistema automaticamente usa o idioma correto -->
<h1>{{ meu_tema_welcome_text }}</h1>

<!-- Idioma atual -->
{{ LANGUAGE_CODE }}  # 'pt-br', 'en', 'es'
{{ LANGUAGE_NAME }}  # 'Português', 'English', 'Español'
```

### Tags de Tradução
```django
{% load i18n %}

<!-- Tradução direta -->
{% trans "Texto para traduzir" %}

<!-- Tradução com variáveis -->
{% blocktrans with name=user.name %}
    Olá {{ name }}, bem-vindo!
{% endblocktrans %}

<!-- Tradução de URLs -->
{% url 'index' as home_url %}
<a href="{{ home_url }}">{% trans "Início" %}</a>
```

---

## ⚙️ Configurações do Projeto {#configuracoes-projeto}

### Configurações Disponíveis
```django
<!-- Metadados -->
{{ PROJECT_TITLE }}         # Título do site
{{ PROJECT_DESCRIPTION }}   # Meta description
{{ PROJECT_KEYWORDS }}      # Meta keywords
{{ PROJECT_URL }}           # URL base

<!-- Assets -->
{{ PROJECT_LOGO_URL }}      # Logo principal
{{ PROJECT_FAVICON_ICO }}   # Favicon
{{ PROJECT_FAVICON_MANIFEST }} # Manifest PWA
{{ PROJECT_THEME_COLOR }}   # Cor do tema

<!-- Redes Sociais -->
{{ PROJECT_DISCORD_URL }}   # Discord
{{ PROJECT_YOUTUBE_URL }}   # YouTube
{{ PROJECT_FACEBOOK_URL }}  # Facebook
{{ PROJECT_INSTAGRAM_URL }} # Instagram

<!-- Sistema -->
{{ project_name }}          # Nome do projeto
{{ version }}               # Versão atual
```

### Uso Prático
```django
<!-- Meta tags -->
<title>{{ PROJECT_TITLE }}</title>
<meta name="description" content="{{ PROJECT_DESCRIPTION }}">
<meta name="keywords" content="{{ PROJECT_KEYWORDS }}">

<!-- Open Graph -->
<meta property="og:title" content="{{ PROJECT_TITLE }}">
<meta property="og:description" content="{{ PROJECT_DESCRIPTION }}">
<meta property="og:image" content="{{ PROJECT_LOGO_URL }}">

<!-- Links sociais -->
<a href="{{ PROJECT_DISCORD_URL }}" target="_blank">Discord</a>
<a href="{{ PROJECT_YOUTUBE_URL }}" target="_blank">YouTube</a>

<!-- Favicon -->
<link rel="icon" href="{{ PROJECT_FAVICON_ICO }}">
<link rel="manifest" href="{{ PROJECT_FAVICON_MANIFEST }}">
<meta name="theme-color" content="{{ PROJECT_THEME_COLOR }}">
```

---

## 🚀 Funcionalidades Especiais {#funcionalidades-especiais}

### Background Dinâmico
```django
<!-- Background configurado no admin -->
<div class="hero" style="background-image: url('{{ background_url }}')">
    <!-- Conteúdo -->
</div>

<!-- Fallback para background padrão -->
<div class="hero" style="background-image: url('{% if background_url %}{{ background_url }}{% else %}{{ path_theme }}/images/bg/default.jpg{% endif %}')">
```

### Sistema de Notificações
```django
<!-- Inclui sistema de mensagens -->
{% include 'includes/messages.html' %}

<!-- Inclui sistema de notificações -->
{% include 'includes/notification.html' %}
```

### Login Social
```django
<!-- Verifica se login social está habilitado -->
{% if SOCIAL_LOGIN_ENABLED %}
    <div class="social-login">
        {% if SOCIAL_LOGIN_GOOGLE_ENABLED %}
            <a href="{% url 'social:begin' 'google-oauth2' %}">Google</a>
        {% endif %}
        
        {% if SOCIAL_LOGIN_DISCORD_ENABLED %}
            <a href="{% url 'social:begin' 'discord' %}">Discord</a>
        {% endif %}
    </div>
{% endif %}
```

### Slogan Condicional
```django
<!-- Mostra slogan se habilitado -->
{% if SHOW_SLOGAN %}
    <div class="slogan">
        <p>Seu slogan aqui</p>
    </div>
{% endif %}
```

### Verificação de Tema Ativo
```django
<!-- Verifica se há tema ativo -->
{% if active_theme %}
    <!-- Tema personalizado ativo -->
    <link href="{{ path_theme }}/css/custom.css" rel="stylesheet">
{% else %}
    <!-- Usando tema padrão -->
    <link href="{% static 'default/css/main.css' %}" rel="stylesheet">
{% endif %}
```

---

## ⚠️ Limitações e Restrições {#limitacoes-restricoes}

### Restrições de Segurança
- **Tamanho máximo**: 30MB por ZIP
- **Extensões permitidas**: Apenas as listadas acima
- **Path traversal**: Bloqueado automaticamente
- **Execução de código**: Não é possível executar PHP, Python, etc.

### Limitações Técnicas
- **Apenas um tema ativo**: Não é possível ter múltiplos temas
- **Fallback automático**: Se arquivo não existe no tema, usa padrão
- **Cache**: Variáveis são cacheadas, pode precisar limpar cache
- **Context processors**: Sempre executados, não podem ser desabilitados

### Validações Obrigatórias
```json
// theme.json deve ter:
{
    "name": "string obrigatório",
    "slug": "string obrigatório",
    "variables": "array opcional"
}
```

### Comportamentos do Sistema
- **Ativação**: Quando um tema é ativado, outros são desativados
- **Exclusão**: Ao deletar tema, arquivos são removidos automaticamente
- **Validação**: ZIP é validado antes da extração
- **Slug**: Convertido automaticamente para formato seguro

---

## 💡 Dicas de Desenvolvimento

### Debug de Variáveis
```django
<!-- Debug no template -->
{{ active_theme|pprint }}
{{ theme_files|pprint }}

<!-- Verificar se variável existe -->
{% if meu_tema_variavel %}
    {{ meu_tema_variavel }}
{% else %}
    Variável não encontrada
{% endif %}
```

### Verificação de Arquivos
```django
<!-- Verificar se arquivo existe no tema -->
{% if 'custom.css' in theme_files %}
    <link href="{{ path_theme }}/css/custom.css" rel="stylesheet">
{% endif %}
```

### Fallback Inteligente
```django
<!-- Fallback para diferentes cenários -->
{% if active_theme %}
    {% if 'hero-bg.jpg' in theme_files %}
        <img src="{{ path_theme }}/images/hero-bg.jpg">
    {% else %}
        <img src="{% static 'default/images/hero-bg.jpg' %}">
    {% endif %}
{% else %}
    <img src="{% static 'default/images/hero-bg.jpg' %}">
{% endif %}
```

### Performance
```django
<!-- Carregamento condicional de recursos pesados -->
{% if meu_tema_load_heavy_assets %}
    <script src="{{ path_theme }}/js/heavy-library.js"></script>
{% endif %}
```

---

## 📚 Recursos de Referência

### Arquivos do Sistema
- `core/context_processors.py` - Processadores de contexto
- `apps/main/administrator/models.py` - Modelos Theme e ThemeVariable
- `utils/render_theme_page.py` - Função de renderização
- `docs/THEME_SYSTEM.md` - Documentação técnica
- `docs/THEME_SYSTEM_FLOW_DIAGRAM.md` - Fluxo do sistema

### Exemplo Funcional
- `themes/installed/l2-ethernal-templar/` - Tema completo de exemplo

### Comandos Úteis
```bash
# Limpar cache de templates
python manage.py clearcache

# Verificar temas instalados
ls themes/installed/

# Verificar variáveis no shell
python manage.py shell
>>> from apps.main.administrator.models import ThemeVariable
>>> ThemeVariable.objects.all()
```

---

*Este guia foca nos recursos específicos do sistema de temas do PDL. Para dicas de HTML/CSS/JS, consulte a documentação padrão dessas tecnologias.* 