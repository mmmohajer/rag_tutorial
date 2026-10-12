#!/bin/sh
set -eu

echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."

i=0
while [ "$i" -lt 60 ]; do
  if python -c 'import os, socket; s = socket.create_connection((os.environ["DB_HOST"], int(os.environ["DB_PORT"])), 2); s.close()'; then
    echo "Database is accepting connections"
    if [ "$#" -gt 0 ]; then
      exec "$@"
    fi
    echo "Running database migrations..."
    alembic upgrade head
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
  fi
  i=$((i + 1))
  sleep 1
done

echo "Database did not become ready in time" >&2
exit 1
