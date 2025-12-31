#!/bin/bash
# Start Celery beat scheduler (for periodic tasks)

celery -A app.workers.celery_app beat \
    --loglevel=info

