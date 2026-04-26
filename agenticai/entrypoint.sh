#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating dev superuser..."
python manage.py create_dev_superuser

echo "Seeding example data..."
python manage.py seed_data

echo "Starting server..."
exec "$@"
