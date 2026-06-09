import time

from app.core.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, email: str):
    try:
        print(f"[EMAIL] Sending email to {email}...")
        time.sleep(10)  # simulates real SMTP latency
        print(f"[EMAIL] Email sent to {email}")
        return {"status": "success", "email": email}
    except Exception as exc:
        # Retry after 5 seconds on failure
        raise self.retry(exc=exc, countdown=5)


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email_task(self, user_email: str, username: str):
    try:
        print(f"[WELCOME] Sending welcome email to {user_email} ({username})...")
        time.sleep(5)
        print(f"[WELCOME] Welcome email sent to {user_email}")
        return {"status": "success", "email": user_email, "type": "welcome"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
