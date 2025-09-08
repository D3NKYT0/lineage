# Integration Diagram: Django x L2 Database

This diagram illustrates how the `apps.lineage.server` app bridges Django and the Lineage 2 (L2) database, detailing the data flow and responsibilities of each layer.

```mermaid
flowchart TD
    subgraph Django
        A["User (Browser)"]
        B["Django Views/Endpoints"]
        C["Utility Functions (LineageStats, LineageServices, etc)"]
    end
    subgraph Integration
        D["LineageDB (SQLAlchemy)"]
    end
    subgraph L2
        E["L2 Database (MySQL)"]
        F["Tables: characters, accounts, clan_data, ..."]
    end

    A -->|HTTP| B
    B --> C
    C -->|SQL| D
    D -->|Direct connection| E
    E --> F

    classDef safe fill:#444,stroke:#fff,stroke-width:2px,color:#fff;
    class A,B,C,D,E,F safe;
    %% Background
    %%{init: { 'theme': 'dark' }}%%
```

## Legend
- **User (Browser):** Client accessing the site.
- **Django Views/Endpoints:** Presentation and API layer.
- **Utility Functions:** Logic layer that prepares and executes queries.
- **LineageDB:** Integration class, bridges Django and the L2 database using SQLAlchemy.
- **L2 Database:** Game server database, with specific Lineage 2 tables.