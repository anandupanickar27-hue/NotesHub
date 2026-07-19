#!/bin/sh

echo "Waiting for database connection..."

sleep 5

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Rebuilding seed_demo"
python seed_demo.py

echo "Rebuilding ChromaDB..."
python manage.py rebuild_chroma

echo "Starting Gunicorn..."

exec gunicorn noteshub.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 1 