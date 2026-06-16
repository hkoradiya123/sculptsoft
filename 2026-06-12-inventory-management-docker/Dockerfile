# Use slim version for smaller image size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Setup PostgreSQL and Redis directories
RUN mkdir -p /var/lib/postgresql/data /run/postgresql && \
    chown -R postgres:postgres /var/lib/postgresql /run/postgresql && \
    chmod 775 /run/postgresql

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables for all-in-one setup
ENV DATABASE_URL=postgresql://postgres:postgres@localhost:5432/inventory_db
ENV REDIS_URL=redis://localhost:6379/0
ENV RUN_SEED=true

# Fix Windows line endings and move entrypoint to a safe place
RUN apt-get update && apt-get install -y --no-install-recommends sed && \
    sed -i 's/\r$//' entrypoint.sh && \
    chmod +x entrypoint.sh && \
    mv entrypoint.sh /usr/local/bin/entrypoint.sh

# Expose port
EXPOSE 8000

# Use entrypoint script from the safe location
ENTRYPOINT ["entrypoint.sh"]
