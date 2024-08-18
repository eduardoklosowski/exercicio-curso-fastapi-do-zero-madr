#!/bin/sh

set -e

echo '===> Run migrations'
alembic upgrade head
echo

echo '===> Run app'
exec uvicorn --host 0.0.0.0 --port 8000 --access-log madr.api:app
