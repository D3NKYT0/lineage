# Architecture Diagram

This diagram represents the project architecture, from user access to the database, including all services orchestrated by Docker Compose.

```mermaid
flowchart TD
    subgraph Web
        A["User (Browser)"]
    end
    subgraph Nginx
        B["nginx (Reverse Proxy)"]
    end
    subgraph App
        C["site (Django/ASGI)"]
        D["celery (Worker)"]
        E["celery-beat (Scheduler)"]
        F["flower (Celery Monitoring)"]
    end
    subgraph Infra
        G["redis (Broker/Cache)"]
        H["postgres (Database)"]
    end
    
    A -->|HTTP/HTTPS| B
    B -->|Proxy| C
    B -->|Static/Media Files| B
    C -->|ORM| H
    C -->|Asynchronous Tasks| G
    D -->|Broker| G
    E -->|Broker| G
    F -->|Broker| G
    D -->|Executes Tasks| C
    E -->|Triggers Tasks| D
    F -->|Monitors| D
    F -->|Monitors| E
    C -->|Depends on| G
    D -->|Depends on| C
    E -->|Depends on| C
    F -->|Depends on| C
    B -->|Depends on| C
    C -->|Depends on| H
    D -->|Depends on| G
    E -->|Depends on| G
    F -->|Depends on| G

    classDef safe fill:#444,stroke:#fff,stroke-width:2px,color:#fff;
    class A,B,C,D,E,F,G,H safe;
    %% Chart background
    %% Mermaid does not have an official directive for background, but you can use a note to simulate
    %% or instruct the viewer to use dark theme.
    %% For renderers that support it, you can use: %%{init: { 'theme': 'dark' }}%%
    %%{init: { 'theme': 'dark' }}%%
```

## Component Legend
- **User (Browser):** Client accessing the system.
- **nginx:** Reverse proxy, serves static files and forwards requests to Django.
- **site:** Django application running via ASGI (Daphne).
- **celery:** Worker for asynchronous tasks.
- **celery-beat:** Periodic task scheduler.
- **flower:** Celery monitoring and dashboard.
- **redis:** Message broker and cache.
- **postgres:** Relational database.
