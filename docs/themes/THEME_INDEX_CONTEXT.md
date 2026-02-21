# Variáveis de Contexto da Página Inicial (`index.html`)

> **Última atualização:** 21/02/2026

O sistema PDL passa um conjunto rico de dados da view Python (`apps/main/home/views/views.py`) para o template da página inicial do tema (`index.html`). Este documento detalha todas essas variáveis, sua estrutura de dados e exemplos de como utilizá-las no desenvolvimento do seu tema.

---

## 📋 Resumo das Variáveis

Aqui estão as variáveis disponíveis no contexto do `index.html`, além das [variáveis globais do sistema de temas](THEME_DEVELOPER_GUIDE.md#variaveis-sistema):

1. [clanes](#clanes)
2. [classes_info](#classes_info)
3. [online e show_players_online](#status-online)
4. [configuracao e traduções do servidor](#info-servidor)
5. [apoiadores](#apoiadores)
6. [latest_news_list](#latest_news_list)
7. [content_items](#content_items)
8. [server_status](#server_status)
9. [banners e popup_banners](#banners)

---

## 1. `clanes` {#clanes}

**O que é:** Uma lista dos top 10 clãs do servidor com suas respectivas crests embutidas como base64.

**Estrutura de cada item na lista:**
- `clan_name` (string)
- `clan_level` (int)
- `reputation_score` (int)
- `leader_name` (string)
- `crest_base64` (string / opcional, gerada internamente se o clã tiver um crest)

**Exemplo de uso no HTML:**
```django
<div class="top-clans">
    <h3>Top Clãs</h3>
    <ul>
        {% for clan in clanes %}
            <li>
                {% if clan.crest_base64 %}
                    <img src="data:image/png;base64,{{ clan.crest_base64 }}" alt="Crest">
                {% else %}
                    <div class="default-crest"></div>
                {% endif %}
                <b>{{ clan.clan_name }}</b> (Lvl {{ clan.clan_level }}) - Reputação: {{ clan.reputation_score }}
            </li>
        {% empty %}
            <li>Nenhum clã encontrado.</li>
        {% endfor %}
    </ul>
</div>
```

---

## 2. `classes_info` {#classes_info}

**O que é:** Dados detalhados das classes do jogo, extraídos de configurações do sistema (`utils/data/index.json`), para cards ou sliders.

**Estrutura de cada item na lista:**
- `name` (string): Nome da classe.
- `slug` (string): Identificador.
- `badge` (string): Caminho ou classe do ícone.
- `difficulty` (int/string): Dificuldade da classe.
- `stats` (dict): Atributos da classe (ex: p_atk, m_atk).
- `skills` (lista): Lista de skills da classe.
- `descricao` (string): Texto de descrição da classe.
- `image` (string): Caminho/URL para imagem representativa.

**Exemplo de uso no HTML:**
```django
<div class="classes-slider">
    {% for c in classes_info %}
        <div class="class-card">
            <h4>{{ c.name }}</h4>
            <img src="{{ c.image }}" alt="{{ c.name }}">
            <p>{{ c.descricao }}</p>
            <span class="difficulty">Dificuldade: {{ c.difficulty }}/5</span>
        </div>
    {% endfor %}
</div>
```

---

## 3. `online` e `show_players_online` {#status-online}

**O que é:** Parâmetros para controle e exibição do número de jogadores online. O valor `online` já inclui cálculos com *fake players* caso configurado.

- `online` (numérico): Quantidade de jogadores.
- `show_players_online` (booleano): Flag que define se a visualização deve estar ativa de acordo com as configurações do painel `settings`.

**Exemplo de uso no HTML:**
```django
{% if show_players_online %}
    <div class="online-counter">
        <span class="status-dot green"></span>
        {{ online }} Jogadores Online
    </div>
{% endif %}
```

---

## 4. `configuracao` e Tradução do Servidor {#info-servidor}

**O que é:** Variáveis referentes à customização textual inicial do site, adaptáveis dependendo do idioma ativo da sessão.

- `configuracao`: Objeto completo do modelo `IndexConfig`.
- `nome_servidor` (string): O título ou nome configurado, traduzido.
- `descricao_servidor` (string): A descrição ("Onde Lendas Nascem..."), traduzida.
- `jogadores_online_texto` (string): O prefixo/sufixo customizado de jogadores, traduzido.

**Exemplo de uso no HTML:**
```django
<header class="server-header">
    <h1>{{ nome_servidor }}</h1>
    <p>{{ descricao_servidor }}</p>
    {% if show_players_online %}
        <p>{{ online }} {{ jogadores_online_texto }}</p>
    {% endif %}
</header>
```

---

## 5. `apoiadores` {#apoiadores}

**O que é:** Uma query de objetos do modelo `Apoiador` que reflete os doadores ou contribuidores ativos e aprovados.

**Estrutura principal de cada objeto `Apoiador`:**
- `user.username` (string): Nome do usuário no sistema.
- `imagem` (FileField): A imagem de avatar/badge do apoiador inserido no painel de administração.
- Pode conter outras informações de acordo com o modelo (como valor, link, etc).

**Exemplo de uso no HTML:**
```django
<div class="supporters-section">
    {% for apoiador in apoiadores %}
        <div class="supporter">
            {% if apoiador.imagem %}
                <img src="{{ apoiador.imagem.url }}" alt="{{ apoiador.user.username }}">
            {% endif %}
            <span>{{ apoiador.user.username }}</span>
        </div>
    {% endfor %}
</div>
```

---

## 6. `latest_news_list` {#latest_news_list}

**O que é:** As 10 notícias públicas e publicadas mais recentes do servidor, encapsuladas junto a suas respectivas traduções de acordo com a linguagem atual do visitante (`'pt'`, `'en'`, etc.).

**Estrutura de cada item na lista:**
- `news` (Objeto `News`): O registro genérico. Tem campos cruciais como `news.slug`, `news.image_url()`, e `news.pub_date`.
- `translation` (Objeto `NewsTranslation`): A tradução atrelada, contendo os campos de texto que devem ser mostrados (`translation.title`, `translation.abstract`, etc.).

**Exemplo de uso no HTML:**
```django
<section class="news-list">
    {% for item in latest_news_list %}
        <article class="news-card">
            <a href="{% url 'public_news_detail' item.news.slug %}">
                <img src="{{ item.news.image_url }}" alt="{{ item.translation.title }}">
                <h2>{{ item.translation.title }}</h2>
                <p>{{ item.translation.abstract }}</p>
                <small>Postado em: {{ item.news.pub_date|date:"d/m/Y" }}</small>
            </a>
        </article>
    {% endfor %}
</section>
```

---

## 7. `content_items` {#content_items}

**O que é:** Os últimos 4 recursos visuais de mídia (imagens) hospedados como públicos e ativos no aplicativo `media_storage`. Isso é usado primariamente nas sessões de *Galeria*.

**Estrutura de cada objeto `MediaFile`:**
- `title` (string): O nome ou título da imagem.
- `file.url` (string): URL direta para o arquivo.
- `uploaded_at` (datetime): Data de envio da mídia.

**Exemplo de uso no HTML:**
```django
<div class="gallery">
    <h3>Media Content</h3>
    <div class="grid">
        {% for content in content_items %}
            <div class="media-preview">
                <img src="{{ content.file.url }}" alt="{{ content.title }}">
            </div>
        {% empty %}
            <p>Nenhuma media disponível.</p>
        {% endfor %}
    </div>
</div>
```

---

## 8. `server_status` {#server_status}

**O que é:** Transmite em tempo real o acesso do back-end ao servidor Login/Game através do cache. Retorna um dicionário.

**Estrutura do dicionário:**
- `overall_status` (string): Retorna `"online"` ou `"offline"`.
- `game_server['status']` (string): Retorna `"online"` ou `"offline"` específico para o GameServer.
- `login_server['status']` (string): Retorna `"online"` ou `"offline"` específico para o LoginServer.
- `server_ip` (string): IP analisado.

**Exemplo de uso no HTML:**
```django
<div class="status-panel">
    <div class="server {{ server_status.login_server.status }}">
        Login: {{ server_status.login_server.status|upper }}
    </div>
    <div class="server {{ server_status.game_server.status }}">
        Game: {{ server_status.game_server.status|upper }}
    </div>
</div>
```

---

## 9. Banners e Popups (`banners` e `popup_banners`) {#banners}

**O que é:** Listas de anúncios/notificiações vitais gerenciadas ativamente pelos administradores.

**Estrutura e Diferentes Categorias:**
- `popup_banners` (lista): Banners desenhados para agir como pop-ups iniciais na abertura da plataforma. Se renderizados, costumam engatilhar scripts em Modal visuais.
- `banners` (dicionário): Contêm banners classificados restritamente de acordo com sua `position`.  Isso simplifica alocar o layout independentemente (A top banner renderiza no header, um bottom no footer).
  - `banners.top`: Renderiza objetos `Banner` associados ao topo.
  - `banners.middle`: Renderiza objetos associados ao meio.
  - `banners.bottom`: Renderiza objetos associados à base/rodapé.

**Objetos Banner (Campos úteis):**
- `title`, `link`, `image.url`, `description`, `is_blank` (Nova aba).

**Exemplo de uso no HTML:**
```django
<!-- Renderizando banner de Topo -->
{% for banner in banners.top %}
    <div class="top-banner">
        <a href="{{ banner.link }}" {% if banner.is_blank %}target="_blank"{% endif %}>
            {% if banner.image %}
                <img src="{{ banner.image.url }}" alt="{{ banner.title }}">
            {% else %}
                <b>{{ banner.title }}</b> - {{ banner.description }}
            {% endif %}
        </a>
    </div>
{% endfor %}

<!-- Lógica simulando modal Pop-up -->
{% if popup_banners %}
    <div id="welcome-modal" class="modal">
        {% for popup in popup_banners %}
            <div class="modal-content">
                <h2>{{ popup.title }}</h2>
                {% if popup.image %}
                    <img src="{{ popup.image.url }}">
                {% endif %}
                <button onclick="closeModal()">Fechar</button>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

---

**Leituras Sugeridas:**
- [Guia do Desenvolvedor de Temas](THEME_DEVELOPER_GUIDE.md)
- [Sistema de Temas Central](THEME_SYSTEM.md)

---

[ Voltar ao Índice](../INDEX.md)
