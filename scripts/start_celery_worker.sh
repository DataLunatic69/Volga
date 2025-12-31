#!/bin/bash
# Start Celery worker for email tasks

celery -A app.workers.celery_app worker \
    --loglevel=info \
    --queues=email_queue \
    --concurrency=4 \
    --hostname=worker@%h

