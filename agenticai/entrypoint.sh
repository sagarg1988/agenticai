#!/bin/sh
set -e

echo "Waiting for database to be ready..."
python - <<'PYEOF'
import os, sys, time
try:
    import psycopg2
except ImportError:
    # psycopg2 not available — skip wait and let migrate fail with a clear error
    sys.exit(0)

host     = os.getenv("POSTGRES_HOST", "db")
port     = int(os.getenv("POSTGRES_PORT", "5432"))
db       = os.getenv("POSTGRES_DB", "aiagent")
user     = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "postgres")

for attempt in range(1, 31):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=password)
        conn.close()
        print(f"Database ready after {attempt} attempt(s).")
        sys.exit(0)
    except psycopg2.OperationalError:
        print(f"  Database not ready yet (attempt {attempt}/30) — retrying in 2s...")
        time.sleep(2)

print("ERROR: database did not become ready in 60 seconds.", file=sys.stderr)
sys.exit(1)
PYEOF

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
