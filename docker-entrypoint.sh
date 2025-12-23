#!/bin/sh

set -e

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done

echo "Database is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Loading initial data..."
python manage.py loaddata fixtures/initial_data.json || echo "Fixtures already loaded or failed"

echo "Starting server..."
exec "$@"
