# App Tops - Rankings do Servidor

Este app fornece uma interface pública para visualizar os rankings do servidor Lineage 2, seguindo o padrão dos apps Wiki e Downloads.

## Funcionalidades

- **Ranking PvP**: Melhores guerreiros PvP do servidor
- **Ranking PK**: Jogadores com mais PKs
- **Ranking Adena**: Jogadores mais ricos
- **Ranking Clãs**: Clãs mais poderosos
- **Ranking Nível**: Jogadores de maior nível
- **Top Online**: Jogadores online no momento
- **Ranking Olimpíada**: Campeões da olimpíada
- **Castle & Siege**: Status dos castelos e cerco

## Estrutura

```
apps/lineage/tops/
├── __init__.py
├── apps.py              # Configuração do app
├── urls.py              # URLs do app
├── views.py             # Views das páginas
├── templates/
│   └── tops/
│       ├── base-tops.html      # Template base
│       ├── base.html           # Template com abas
│       ├── home.html           # Página inicial
│       ├── pvp.html            # Ranking PvP
│       ├── pk.html             # Ranking PK
│       ├── adena.html          # Ranking Adena
│       ├── clans.html          # Ranking Clãs
│       ├── level.html          # Ranking Nível
│       ├── online.html         # Top Online
│       ├── olympiad.html       # Ranking Olimpíada
│       └── siege.html          # Castle & Siege
└── README.md
```

## URLs

- `/public/tops/` - Página inicial
- `/public/tops/pvp/` - Ranking PvP
- `/public/tops/pk/` - Ranking PK
- `/public/tops/adena/` - Ranking Adena
- `/public/tops/clans/` - Ranking Clãs
- `/public/tops/level/` - Ranking Nível
- `/public/tops/online/` - Top Online
- `/public/tops/olympiad/` - Ranking Olimpíada
- `/public/tops/siege/` - Castle & Siege

## Views

### TopsBaseView
Classe base para todas as views do app, fornecendo funcionalidades comuns.

### TopsHomeView
Página inicial com cards para cada tipo de ranking.

### TopsPvpView, TopsPkView, etc.
Views específicas para cada tipo de ranking, utilizando as mesmas queries do app server mas sem autenticação.

## Templates

### base-tops.html
Template base com header fixo, seletor de idioma e botão para voltar ao site.

### base.html
Template com navegação lateral (abas) seguindo o padrão do Wiki.

### home.html
Página inicial com cards para cada ranking.

### [ranking].html
Templates específicos para cada ranking com tabelas responsivas.

## CSS

O arquivo `static/default/css/tops.css` contém todos os estilos específicos do app, seguindo o padrão visual do Wiki.

## Integração

- Utiliza as mesmas queries do app `server` através do `LineageStats`
- Aplica crests aos clãs usando `attach_crests_to_clans`
- Suporte completo a internacionalização (i18n)
- Responsivo para mobile e desktop

## Dependências

- `apps.lineage.server.database.LineageDB`
- `apps.lineage.server.utils.crest`
- `apps.lineage.server.models.ActiveAdenaExchangeItem`
- `utils.dynamic_import`

## Configuração

O app já está configurado no `INSTALLED_APPS` e suas URLs estão incluídas no `core/urls.py`.

## Traduções

Todas as strings estão traduzidas em português no arquivo `locale/pt/LC_MESSAGES/django.po`. 