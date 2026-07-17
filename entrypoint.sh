#!/bin/sh

echo "Waiting for database connection..."

sleep 5

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."

exec gunicorn noteshub.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3