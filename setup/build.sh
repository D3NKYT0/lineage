#!/bin/bash

# Exit on any error
set -e

# Detect Ubuntu version
UBUNTU_VERSION=$(lsb_release -cs)
if [ "$UBUNTU_VERSION" = "focal" ]; then
  DOCKER_COMPOSE="docker-compose"
else
  DOCKER_COMPOSE="docker compose"
fi

echo "=============================="
echo "Starting deployment process"
echo "=============================="

# Pull latest changes from Git
echo "Pulling latest changes from Git..."
git pull origin main || { echo "Failed to pull from Git repository"; exit 1; }

# Activate virtualenv (must exist)
echo "Activating virtual environment..."
source .venv/bin/activate || { echo "Virtualenv not found. Please create it with 'python -m venv .venv'"; exit 1; }

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip || { echo "Failed to upgrade pip"; exit 1; }

# Upgrade installed packages from requirements.txt
echo "Upgrading packages from requirements.txt..."
pip install -U -r requirements.txt || { echo "Failed to upgrade packages"; exit 1; }

# Check Django project for issues
echo "Running Django system check (host)..."
python3 manage.py check || { echo "Django check failed"; exit 1; }

# Create new migrations locally
echo "Making migrations (host)..."
python3 manage.py makemigrations || { echo "Failed to make migrations"; exit 1; }

# Stop running containers
echo "Stopping containers..."
$DOCKER_COMPOSE down || { echo "Failed to stop running containers"; }

# Remove old containers
echo "Removing old containers..."
containers=$(docker ps -a -q --filter name=site --filter name=celery --filter name=celery_beat --filter name=flower --filter name=nginx --filter name=redis)
if [ -n "$containers" ]; then
  docker rm $containers || echo "Some containers could not be removed (maybe already removed)"
else
  echo "No containers found to remove."
fi

# Remove optional static_data volume
echo "Removing static_data volume..."
docker volume rm $(docker volume ls -q --filter name=static_data) || echo "Volume not found or already removed"

# Build Docker images
echo "Building Docker images..."
$DOCKER_COMPOSE build || { echo "Failed to build Docker images"; exit 1; }

# Start containers
echo "Starting containers..."
$DOCKER_COMPOSE up -d || { echo "Failed to start containers"; exit 1; }

# Wait for DB (direct)
echo "Waiting for database..."
until $DOCKER_COMPOSE exec postgres pg_isready -U db_user > /dev/null 2>&1; do
  echo "$(date '+%H:%M:%S') - PostgreSQL is not ready yet. Waiting..."
  sleep 2
done

# Run migration inside container (applies what was created on host)
echo "Applying migrations inside container..."
$DOCKER_COMPOSE exec site python3 manage.py migrate || { echo "Failed to apply migrations"; exit 1; }

# Clean up
echo "Cleaning up..."
docker image prune -f
docker volume prune -f
docker container prune -f
docker builder prune -f

echo "Deployment completed successfully."
