#!/usr/bin/env sh
set -e

echo "Waiting for database..."
until python -c "import socket; socket.create_connection(('db', 5432), 2)" 2>/dev/null; do
  echo "  db not ready, retrying..."
  sleep 2
done
echo "Database is up."

if [ "${RUN_BOOTSTRAP:-1}" = "1" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput

  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

exec "$@"
