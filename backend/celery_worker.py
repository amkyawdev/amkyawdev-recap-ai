"""
Celery Worker with GPU Support
Background task processing for video rendering
"""
import os
import logging
from celery import Celery
from app.core.config import settings
from app.core.gpu_manager import gpu_manager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "recap-ai-worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.services.render_engine.worker",
        "app.services.whisper.tasks",
        "app.services.translate.tasks",
    ]
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
        "app.services.whisper.tasks.*": {"queue": "cpu"},
        "app.services.translate.tasks.*": {"queue": "cpu"},
    },
    
    # Task settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=7200,  # 2 hours max
    task_soft_time_limit=6600,  # 110 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    worker_disable_rate_limits=True,
    
    # Result settings
    result_expires=86400,  # 24 hours
    result_extended=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)


@celery_app.task(bind=True, name="gpu_health_check")
def gpu_health_check(self):
    """Health check with GPU status"""
    status = gpu_manager.get_status()
    return {
        "status": "ok",
        "gpu_available": status.get("available", False),
        "gpu_count": status.get("device_count", 0),
    }


@celery_app.task(name="cleanup_temp_files")
def cleanup_temp_files():
    """Cleanup temporary files"""
    import glob
    import time
    
    temp_dir = settings.TEMP_DIR
    max_age = 3600 * 24  # 24 hours
    
    removed = 0
    for pattern in ["*.mp4", "*.wav", "*.jpg", "*.tmp"]:
        for path in glob.glob(os.path.join(temp_dir, pattern)):
            try:
                if time.time() - os.path.getmtime(path) > max_age:
                    os.unlink(path)
                    removed += 1
            except Exception as e:
                logger.warning(f"Failed to remove {path}: {e}")
    
    return {"removed_files": removed}


# Start worker with: celery -A celery_worker worker --loglevel=info --concurrency=2 -Q gpu,celery
# Or use docker-compose up with the worker services
