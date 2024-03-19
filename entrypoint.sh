#!/bin/bash

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Celery worker
celery -A backend worker -l info &

# Start Django development server
python manage.py runserver 0.0.0.0:8000
