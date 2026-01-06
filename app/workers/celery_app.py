"""
Celery application configuration.
"""
import ssl
from celery import Celery
from app.config import settings

# Get Redis URL
redis_url = settings.redis_connection_url

# Configure broker and backend with SSL parameters for rediss:// URLs
broker_use_ssl = None
redis_backend_use_ssl = None

if redis_url.startswith("rediss://"):
    # SSL configuration for secure Redis connections (Upstash, etc.)
    broker_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE,  # Don't verify SSL certificates
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    }
    redis_backend_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    }

# Create Celery app
celery_app = Celery(
    "nexcell_ai",
    broker=redis_url,
    backend=redis_url,
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
    # SSL configuration for broker and backend
    broker_use_ssl=broker_use_ssl,
    redis_backend_use_ssl=redis_backend_use_ssl,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers.tasks"])

