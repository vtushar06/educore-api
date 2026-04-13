#!/bin/bash
set -e

echo "Waiting for database..."
while ! python -c "
import os, psycopg2
conn = psycopg2.connect(
    dbname=os.environ.get('POSTGRES_DB', 'educore'),
    user=os.environ.get('POSTGRES_USER', 'educore'),
    password=os.environ.get('POSTGRES_PASSWORD', 'educore'),
    host=os.environ.get('POSTGRES_HOST', 'db'),
    port=os.environ.get('POSTGRES_PORT', '5432'),
)
conn.close()
" 2>/dev/null; do
    echo "  Database unavailable — retrying in 2s..."
    sleep 2
done

echo "Database is ready."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo "Starting server..."
exec "$@"
