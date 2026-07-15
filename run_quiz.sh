#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

mkdir -p data

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  echo "Starting Telegram Quiz Bot with Docker..."
  export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://quiz_user:quiz_password@postgres:5432/quiz_db}"
  export REDIS_URL="${REDIS_URL:-redis://redis:6379/0}"
  docker compose up -d --build
  echo ""
  echo "The bot is starting. Check logs with:"
  echo "  docker compose logs -f bot"
  echo ""
  echo "To stop it later, run:"
  echo "  docker compose down"
  exit 0
fi

echo "Docker is not available; starting the bot locally..."
export DATABASE_URL="sqlite+aiosqlite:///./data/quiz.db"
export REDIS_URL="memory://"
export ENVIRONMENT="development"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

if ! "$PYTHON_BIN" -c "import aiogram, sqlalchemy, redis" >/dev/null 2>&1; then
  echo "Installing Python dependencies..."
  "$PYTHON_BIN" -m pip install -r requirements.txt >/dev/null 2>&1 || true
fi

exec "$PYTHON_BIN" -m app.main
