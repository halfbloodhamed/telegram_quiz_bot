#!/bin/bash
# Create initial database migration

echo "Creating initial database migration..."
alembic revision --autogenerate -m "Initial migration"

echo "Migration created successfully!"
echo "To apply migration, run: alembic upgrade head"
