"""
Celery application configuration.
"""
from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "nexcell_ai",
    broker=settings.redis_connection_url,
    backend=settings.redis_connection_url,
    include=[
        "app.workers.tasks.email_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Task routing
    task_routes={
        "app.workers.tasks.email_tasks.*": {"queue": "email_queue"},
    },
    # Task result expiration
    result_expires=3600,  # 1 hour
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers.tasks"])

