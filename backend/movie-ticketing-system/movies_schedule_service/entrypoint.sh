#!/usr/bin/env bash
set -e

# Apply any pending database migrations before starting the service/worker.
# This ensures tables like "movie_details" exist for the Celery scrape task.
echo "Running Django migrations..."
python manage.py migrate --noinput

# Hand off to whatever command was passed (runserver / celery worker / beat).
exec "$@"