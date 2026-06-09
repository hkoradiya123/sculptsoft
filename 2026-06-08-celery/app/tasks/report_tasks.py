import time

from app.core.celery_app import celery_app


@celery_app.task
def generate_daily_report():
    print("[REPORT] Generating daily report...")
    time.sleep(3)
    print("[REPORT] Daily report generated")
    return {"status": "success", "report": "daily_report.pdf"}


@celery_app.task(bind=True, max_retries=2)
def generate_invoice_pdf_task(self, invoice_id: int):
    try:
        print(f"[PDF] Generating invoice PDF for invoice_id={invoice_id}...")
        time.sleep(8)
        print(f"[PDF] Invoice PDF generated for invoice_id={invoice_id}")
        return {"status": "success", "invoice_id": invoice_id, "file": f"invoice_{invoice_id}.pdf"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
