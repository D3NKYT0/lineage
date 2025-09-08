# Installation and Deployment Guide

## Prerequisites
- Python 3.10+
- Docker and Docker Compose
- Node.js (optional, for frontend)

## Local Installation (without Docker)
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd SITE
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the environment variables:
   - Copy `env.sample` to `.env` and adjust as needed.
5. Migrate the database and create a superuser:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
6. Run the server:
   ```bash
   python manage.py runserver
   ```

## Installation with Docker
1. Configure the `.env` file.
2. Run:
   ```bash
   docker-compose up --build
   ```
3. Access the system at `http://localhost:6085`.

## Production Deployment
- Use Docker Compose, Nginx, HTTPS (Let's Encrypt).
- Configure volumes for data persistence.
- Adjust environment variables for production.

## Tips
- Use `docker-compose logs -f` to view the logs.
- Use `docker-compose exec site bash` to access the Django container. 