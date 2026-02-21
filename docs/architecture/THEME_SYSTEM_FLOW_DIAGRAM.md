# Diagrama de Fluxo do Sistema de Temas

> **Última atualização:** 21/02/2026

Este diagrama mostra o fluxo completo do sistema de temas, do upload do ZIP até a renderização da página com o tema ativo.

```mermaid
flowchart TD
    subgraph Admin
        A["Django Admin: Upload ZIP do Tema"]
    end
    subgraph Backend
        B["Model Theme: Validação e Extração"]
        C["theme.json: Metadados e Variáveis"]
        D["Arquivos em themes/installed/<slug>/"]
        E["Ativação: Apenas 1 tema ativo"]
        F["ThemeVariable: Variáveis salvas no banco"]
    end
    subgraph Contexto
        G["Context Processors:\n- active_theme\n- theme_variables\n- background_setting"]
    end
    subgraph Renderização
        H["render_theme_page (utils)"]
        I["Templates do tema ativo\n(installed/<slug>/base.html, etc)"]
        J["Fallback para templates padrão"]
    end
    subgraph Frontend
        K["Usuário acessa página\ncom a aparência do tema ativo"]
    end

    A --> B
    B --> C
    B --> D
    B --> F
    B --> E
    F --> G
    E --> G
    G --> H
    H --> I
    H --> J
    I --> K
    J --> K

    classDef safe fill:#444,stroke:#fff,stroke-width:2px,color:#fff;
    class A,B,C,D,E,F,G,H,I,J,K safe;
    %%{init: { 'theme': 'dark' }}%%
```

## Legenda
- **Django Admin:** Upload e gerenciamento de temas.
- **Model Theme:** Validação, extração e ativação do tema.
- **theme.json:** Metadados e variáveis do tema.
- **Arquivos extraídos:** Templates, CSS, JS, imagens, etc.
- **ThemeVariable:** Variáveis salvas e internacionalizadas.
- **Context Processors:** Injetam contexto nos templates.
- **render_theme_page:** Função utilitária para renderização dinâmica.
- **Templates do tema ativo:** Templates customizados do tema.
- **Fallback:** Usa templates padrão se não existirem no tema.
- **Usuário:** Visualiza o site com o tema ativo.
---

[ Voltar ao Índice](../INDEX.md)

