from celery.result import AsyncResult
from fastapi import APIRouter

from app.core.celery_app import celery_app
from app.tasks.email_tasks import send_email_task, send_welcome_email_task
from app.tasks.report_tasks import generate_invoice_pdf_task

router = APIRouter()


@router.post("/send-email")
def send_email(email: str):
    task = send_email_task.delay(email)
    return {
        "message": "Email queued",
        "task_id": task.id,
    }


@router.post("/send-welcome-email")
def send_welcome_email(user_email: str, username: str):
    task = send_welcome_email_task.delay(user_email, username)
    return {
        "message": "Welcome email queued",
        "task_id": task.id,
    }


@router.post("/generate-invoice")
def generate_invoice(invoice_id: int):
    task = generate_invoice_pdf_task.delay(invoice_id)
    return {
        "message": "Invoice PDF generation queued",
        "task_id": task.id,
        "invoice_id": invoice_id,
    }


@router.get("/task/{task_id}")
def task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "state": result.state,
        # result.result can be an Exception on FAILURE, so convert to str
        "result": str(result.result) if result.state == "FAILURE" else result.result,
    }
