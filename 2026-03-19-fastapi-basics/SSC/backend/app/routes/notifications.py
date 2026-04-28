from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import get_current_user
from app.schemas import NotificationResponse
from app.utils.firestore_data import COLL, as_obj, create_doc, delete_doc, first_doc, list_docs, now_utc, update_doc, _parse_datetime
from app.utils.logger import log_action

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _same_id(left, right) -> bool:
    if left is None or right is None:
        return False
    return str(left) == str(right)


def _cleanup_old_read_notifications(user_id, days_to_keep: int = 7) -> int:
    """Delete read notifications older than retention window."""
    cutoff_ts = now_utc().timestamp() - (days_to_keep * 86400)

    rows = list_docs(
        COLL.notifications,
        predicate=lambda row: _same_id(row.get("user_id"), user_id) and row.get("is_read", False),
        limit=500,
    )

    deleted = 0
    for row in rows:
        read_at = row.get("read_at") or row.get("updated_at") or row.get("created_at")
        read_dt = _parse_datetime(read_at) if isinstance(read_at, str) else read_at

        if not isinstance(read_dt, datetime):
            continue
        if read_dt.tzinfo is None:
            read_dt = read_dt.replace(tzinfo=timezone.utc)

        if read_dt.timestamp() <= cutoff_ts:
            delete_doc(COLL.notifications, row.get("id"))
            deleted += 1

    return deleted


def _downgrade_if_expired(user: dict) -> bool:
    expiry = user.get("premium_expiry")
    if not user.get("is_premium") or not expiry:
        return False

    # Parse expiry to timezone-aware datetime
    expiry_dt = _parse_datetime(expiry) if isinstance(expiry, str) else expiry
    if isinstance(expiry_dt, datetime) and expiry_dt.tzinfo is None:
        expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)

    # Only act when membership is actually expired.
    if not expiry_dt or now_utc() < expiry_dt:
        return False

    update_doc(
        COLL.users,
        user["id"],
        {"is_premium": False, "premium_expiry": None, "updated_at": now_utc()},
    )

    existing_unread = first_doc(
        COLL.notifications,
        predicate=lambda row: _same_id(row.get("user_id"), user.get("id"))
        and row.get("notification_type") == "premium_expiry"
        and not row.get("is_read", False),
    )

    if not existing_unread:
        create_doc(
            COLL.notifications,
            {
                "user_id": user["id"],
                "title": "Premium Membership Expired",
                "message": "Your premium membership expired. Featured premium visibility is now disabled until you renew.",
                "notification_type": "premium_expiry",
                "is_read": False,
                "created_at": now_utc(),
            },
        )

    return True

    return False


@router.get("/me", response_model=list[NotificationResponse])
async def get_my_notifications(current_user=Depends(get_current_user)):
    _cleanup_old_read_notifications(current_user.id, days_to_keep=7)

    notifications = list_docs(
        COLL.notifications,
        predicate=lambda row: _same_id(row.get("user_id"), current_user.id),
        sort_key="created_at",
        reverse=True,
        limit=100,
    )
    return [as_obj(row) for row in notifications]


@router.post("/check-expiry")
async def check_premium_expiry_notification(current_user=Depends(get_current_user)):
    user = first_doc(COLL.users, predicate=lambda row: _same_id(row.get("id"), current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expired = _downgrade_if_expired(user)

    if expired:
        return {
            "message": "Premium already expired. Expiry notification created.",
            "days_left": 0,
            "notification_created": True,
        }

    if not user.get("is_premium") or not user.get("premium_expiry"):
        return {
            "message": "No active premium subscription.",
            "days_left": None,
            "notification_created": False,
        }

    expiry_dt = _parse_datetime(user["premium_expiry"]) if isinstance(user["premium_expiry"], str) else user["premium_expiry"]
    days_left = (expiry_dt - now_utc()).total_seconds() / 86400 if expiry_dt else None

    if days_left > 3:
        return {
            "message": "Premium subscription is active.",
            "days_left": round(days_left, 1),
            "notification_created": False,
        }

    if days_left < 0:
        return {
            "message": "Premium already expired.",
            "days_left": 0,
            "notification_created": False,
        }

    existing = first_doc(
        COLL.notifications,
        predicate=lambda row: _same_id(row.get("user_id"), current_user.id)
        and row.get("notification_type") == "premium_expiry_warning"
        and not row.get("is_read", False),
    )

    if existing:
        return {
            "message": "Expiry warning already exists.",
            "days_left": round(days_left, 1),
            "notification_created": False,
        }

    create_doc(
        COLL.notifications,
        {
            "user_id": current_user.id,
            "title": "Premium Expiry Reminder",
            "message": f"Your premium membership expires in {int(round(days_left))} day(s). Renew to stay featured.",
            "notification_type": "premium_expiry_warning",
            "is_read": False,
            "created_at": now_utc(),
        },
    )

    log_action("Premium expiry warning created", user_id=current_user.id)

    return {
        "message": "Expiry warning created.",
        "days_left": round(days_left, 1),
        "notification_created": True,
    }


@router.put("/{notification_id}/read")
async def mark_notification_as_read(notification_id: int, current_user=Depends(get_current_user)):
    notification = first_doc(
        COLL.notifications,
        predicate=lambda row: _same_id(row.get("id"), notification_id) and _same_id(row.get("user_id"), current_user.id),
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    update_doc(
        COLL.notifications,
        notification_id,
        {"is_read": True, "read_at": now_utc(), "updated_at": now_utc()},
    )

    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_notifications_as_read(current_user=Depends(get_current_user)):
    rows = list_docs(
        COLL.notifications,
        predicate=lambda row: _same_id(row.get("user_id"), current_user.id) and not row.get("is_read", False),
    )
    for row in rows:
        update_doc(
            COLL.notifications,
            row["id"],
            {"is_read": True, "read_at": now_utc(), "updated_at": now_utc()},
        )

    return {"message": "All notifications marked as read"}


@router.delete("/clear-read")
async def clear_read_notifications(current_user=Depends(get_current_user)):
    rows = list_docs(
        COLL.notifications,
        predicate=lambda row: _same_id(row.get("user_id"), current_user.id) and row.get("is_read", False),
        limit=500,
    )

    deleted = 0
    for row in rows:
        if delete_doc(COLL.notifications, row.get("id")):
            deleted += 1

    return {"message": "Read notifications cleared", "deleted": deleted}


@router.delete("/{notification_id}")
async def delete_read_notification(notification_id: int, current_user=Depends(get_current_user)):
    notification = first_doc(
        COLL.notifications,
        predicate=lambda row: _same_id(row.get("id"), notification_id) and _same_id(row.get("user_id"), current_user.id),
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if not notification.get("is_read", False):
        raise HTTPException(status_code=400, detail="Only read notifications can be removed")

    delete_doc(COLL.notifications, notification_id)
    return {"message": "Notification removed"}
