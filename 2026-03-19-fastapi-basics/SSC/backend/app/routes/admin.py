from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from typing import List, Union
import uuid

from app.config import settings
from app.schemas import AdminChatCreate, AdminChatResponse
from app.middleware.auth import get_admin_user, get_current_user
from app.utils.auth import hash_password
from app.utils.firestore_data import COLL, _parse_datetime, as_obj, create_doc, delete_doc, first_doc, list_docs, now_utc, update_doc
from app.utils.logger import log_action

router = APIRouter(prefix="/admin", tags=["Admin"])


def _same_id(left, right) -> bool:
    if left is None or right is None:
        return False
    return str(left) == str(right)


def _matches_user_identity(row: dict, value: Union[int, str]) -> bool:
    return _same_id(row.get("id"), value) or _same_id(row.get("uid"), value)


def _current_user_chat_ids(current_user) -> set[str]:
    ids = set()
    for value in (getattr(current_user, "id", None), getattr(current_user, "uid", None)):
        if value is not None:
            ids.add(str(value))
    return ids


def _sort_ts(value) -> float:
    if value is None:
        return float("-inf")
    dt = _parse_datetime(value) if isinstance(value, str) else value
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    return float("-inf")


@router.get("/users", response_model=List)
async def list_all_users(skip: int = 0, limit: int = 100, admin=Depends(get_admin_user)):
    users = list_docs(COLL.users, sort_key="created_at", reverse=True, offset=skip, limit=limit)
    log_action("Admin viewed all users", user_id=admin.id)
    return [
        {
            "id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
            "is_active": user.get("is_active", True),
            "is_premium": user.get("is_premium", False),
            "runs": user.get("runs", 0),
            "matches": user.get("matches", 0),
            "wickets": user.get("wickets", 0),
            "created_at": user.get("created_at"),
        }
        for user in users
    ]


@router.put("/users/{user_id}/premium")
async def toggle_user_premium(user_id: Union[int, str], days: int = 30, admin=Depends(get_admin_user)):
    user = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, user_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    is_premium = not user.get("is_premium", False)
    patch = {"is_premium": is_premium, "updated_at": now_utc()}

    if is_premium:
        from datetime import timedelta
        patch["premium_expiry"] = now_utc() + timedelta(days=days)
        patch["premium_start_date"] = now_utc()
    else:
        patch["premium_expiry"] = None

    update_doc(COLL.users, user.get("_doc_id") or user.get("id"), patch)
    log_action("Admin toggled user premium", user_id=admin.id, details=f"User {user_id}")

    return {"message": "User premium status updated"}


@router.post("/users/{user_id}/approve-premium")
async def approve_premium_request(user_id: Union[int, str], days: int = 30, admin=Depends(get_admin_user)):
    user = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, user_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.get("role") != "player":
        raise HTTPException(status_code=400, detail="Only players can be upgraded to premium")

    if user.get("is_premium", False):
        raise HTTPException(status_code=400, detail="User is already premium")

    now = now_utc()
    expiry = now + timedelta(days=days)
    update_doc(
        COLL.users,
        user.get("_doc_id") or user.get("id"),
        {
            "is_premium": True,
            "premium_start_date": now,
            "premium_expiry": expiry,
            "updated_at": now,
        },
    )

    transaction_id = str(uuid.uuid4())
    create_doc(
        COLL.payments,
        {
            "user_id": user.get("id"),
            "amount": float(settings.PREMIUM_COST),
            "payment_method": "admin_approved",
            "transaction_id": transaction_id,
            "status": "completed",
            "plan_duration_days": days,
            "created_at": now,
            "updated_at": now,
        },
    )

    create_doc(
        COLL.finance_transactions,
        {
            "user_id": user.get("id"),
            "transaction_type": "credit",
            "amount": float(settings.PREMIUM_COST),
            "category": "premium_payment",
            "description": f"Premium approved by admin for {user.get('email')}",
            "reference_id": transaction_id,
            "created_at": now,
        },
    )

    create_doc(
        COLL.admin_chat_messages,
        {
            "user_id": user.get("uid") or user.get("id"),
            "sender_role": "admin",
            "message": f"Your premium request has been approved for {days} days.",
            "is_read": False,
            "created_at": now,
        },
    )

    log_action("Admin approved premium request", user_id=admin.id, details=f"User {user_id}")
    return {"message": "Premium request approved and user upgraded"}


@router.delete("/users/{user_id}")
async def deactivate_user(user_id: Union[int, str], admin=Depends(get_admin_user)):
    user = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, user_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if _same_id(user.get("id"), admin.id):
        raise HTTPException(status_code=400, detail="You cannot deactivate your own admin account")

    update_doc(COLL.users, user.get("_doc_id") or user.get("id"), {"is_active": False, "updated_at": now_utc()})

    log_action("Admin deactivated user", user_id=admin.id, details=f"User {user_id}")

    return {"message": "User deactivated successfully"}


@router.post("/users/{user_id}/activate")
async def activate_user(user_id: Union[int, str], admin=Depends(get_admin_user)):
    user = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, user_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_doc(COLL.users, user.get("_doc_id") or user.get("id"), {"is_active": True, "updated_at": now_utc()})

    log_action("Admin activated user", user_id=admin.id, details=f"User {user_id}")
    return {"message": "User activated successfully"}


@router.put("/users/{user_id}/role")
async def update_user_role(user_id: Union[int, str], role: str, admin=Depends(get_admin_user)):
    normalized_role = (role or "").strip().lower()
    if normalized_role not in {"admin", "player"}:
        raise HTTPException(status_code=400, detail="Role must be either 'admin' or 'player'")

    user = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if _same_id(user.get("id"), admin.id) and normalized_role != "admin":
        raise HTTPException(status_code=400, detail="You cannot remove your own admin role")

    update_doc(
        COLL.users,
        user.get("_doc_id") or user.get("id"),
        {"role": normalized_role, "updated_at": now_utc()},
    )

    log_action("Admin updated user role", user_id=admin.id, details=f"User {user_id} -> {normalized_role}")
    return {"message": "User role updated successfully"}


@router.delete("/users/{user_id}/hard-delete")
async def hard_delete_user(user_id: Union[int, str], admin=Depends(get_admin_user)):
    user = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, user_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if _same_id(user.get("id"), admin.id):
        raise HTTPException(status_code=400, detail="You cannot delete your own admin account")

    effective_user_ids = {str(user.get("id")), str(user.get("uid"))}
    chats = list_docs(COLL.admin_chat_messages, limit=5000)
    for message in chats:
        if str(message.get("user_id")) in effective_user_ids:
            delete_doc(COLL.admin_chat_messages, message.get("id"))

    delete_doc(COLL.users, user.get("_doc_id") or user.get("id"))

    log_action("Admin hard deleted user", user_id=admin.id, details=f"User {user_id}")
    return {"message": "User deleted permanently"}


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(user_id: Union[int, str], admin=Depends(get_admin_user)):
    user = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, user_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    temporary_password = "123456"
    update_doc(
        COLL.users,
        user.get("_doc_id") or user.get("id"),
        {
            "password": hash_password(temporary_password),
            "updated_at": now_utc(),
        },
    )

    log_action("Admin reset user password", user_id=admin.id, details=f"User {user_id}")
    return {"message": "Password reset to 123456"}


@router.get("/stats")
async def get_system_stats(admin=Depends(get_admin_user)):
    users = list_docs(COLL.users)
    payments = list_docs(COLL.payments, predicate=lambda row: row.get("status") == "completed")
    transactions = list_docs(COLL.finance_transactions)
    chats = list_docs(COLL.admin_chat_messages)

    total_users = len(users)
    active_users = len([u for u in users if u.get("is_active", True)])
    premium_users = len([u for u in users if u.get("is_premium", False)])
    total_matches = sum(int(u.get("matches", 0)) for u in users)

    paid_user_ids = {row.get("user_id") for row in payments}
    active_players = [u for u in users if u.get("is_active", True) and u.get("role") == "player"]
    unpaid_players = [u for u in active_players if u.get("id") not in paid_user_ids]

    pending_funds = len(unpaid_players) * settings.PREMIUM_COST

    total_collected = sum(float(row.get("amount", 0)) for row in payments)
    manual_credits = sum(
        float(row.get("amount", 0))
        for row in transactions
        if row.get("transaction_type") == "credit" and row.get("category") == "manual_credit"
    )
    total_debits = sum(float(row.get("amount", 0)) for row in transactions if row.get("transaction_type") == "debit")
    funds_remaining = round((total_collected + manual_credits) - total_debits, 2)

    unread_chat_messages = len(
        [m for m in chats if m.get("sender_role") == "player" and not m.get("is_read", False)]
    )

    log_action("Admin viewed system stats", user_id=admin.id)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "premium_users": premium_users,
        "total_matches": total_matches,
        "pending_funds": pending_funds,
        "funds_remaining": funds_remaining,
        "unread_chat_messages": unread_chat_messages,
    }


@router.get("/chats")
async def get_chat_threads(admin=Depends(get_admin_user)):
    players = list_docs(COLL.users, predicate=lambda row: row.get("role") == "player" and row.get("is_active", True))
    chats = list_docs(COLL.admin_chat_messages, sort_key="created_at", reverse=True)

    threads = []
    for player in players:
        player_messages = [
            m
            for m in chats
            if _same_id(m.get("user_id"), player.get("id")) or _same_id(m.get("user_id"), player.get("uid"))
        ]
        last_message = player_messages[0] if player_messages else None
        unread_count = len(
            [m for m in player_messages if m.get("sender_role") == "player" and not m.get("is_read", False)]
        )

        thread_user_id = player.get("uid") or player.get("id")

        threads.append(
            {
                "user_id": thread_user_id,
                "name": player.get("name"),
                "email": player.get("email"),
                "unread_count": unread_count,
                "last_message": last_message.get("message") if last_message else None,
                "last_message_at": last_message.get("created_at") if last_message else None,
            }
        )

    threads.sort(key=lambda item: _sort_ts(item.get("last_message_at")), reverse=True)
    return threads


@router.get("/chats/{user_id}", response_model=list[AdminChatResponse])
async def get_chat_thread(user_id: Union[int, str], admin=Depends(get_admin_user)):
    user = first_doc(
        COLL.users,
        predicate=lambda row: _matches_user_identity(row, user_id) and row.get("role") == "player",
    )
    if not user:
        raise HTTPException(status_code=404, detail="Player not found")

    effective_user_id = user.get("uid") or user.get("id")

    messages = list_docs(
        COLL.admin_chat_messages,
        predicate=lambda row: _same_id(row.get("user_id"), effective_user_id) or _same_id(row.get("user_id"), user.get("id")),
        sort_key="created_at",
        reverse=False,
    )

    for message in messages:
        if message.get("sender_role") == "player" and not message.get("is_read", False):
            update_doc(COLL.admin_chat_messages, message["id"], {"is_read": True})
            message["is_read"] = True

    return [as_obj(row) for row in messages]


@router.post("/chats/{user_id}", response_model=AdminChatResponse)
async def send_admin_chat_message(user_id: Union[int, str], payload: AdminChatCreate, admin=Depends(get_admin_user)):
    user = first_doc(
        COLL.users,
        predicate=lambda row: _matches_user_identity(row, user_id) and row.get("role") == "player",
    )
    if not user:
        raise HTTPException(status_code=404, detail="Player not found")

    effective_user_id = user.get("uid") or user.get("id")

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    chat = create_doc(
        COLL.admin_chat_messages,
        {
            "user_id": effective_user_id,
            "sender_role": "admin",
            "message": message,
            "is_read": False,
            "created_at": now_utc(),
        },
    )

    log_action("Admin chat message sent", user_id=admin.id, details=f"to={user_id}")
    return as_obj(chat)


@router.get("/my-chat", response_model=list[AdminChatResponse])
async def get_my_chat(current_user=Depends(get_current_user)):
    chat_ids = _current_user_chat_ids(current_user)

    messages = list_docs(
        COLL.admin_chat_messages,
        predicate=lambda row: str(row.get("user_id")) in chat_ids,
        sort_key="created_at",
        reverse=False,
    )

    for message in messages:
        if message.get("sender_role") == "admin" and not message.get("is_read", False):
            update_doc(COLL.admin_chat_messages, message["id"], {"is_read": True})
            message["is_read"] = True

    return [as_obj(row) for row in messages]


@router.post("/my-chat", response_model=AdminChatResponse)
async def send_message_to_admin(payload: AdminChatCreate, current_user=Depends(get_current_user)):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    effective_user_id = getattr(current_user, "uid", None) or current_user.id

    chat = create_doc(
        COLL.admin_chat_messages,
        {
            "user_id": effective_user_id,
            "sender_role": "player",
            "message": message,
            "is_read": False,
            "created_at": now_utc(),
        },
    )

    log_action("Player chat message sent", user_id=current_user.id)
    return as_obj(chat)
