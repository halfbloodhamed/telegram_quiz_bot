FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for SQLite database (for local dev)
RUN mkdir -p /app/data

# Run migrations if available, then start the bot
CMD sh -c 'if [ -d /app/alembic/versions ]; then alembic upgrade head; fi; python -m app.main'
