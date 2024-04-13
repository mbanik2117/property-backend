#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Celery worker for the 'ecom' app
echo "Starting Celery worker for 'ecom' app..."
celery -A backend worker -l info &

# Start Gunicorn server
echo "Starting Gunicorn server..."
gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Keep container running
exec "$@"
