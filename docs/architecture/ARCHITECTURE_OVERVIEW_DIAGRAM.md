# Diagrama de Arquitetura

> **Última atualização:** 21/02/2026

Este diagrama representa a arquitetura do projeto PDL, do acesso do usuário ao banco de dados, incluindo todos os serviços orquestrados pelo Docker Compose.

```mermaid
flowchart TD
    subgraph Web
        A["Usuário (Navegador)"]
    end
    subgraph Nginx
        B["nginx (Proxy Reverso)"]
    end
    subgraph App
        C["site_http (Django/Gunicorn)"]
        C2["site_asgi (Django/Daphne)"]
        D["celery (Worker)"]
        E["celery-beat (Agendador)"]
        F["flower (Monitoramento Celery)"]
    end
    subgraph Infra
        G["redis (Broker/Cache)"]
        H["postgres (Banco de Dados)"]
    end
    
    A -->|HTTP/HTTPS| B
    B -->|Proxy HTTP| C
    B -->|Proxy WebSocket| C2
    B -->|Arquivos Estáticos/Mídia| B
    C -->|ORM| H
    C2 -->|ORM| H
    C -->|Tarefas Assíncronas| G
    C2 -->|Tarefas Assíncronas| G
    D -->|Broker| G
    E -->|Broker| G
    F -->|Broker| G
    D -->|Executa Tarefas| C
    E -->|Dispara Tarefas| D
    F -->|Monitora| D
    F -->|Monitora| E
    C -->|Depende de| G
    C2 -->|Depende de| G
    D -->|Depende de| C
    E -->|Depende de| C
    F -->|Depende de| C
    B -->|Depende de| C
    B -->|Depende de| C2
    C -->|Depende de| H
    C2 -->|Depende de| H
    D -->|Depende de| G
    E -->|Depende de| G
    F -->|Depende de| G

    classDef safe fill:#444,stroke:#fff,stroke-width:2px,color:#fff;
    class A,B,C,C2,D,E,F,G,H safe;
    %%{init: { 'theme': 'dark' }}%%
```

## Legenda dos Componentes
- **Usuário (Navegador):** Cliente acessando o sistema.
- **nginx:** Proxy reverso, serve arquivos estáticos e encaminha requisições para Django.
- **site_http:** Aplicação Django via Gunicorn (requisições HTTP síncronas).
- **site_asgi:** Aplicação Django via Daphne (WebSockets e requisições assíncronas).
- **celery:** Worker de tarefas assíncronas.
- **celery-beat:** Agendador de tarefas periódicas.
- **flower:** Dashboard de monitoramento do Celery.
- **redis:** Broker de mensagens e cache.
- **postgres:** Banco de dados PostgreSQL.

---

[ Voltar ao Índice](../INDEX.md)

