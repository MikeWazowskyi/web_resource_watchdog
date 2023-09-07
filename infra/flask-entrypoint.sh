#!/bin/sh

until cd /app/; do
  echo "Waiting for server volume..."
done

# Apply database migrations
echo "Applying database migrations ..."
until flask db upgrade; do
  echo "Waiting for db to be ready..."
  sleep 2
done

# Start server
echo "Starting server ..."
gunicorn -w "$WORKERS" web_resource_watchdog:flask_app -b 0.0.0.0:"$GUNICORN_PORT"
