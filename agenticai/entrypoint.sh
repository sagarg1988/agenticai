#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

# Only create the dev superuser and seed data when explicitly requested.
# Set RUN_DEV_SETUP=true in docker-compose.yml (or locally) for development.
# Never set this in production.
if [ "${RUN_DEV_SETUP:-false}" = "true" ]; then
    echo "Creating dev superuser..."
    python manage.py create_dev_superuser

    echo "Seeding example data..."
    python manage.py seed_data
fi

echo "Starting server..."
exec "$@"
