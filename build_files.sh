#!/bin/bash
echo "Installing project dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static assets..."
python3 manage.py collectstatic --no-input --clear

echo "Static build complete."
