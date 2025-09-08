# Theme System Flow Diagram

This diagram shows the complete flow of the theme system, from ZIP upload to page rendering with the active theme.

```mermaid
flowchart TD
    subgraph Admin
        A["Django Admin: Theme ZIP Upload"]
    end
    subgraph Backend
        B["Theme Model: Validation & Extraction"]
        C["theme.json: Metadata & Variables"]
        D["Extracted files in themes/installed/<slug>/"]
        E["Activation: Only 1 active theme"]
        F["ThemeVariable: Variables saved in the database"]
    end
    subgraph Context
        G["Context Processors:\n- active_theme\n- theme_variables\n- background_setting"]
    end
    subgraph Rendering
        H["render_theme_page (utils)"]
        I["Templates of the active theme\n(installed/<slug>/base.html, etc)"]
        J["Fallback to default templates"]
    end
    subgraph Frontend
        K["User accesses page\nwith the active theme's look"]
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
    %% Background of the graph
    %%{init: { 'theme': 'dark' }}%%
```

## Legend
- **Django Admin:** Theme upload and management.
- **Theme Model:** Validation, extraction, and activation of the theme.
- **theme.json:** Theme metadata and variables.
- **Extracted files:** Templates, CSS, JS, images, etc.
- **ThemeVariable:** Saved and internationalized variables.
- **Context Processors:** Inject context into templates.
- **render_theme_page:** Utility function for dynamic rendering.
- **Templates of active theme:** Customized theme templates.
- **Fallback:** Use default templates if not present in the theme.
- **User:** Views the site with the active theme.