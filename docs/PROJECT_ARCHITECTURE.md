# Project Architecture Document

## 1. Overview

This project is a robust web application based on Django, with multiple modules (apps) organized for different business domains. It uses Docker for environment orchestration, facilitating development, testing, and deployment. The frontend is decoupled, suggesting a modern and scalable architecture.

---

## 2. Main Components

### 2.1 Backend (Django)
- **Location:** `apps/`, `core/`, `middlewares/`, `utils/`
- **Description:**  
  The backend is implemented in Django, structured into multiple apps, each responsible for a specific domain (e.g., `accountancy`, `auction`, `games`, `inventory`, etc).  
  The `core/` directory likely contains global settings and shared functionalities.
- **Features:**  
  - Authentication, administration, reports, inventory, payments, games, shop, wiki, notifications, etc.
  - Use of custom middlewares.
  - Utilities and helper scripts in `utils/`.

### 2.2 Frontend
- **Location:** `frontend/`
- **Description:**  
  The frontend is decoupled from the backend, suggesting the use of modern frameworks (React, Vue, etc).  
  The `Charts.js` file and other JS files indicate dynamic visualizations.
- **Integration:**  
  Communication via REST API or GraphQL with the Django backend.

### 2.3 Database
- **Location:** Defined in `docker-compose.yml` (not directly visible, but assumed)
- **Description:**  
  The project uses a relational database (probably PostgreSQL or MySQL, common in Django projects).
- **Persistence:**  
  The `db.sqlite3` file suggests the use of SQLite in the development environment.

### 2.4 Web Server and Proxy
- **Location:** `nginx/`, `Dockerfile`, `gunicorn-cfg.py`
- **Description:**  
  Nginx acts as a reverse proxy, serving static files and forwarding requests to Gunicorn, which runs Django.
- **Configuration:**  
  Custom configuration files for Nginx and Gunicorn.

### 2.5 Internationalization
- **Location:** `locale/`
- **Description:**  
  Support for multiple languages (pt, en, es), with `.po` and `.mo` files for translations.

### 2.6 Static and Media Files
- **Location:** `static/`, `media/`
- **Description:**  
  Organization of assets (CSS, JS, images, fonts) and user uploads.

### 2.7 Tests and Scripts
- **Location:** `test/`, `setup/`
- **Description:**  
  Test scripts, key generation, backup automation, build, and dependency installation.

---

## 3. Orchestration with Docker Compose

### 3.1 Defined Services
The `docker-compose.yml` file defines the following main services:
- **site:**  
  Main container running Django with Daphne (ASGI).
- **nginx:**  
  Web server/reverse proxy.
- **db (postgres):**  
  Relational database.
- **redis:**  
  Message broker and cache.
- **celery:**  
  Worker for asynchronous tasks.
- **celery-beat:**  
  Scheduler for periodic tasks.
- **flower:**  
  Celery monitoring and dashboard.

### 3.2 Network and Volumes
- **Internal network:**  
  Communication between containers via Docker network.
- **Volumes:**  
  Data persistence for the database, static files, and media.

---

## 4. Directory Structure

```plaintext
apps/           # Django apps organized by domain
core/           # Central project settings and functionalities
middlewares/    # Custom Django middlewares
utils/          # Helper scripts and utilities
frontend/       # Decoupled frontend code
static/         # Static files (CSS, JS, images)
media/          # User uploads
nginx/          # Nginx configurations
locale/         # Translation files
setup/          # Automation and setup scripts
test/           # Test scripts and files
templates/      # Django HTML templates
```

---

## 5. Request Flow

See diagram in `DIAGRAMA.md`.

---

## 6. Security Considerations
- Use of environment variables for secrets (`env.sample`).
- Reverse proxy configuration (Nginx) for protection and performance.
- Possible use of custom authentication and authorization.

---

## 7. Internationalization and Accessibility
- Support for multiple languages via `locale/`.
- Templates organized for easy maintenance and customization.

---

## 8. Deployment and Scalability
- Deployment facilitated via Docker Compose.
- Possibility to scale services (web, workers) as needed.
- Clear separation between frontend and backend.

---

## 9. Observability and Logs
- `logs/` directory for storing application and access logs.
- Possible integration with external monitoring tools.

---

## 10. Documentation
- `README.md`, `wiki.md`, `help.md` provide usage instructions, contribution guidelines, and project details. 