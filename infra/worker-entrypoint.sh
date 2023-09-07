#!/bin/sh

until cd /app/; do
  echo "Waiting for server volume..."
done

celery -A web_resource_watchdog.celery_app worker --loglevel=info
