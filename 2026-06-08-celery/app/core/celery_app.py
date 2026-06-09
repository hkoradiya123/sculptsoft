import logging
import os
import sys

from celery import Celery, signals
from celery.schedules import crontab
from kombu import Exchange, Queue

logger = logging.getLogger(__name__)

# ── Redis connection ──────────────────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ── App ───────────────────────────────────────────────────────────────────────
celery_app = Celery(
    "myapp",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.report_tasks",
    ],
)

# ── Queues & Routing ──────────────────────────────────────────────────────────
# Three priority lanes: high → default → low
# Workers pick high first, then default, then low.
default_exchange = Exchange("default", type="direct")
high_exchange    = Exchange("high",    type="direct")
low_exchange     = Exchange("low",     type="direct")

CELERY_QUEUES = (
    Queue("high",    high_exchange,    routing_key="high"),
    Queue("default", default_exchange, routing_key="default"),
    Queue("low",     low_exchange,     routing_key="low"),
)

CELERY_ROUTES = {
    # Critical emails go to high-priority queue
    "app.tasks.email_tasks.send_email_task":         {"queue": "high"},
    "app.tasks.email_tasks.send_welcome_email_task": {"queue": "high"},
    # Heavy background work goes to low-priority queue
    "app.tasks.report_tasks.generate_invoice_pdf_task": {"queue": "low"},
    "app.tasks.report_tasks.generate_daily_report":     {"queue": "low"},
}

# ── Windows fix ───────────────────────────────────────────────────────────────
# prefork uses billiard semaphores that fail with WinError 5 on Windows.
_pool = "solo" if sys.platform == "win32" else "prefork"

# ── Default retry policy (applied to every task unless overridden) ────────────
DEFAULT_RETRY_POLICY = {
    "max_retries": 3,
    "interval_start": 5,   # wait 5 s before first retry
    "interval_step":  5,   # add 5 s for each subsequent retry
    "interval_max":  30,   # cap at 30 s
}

# ── Main config ───────────────────────────────────────────────────────────────
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Reliability
    task_acks_late=True,            # ack only after task succeeds
    worker_prefetch_multiplier=1,   # fetch one task at a time → fair dispatch
    task_reject_on_worker_lost=True, # requeue if worker dies mid-task

    # Results
    result_expires=3600,            # keep results in Redis for 1 hour

    # Pool
    worker_pool=_pool,

    # Queues
    task_queues=CELERY_QUEUES,
    task_routes=CELERY_ROUTES,
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",

    # Retry defaults
    task_publish_retry_policy=DEFAULT_RETRY_POLICY,
)

# ── Beat schedule (cron jobs) ─────────────────────────────────────────────────
celery_app.conf.beat_schedule = {
    # Daily report at 2:00 AM UTC every day
    "daily-report-2am": {
        "task": "app.tasks.report_tasks.generate_daily_report",
        "schedule": crontab(hour=2, minute=0),
    },
    # Health-check ping every 5 minutes (useful for monitoring)
    "health-ping-5min": {
        "task": "app.tasks.report_tasks.generate_daily_report",
        "schedule": crontab(minute="*/5"),
    },
}

# ── Signals (lifecycle hooks) ─────────────────────────────────────────────────
@signals.task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **_):
    logger.info("[START] task=%s id=%s args=%s", task.name, task_id, args)


@signals.task_postrun.connect
def task_postrun_handler(task_id, task, retval, state, **_):
    logger.info("[DONE]  task=%s id=%s state=%s", task.name, task_id, state)


@signals.task_failure.connect
def task_failure_handler(task_id, exception, traceback, **_):
    logger.error("[FAIL]  id=%s exception=%s", task_id, exception)
