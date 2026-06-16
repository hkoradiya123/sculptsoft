#!/bin/sh
set -e

# 1. Start Redis
echo "[INIT] Starting Redis..."
redis-server --daemonize yes

# 2. Setup PostgreSQL
echo "[INIT] Setting up PostgreSQL..."
PGDATA="/var/lib/postgresql/data"

# Initialize PostgreSQL if the data directory is empty
if [ ! -d "$PGDATA/base" ]; then
    echo "[INIT] Initializing PostgreSQL database..."
    chown -R postgres:postgres "$PGDATA"
    sudo -u postgres /usr/lib/postgresql/15/bin/initdb -D "$PGDATA"
fi

# Start PostgreSQL
echo "[INIT] Starting PostgreSQL..."
sudo -u postgres /usr/lib/postgresql/15/bin/postgres -D "$PGDATA" > /var/log/postgresql.log 2>&1 &

# 3. Wait for PostgreSQL to be ready
echo "[INIT] Waiting for PostgreSQL to be ready..."
until sudo -u postgres psql -c '\q' > /dev/null 2>&1; do
  sleep 1
done
echo "[INIT] PostgreSQL is ready."

# 4. Create Database and User if they don't exist
echo "[INIT] Ensuring database and user exist..."
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "CREATE DATABASE inventory_db OWNER postgres;" 2>/dev/null || true

# 5. Start Celery Worker in the background
echo "[APP] Starting Celery Worker..."
celery -A celery_app worker --loglevel=info > /var/log/celery.log 2>&1 &

# 6. Run Database Seeding
if [ "$RUN_SEED" = "true" ]; then
    echo "[SEED] Running Database Seeding..."
    python seed_db.py
    echo "[SEED] Seeding completed."
fi

# 7. Start FastAPI application in the foreground
echo "[APP] Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
