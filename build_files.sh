#!/bin/bash

# Install required packages and dependencies
pip install -r requirements.txt

# Collect static files
python3.10 manage.py collectstatic --noinput
python3.10 manage.py migrate --noinput
