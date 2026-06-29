"""
Redis Task Queue Configuration
"""
from celery import Celery
from app.core.config import settings


celery_app = Celery(
    "recap-ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.render_engine.worker"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.services.render_engine.worker.*": {"queue": "gpu"},
        "app.services.whisper.*": {"queue": "cpu"},
        "app.services.translate.*": {"queue": "cpu"},
    },
    
    # Task settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,
)


@celery_app.task(bind=True, name="health_check")
def health_check(self):
    """Health check task"""
    return {"status": "ok", "task_id": self.request.id}
