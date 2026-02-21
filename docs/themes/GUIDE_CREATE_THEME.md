# Guia Completo: Como Criar Temas para o PDL

> **Última atualização:** 21/02/2026

## 📋 Índice
1. [Visão Geral do Sistema de Temas](#visão-geral)
2. [Estrutura de Arquivos do Tema](#estrutura)
3. [Arquivo theme.json](#theme-json)
4. [Templates HTML](#templates)
5. [Estilos CSS/SCSS](#estilos)
6. [JavaScript](#javascript)
7. [Assets e Recursos](#assets)
8. [Variáveis de Tema](#variaveis)
9. [Processo de Instalação](#instalacao)
10. [Exemplos Práticos](#exemplos)
11. [Boas Práticas](#boas-praticas)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral do Sistema de Temas {#visão-geral}

O PDL (Private Development Lineage) possui um sistema de temas robusto que permite personalização completa da aparência do site. Cada tema é um pacote ZIP contendo:

- **Templates HTML**: Páginas personalizadas
- **Estilos CSS/SCSS**: Design visual
- **JavaScript**: Interatividade
- **Assets**: Imagens, fontes, ícones
- **Configuração**: Arquivo `theme.json` com metadados e variáveis

### Como Funciona
1. **Upload**: Admin faz upload do ZIP do tema
2. **Validação**: Sistema verifica estrutura e arquivos
3. **Extração**: Arquivos são extraídos para `themes/installed/<slug>/`
4. **Ativação**: Apenas um tema pode estar ativo por vez
5. **Renderização**: Templates do tema ativo são usados automaticamente

---

## 📁 Estrutura de Arquivos do Tema {#estrutura}

```
meu-tema.zip
├── theme.json                 # OBRIGATÓRIO - Configuração do tema
├── base.html                  # OBRIGATÓRIO - Template base
├── index.html                 # Página inicial personalizada
├── css/
│   ├── style.css
│   ├── main.css
│   └── media.css
├── scss/
│   ├── style.scss
│   ├── main.scss
│   └── media.scss
├── js/
│   ├── script.js
│   └── custom.js
├── images/
│   ├── logo.png
│   ├── bg/
│   │   └── main.jpg
│   └── characters/
│       └── about.png
└── font/
    └── custom-font.woff2
```

### Extensões Permitidas
- **HTML**: `.html`, `.htm`
- **CSS**: `.css`, `.scss`, `.sass`, `.less`
- **JavaScript**: `.js`, `.ts`, `.map`, `.mjs`, `.cjs`
- **Imagens**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`, `.tiff`
- **Fontes**: `.woff`, `.woff2`, `.ttf`, `.otf`, `.eot`
- **Multimídia**: `.mp4`, `.webm`, `.mp3`, `.ogg`
- **Outros**: `.md`, `.txt`, `.pdf`

---

## ⚙️ Arquivo theme.json {#theme-json}

O arquivo `theme.json` é **OBRIGATÓRIO** e contém todas as configurações do tema:

```json
{
    "name": "Nome do Tema",
    "slug": "nome-do-tema",
    "author": "Seu Nome",
    "description": "Descrição detalhada do tema",
    "version": "1.0.0",
    "variables": [
        {
            "name": "main",
            "tipo": "string",
            "valor_pt": "Principal",
            "valor_en": "Main",
            "valor_es": "Principal"
        },
        {
            "name": "primary_color",
            "tipo": "string",
            "valor_pt": "#ff6b35",
            "valor_en": "#ff6b35",
            "valor_es": "#ff6b35"
        },
        {
            "name": "show_hero",
            "tipo": "boolean",
            "valor_pt": "true",
            "valor_en": "true",
            "valor_es": "true"
        }
    ]
}
```

### Campos Obrigatórios
- **name**: Nome do tema
- **slug**: Identificador único (usado para URLs e variáveis)

### Campos Opcionais
- **author**: Autor do tema
- **description**: Descrição detalhada
- **version**: Versão do tema

### Tipos de Variáveis
- **string**: Texto simples
- **int**: Número inteiro
- **boolean**: Verdadeiro/falso

---

## 🎨 Templates HTML {#templates}

### Template Base (base.html)

O `base.html` é o template principal que define a estrutura HTML:

```html
{% load static i18n %}
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ PROJECT_TITLE }}</title>
    
    <!-- Meta Tags -->
    <meta name="description" content="{{ PROJECT_DESCRIPTION }}">
    <meta name="keywords" content="{{ PROJECT_KEYWORDS }}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{{ PROJECT_TITLE }}">
    <meta property="og:description" content="{{ PROJECT_DESCRIPTION }}">
    <meta property="og:image" content="{{ PROJECT_LOGO_URL }}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{{ PROJECT_FAVICON_ICO }}">
    
    <!-- CSS do Tema -->
    <link href="{{ path_theme }}/css/style.css" rel="stylesheet">
    <link href="{{ path_theme }}/css/main.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    
    {% block extrahead %}{% endblock %}
</head>

<body>
    <!-- Navegação -->
    <nav class="theme-nav">
        <div class="nav-container">
            <div class="logo">
                <a href="/">
                    <img src="{{ path_theme }}/images/logo.png" alt="Logo">
                </a>
            </div>
            
            <ul class="nav-menu">
                <li><a href="{% url 'index' %}">{{ meu_tema_main }}</a></li>
                <li><a href="{% url 'index' %}#about">{{ meu_tema_about }}</a></li>
                <li><a href="{% url 'public_news_list' %}">{{ meu_tema_news }}</a></li>
                <li><a href="{% url 'public_faq_list' %}">{{ meu_tema_faq }}</a></li>
                
                {% if user.is_authenticated %}
                    <li><a href="{% url 'dashboard' %}">{{ meu_tema_minha_conta }}</a></li>
                {% else %}
                    <li><a href="{% url 'register' %}">{{ meu_tema_register }}</a></li>
                {% endif %}
            </ul>
        </div>
    </nav>

    <!-- Conteúdo Principal -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="theme-footer">
        <div class="footer-content">
            <p>&copy; 2024 {{ PROJECT_TITLE }}. Todos os direitos reservados.</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script src="{{ path_theme }}/js/script.js"></script>
    {% block extrajs %}{% endblock %}
</body>
</html>
```

### Página Inicial (index.html)

*(**Nota:** Esta página recebe um aglomerado massivo de dados únicos do servidor, como contadores, clãs e status dinâmico. [Acesse o THEME_INDEX_CONTEXT.md](THEME_INDEX_CONTEXT.md) para ver a lista de todas as variáveis de contexto e exemplos.)*

```html
{% extends 'layouts/public.html' %}
{% load static i18n %}

{% block extrahead %}
<style>
    .hero {
        background-image: url('{{ path_theme }}/images/bg/main.jpg');
    }
</style>
{% endblock %}

{% block content %}
<!-- Seção Hero -->
<section class="hero">
    <div class="hero-content">
        <h1 class="hero-title">{{ meu_tema_welcome_title }}</h1>
        <p class="hero-subtitle">{{ meu_tema_welcome_subtitle }}</p>
        
        <div class="hero-buttons">
            <a href="{% url 'downloads:download_list' %}" class="btn btn-primary">
                {{ meu_tema_download }}
            </a>
            
            {% if not user.is_authenticated %}
                <a href="{% url 'register' %}" class="btn btn-secondary">
                    {{ meu_tema_create_account }}
                </a>
            {% endif %}
        </div>
    </div>
</section>

<!-- Seção Sobre -->
<section id="about" class="about">
    <div class="container">
        <h2>{{ meu_tema_about_title }}</h2>
        <p>{{ meu_tema_about_description }}</p>
    </div>
</section>

<!-- Seção Notícias -->
<section class="news">
    <div class="container">
        <h2>{{ meu_tema_news_title }}</h2>
        <!-- Lista de notícias aqui -->
    </div>
</section>
{% endblock %}
```

### Variáveis Disponíveis no Contexto

O sistema injeta automaticamente estas variáveis nos templates:

- **Variáveis do Tema**: `{{ meu_tema_nome_da_variavel }}`
- **Configurações do Projeto**: `{{ PROJECT_TITLE }}`, `{{ PROJECT_DESCRIPTION }}`, etc.
- **Caminho do Tema**: `{{ path_theme }}`
- **Slug do Tema**: `{{ theme_slug }}`
- **Background**: `{{ background_url }}`

---

## 🎨 Estilos CSS/SCSS {#estilos}

### Estrutura CSS Recomendada

```css
/* style.css - Estilos principais */
:root {
    --primary-color: #ff6b35;
    --secondary-color: #2c3e50;
    --text-color: #333;
    --bg-color: #fff;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
}

/* Navegação */
.theme-nav {
    background: var(--primary-color);
    padding: 1rem 0;
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-menu a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.3s;
}

.nav-menu a:hover {
    opacity: 0.8;
}

/* Hero Section */
.hero {
    height: 100vh;
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
}

.hero-content {
    max-width: 800px;
    padding: 2rem;
}

.hero-title {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero-subtitle {
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

/* Botões */
.btn {
    display: inline-block;
    padding: 12px 24px;
    border-radius: 5px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s;
    margin: 0 10px;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-secondary {
    background: transparent;
    color: white;
    border: 2px solid white;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

/* Responsividade */
@media (max-width: 768px) {
    .nav-menu {
        display: none;
    }
    
    .hero-title {
        font-size: 2rem;
    }
}
```

### SCSS (Opcional)

Se preferir usar SCSS, você pode compilar para CSS:

```scss
// _variables.scss
$primary-color: #ff6b35;
$secondary-color: #2c3e50;
$text-color: #333;
$bg-color: #fff;

// _mixins.scss
@mixin flex-center {
    display: flex;
    align-items: center;
    justify-content: center;
}

@mixin responsive($breakpoint) {
    @if $breakpoint == mobile {
        @media (max-width: 768px) { @content; }
    }
    @if $breakpoint == tablet {
        @media (max-width: 1024px) { @content; }
    }
}

// main.scss
@import 'variables';
@import 'mixins';

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: $text-color;
    background-color: $bg-color;
}

.hero {
    height: 100vh;
    background-size: cover;
    background-position: center;
    @include flex-center;
    text-align: center;
    color: white;
    
    @include responsive(mobile) {
        height: 70vh;
    }
}
```

---

## ⚡ JavaScript {#javascript}

### script.js - Funcionalidades Básicas

```javascript
// Aguarda o DOM carregar
document.addEventListener('DOMContentLoaded', function() {
    
    // Navegação suave para âncoras
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Menu mobile toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Animação de scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observa elementos para animação
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    animateElements.forEach(el => observer.observe(el));

    // Contador de servidores (exemplo)
    function updateServerStatus() {
        const serverElements = document.querySelectorAll('.server-status');
        serverElements.forEach(element => {
            const status = element.dataset.status;
            if (status === 'online') {
                element.classList.add('online');
                element.textContent = 'Online';
            } else {
                element.classList.add('offline');
                element.textContent = 'Offline';
            }
        });
    }

    updateServerStatus();

    // Lazy loading de imagens
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
});

// Funções utilitárias
function showNotification(message, type = 'info') {
    // Implementar sistema de notificações
    console.log(`${type}: ${message}`);
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
```

---

## 🖼️ Assets e Recursos {#assets}

### Estrutura de Pastas Recomendada

```
images/
├── logo.png              # Logo principal
├── favicon.ico           # Favicon
├── bg/                   # Imagens de fundo
│   ├── main.jpg
│   ├── about.jpg
│   └── contact.jpg
├── characters/           # Personagens do jogo
│   ├── hero.png
│   └── about.png
├── icons/                # Ícones
│   ├── download.svg
│   ├── server.svg
│   └── community.svg
└── ui/                   # Elementos de interface
    ├── button-bg.png
    └── card-bg.png

font/
├── custom-font.woff2     # Fonte personalizada
└── custom-font.woff      # Fallback
```

### Otimização de Imagens

- **Formatos**: Use WebP para melhor compressão
- **Tamanhos**: Otimize para diferentes resoluções
- **Lazy Loading**: Implemente carregamento sob demanda
- **Compressão**: Reduza o tamanho dos arquivos

### Exemplo de Uso no CSS

```css
/* Carregamento de fontes personalizadas */
@font-face {
    font-family: 'CustomFont';
    src: url('../font/custom-font.woff2') format('woff2'),
         url('../font/custom-font.woff') format('woff');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}

/* Aplicação da fonte */
body {
    font-family: 'CustomFont', 'Arial', sans-serif;
}

/* Imagens de fundo */
.hero {
    background-image: url('../images/bg/main.jpg');
}

.about-section {
    background-image: url('../images/bg/about.jpg');
}
```

---

## 🔧 Variáveis de Tema {#variaveis}

### Definição no theme.json

```json
{
    "variables": [
        {
            "name": "primary_color",
            "tipo": "string",
            "valor_pt": "#ff6b35",
            "valor_en": "#ff6b35",
            "valor_es": "#ff6b35"
        },
        {
            "name": "hero_title",
            "tipo": "string",
            "valor_pt": "Bem-vindo ao Lineage 2",
            "valor_en": "Welcome to Lineage 2",
            "valor_es": "Bienvenido a Lineage 2"
        },
        {
            "name": "show_server_status",
            "tipo": "boolean",
            "valor_pt": "true",
            "valor_en": "true",
            "valor_es": "true"
        },
        {
            "name": "max_players",
            "tipo": "int",
            "valor_pt": "10000",
            "valor_en": "10000",
            "valor_es": "10000"
        }
    ]
}
```

### Uso nos Templates

```html
<!-- Texto simples -->
<h1>{{ meu_tema_hero_title }}</h1>

<!-- Cor no CSS -->
<style>
    :root {
        --primary-color: {{ meu_tema_primary_color }};
    }
</style>

<!-- Condicional -->
{% if meu_tema_show_server_status %}
    <div class="server-status">
        <span>Jogadores Online: {{ meu_tema_max_players }}</span>
    </div>
{% endif %}

<!-- Em JavaScript -->
<script>
    const primaryColor = '{{ meu_tema_primary_color }}';
    const maxPlayers = {{ meu_tema_max_players }};
</script>
```

### Variáveis do Sistema

Além das suas variáveis, o sistema fornece:

```html
<!-- Configurações do projeto -->
<title>{{ PROJECT_TITLE }}</title>
<meta name="description" content="{{ PROJECT_DESCRIPTION }}">

<!-- Caminhos do tema -->
<img src="{{ path_theme }}/images/logo.png" alt="Logo">

<!-- Background ativo -->
<div class="bg" style="background-image: url('{{ background_url }}')"></div>

<!-- URLs do projeto -->
<a href="{{ PROJECT_DISCORD_URL }}">Discord</a>
<a href="{{ PROJECT_YOUTUBE_URL }}">YouTube</a>
```

---

## 📦 Processo de Instalação {#instalacao}

### 1. Preparação do ZIP

1. **Crie a estrutura de pastas** conforme mostrado acima
2. **Adicione o arquivo `theme.json`** com todas as configurações
3. **Teste localmente** antes de empacotar
4. **Compacte tudo** em um arquivo ZIP

### 2. Upload no Admin

1. Acesse o painel administrativo
2. Vá para **Temas** > **Adicionar Tema**
3. Faça upload do arquivo ZIP
4. O sistema validará automaticamente

### 3. Validação Automática

O sistema verifica:
- ✅ Arquivo `theme.json` presente
- ✅ Campos obrigatórios preenchidos
- ✅ Extensões de arquivo permitidas
- ✅ Tamanho máximo (50MB)
- ✅ Segurança contra path traversal

### 4. Ativação

1. Após upload bem-sucedido, o tema aparece na lista
2. Clique em **Ativar** para usar o tema
3. Outros temas são automaticamente desativados

### 5. Verificação

- Acesse o site para ver o tema ativo
- Verifique se todas as variáveis estão funcionando
- Teste em diferentes idiomas
- Confirme responsividade

---

## 💡 Exemplos Práticos {#exemplos}

### Exemplo 1: Tema Minimalista

**theme.json:**
```json
{
    "name": "Minimalist Theme",
    "slug": "minimalist",
    "author": "Designer",
    "description": "Tema limpo e minimalista",
    "version": "1.0.0",
    "variables": [
        {
            "name": "accent_color",
            "tipo": "string",
            "valor_pt": "#3498db",
            "valor_en": "#3498db",
            "valor_es": "#3498db"
        }
    ]
}
```

**base.html:**
```html
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ PROJECT_TITLE }}</title>
    <link href="{{ path_theme }}/css/style.css" rel="stylesheet">
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">{{ PROJECT_TITLE }}</a>
            <ul>
                <li><a href="{% url 'index' %}">Home</a></li>
                <li><a href="{% url 'public_news_list' %}">News</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2024 {{ PROJECT_TITLE }}</p>
    </footer>
</body>
</html>
```

### Exemplo 2: Tema Gaming

**theme.json:**
```json
{
    "name": "Gaming Theme",
    "slug": "gaming",
    "author": "Gamer",
    "description": "Tema com estilo gaming",
    "version": "1.0.0",
    "variables": [
        {
            "name": "neon_color",
            "tipo": "string",
            "valor_pt": "#00ff41",
            "valor_en": "#00ff41",
            "valor_es": "#00ff41"
        },
        {
            "name": "show_particles",
            "tipo": "boolean",
            "valor_pt": "true",
            "valor_en": "true",
            "valor_es": "true"
        }
    ]
}
```

---

## ✅ Boas Práticas {#boas-praticas}

### 1. Organização de Código

- **Separe responsabilidades**: CSS, JS e HTML em arquivos diferentes
- **Use nomes descritivos**: Para classes, IDs e variáveis
- **Comente o código**: Explique funcionalidades complexas
- **Mantenha consistência**: Padrões de nomenclatura

### 2. Performance

- **Otimize imagens**: Use formatos modernos (WebP)
- **Minifique CSS/JS**: Reduza tamanho dos arquivos
- **Lazy loading**: Carregue recursos sob demanda
- **Cache**: Configure headers apropriados

### 3. Acessibilidade

- **Contraste adequado**: Texto legível
- **Navegação por teclado**: Suporte a Tab
- **Alt text**: Para imagens
- **Semântica HTML**: Use tags apropriadas

### 4. Responsividade

- **Mobile-first**: Comece pelo mobile
- **Breakpoints consistentes**: 768px, 1024px, 1200px
- **Teste em dispositivos**: Diferentes tamanhos de tela
- **Touch-friendly**: Botões adequados para touch

### 5. Internacionalização

- **Use variáveis**: Para todos os textos
- **Teste idiomas**: PT, EN, ES
- **Considerações culturais**: Cores e símbolos
- **RTL**: Se necessário

### 6. Segurança

- **Validação**: Sempre valide inputs
- **Escape**: Escape dados dinâmicos
- **HTTPS**: Use recursos seguros
- **CSP**: Content Security Policy

---

## 🔧 Troubleshooting {#troubleshooting}

### Problemas Comuns

#### 1. Tema não aparece após upload
**Solução:**
- Verifique se o `theme.json` está na raiz do ZIP
- Confirme se os campos obrigatórios estão preenchidos
- Verifique o log de erros do Django

#### 2. Variáveis não funcionam
**Solução:**
- Confirme o formato do `theme.json`
- Verifique se o nome da variável está correto
- Limpe o cache do Django: `python manage.py clearcache`

#### 3. CSS não carrega
**Solução:**
- Verifique o caminho no `base.html`
- Confirme se o arquivo existe no ZIP
- Teste o caminho: `{{ path_theme }}/css/style.css`

#### 4. Imagens não aparecem
**Solução:**
- Verifique o caminho das imagens
- Confirme se estão na pasta correta
- Teste com caminho absoluto primeiro

#### 5. JavaScript não funciona
**Solução:**
- Verifique se o arquivo está sendo carregado
- Abra o console do navegador para erros
- Confirme se não há conflitos com outros scripts

### Debug

#### Logs do Django
```bash
# Ative debug mode
DEBUG = True

# Verifique os logs
tail -f logs/django.log
```

#### Console do Navegador
```javascript
// Verifique se as variáveis estão disponíveis
console.log('Path theme:', '{{ path_theme }}');
console.log('Theme slug:', '{{ theme_slug }}');
```

#### Verificação de Arquivos
```python
# No shell do Django
from django.conf import settings
import os

theme_path = os.path.join(settings.BASE_DIR, 'themes', 'installed', 'meu-tema')
print(os.listdir(theme_path))
```

---

## 📚 Recursos Adicionais

### Documentação do Sistema
- `../themes/THEME_SYSTEM.md` - Visão geral técnica
- `docs/THEME_SYSTEM_FLOW_DIAGRAM.md` - Fluxo do sistema

### Arquivos de Referência
- `core/context_processors.py` - Processadores de contexto
- `apps/main/administrator/models.py` - Modelos do tema
- `utils/render_theme_page.py` - Renderização de páginas

### Exemplo Completo
Veja o tema `l2-ethernal-templar` em `themes/installed/` para um exemplo completo e funcional.

---

## 🎉 Conclusão

Criar temas para o PDL é um processo estruturado que permite personalização completa do site. Seguindo este guia, você conseguirá:

1. **Entender o sistema** de temas do PDL
2. **Criar temas funcionais** com todas as funcionalidades
3. **Implementar boas práticas** de desenvolvimento
4. **Resolver problemas** comuns
5. **Manter compatibilidade** com o sistema

Lembre-se: **Teste sempre** antes de fazer upload, **use variáveis** para textos e **mantenha o código organizado**. Com prática e paciência, você criará temas incríveis para o PDL!

---

*Este guia foi criado com base na análise do sistema de temas do PDL. Para dúvidas específicas, consulte a documentação técnica ou entre em contato com a equipe de desenvolvimento.* 
---

[ Voltar ao Índice](../INDEX.md)

