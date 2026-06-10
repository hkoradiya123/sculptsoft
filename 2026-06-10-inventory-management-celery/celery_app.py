from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Redis URL format: redis://:password@hostname:port/db_number
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "inventory_mgmt",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Optimization settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)

# Industry best practice: Automatically find tasks (but forcing explicit import for Windows stability)
# celery_app.autodiscover_tasks(['app.tasks'], force=True)

# Explicitly import the tasks module so Celery registers them immediately
import app.tasks.inventory_tasks

if __name__ == "__main__":
    celery_app.start()
