from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from app.schemas import PremiumUpgradeRequest, PremiumResponse, PaymentResponse
from app.middleware.auth import get_current_user
from app.utils.firestore_data import COLL, as_obj, create_doc, first_doc, list_docs, now_utc, update_doc, _parse_datetime
from app.utils.logger import log_action

router = APIRouter(prefix="/premium", tags=["Premium"])


@router.post("/upgrade", response_model=PremiumResponse)
async def upgrade_to_premium_plan(
    request_data: PremiumUpgradeRequest,
    current_user=Depends(get_current_user),
):
    """Create premium request for admin approval."""
    
    user = first_doc(COLL.users, predicate=lambda row: row.get("id") == current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("is_premium"):
        raise HTTPException(status_code=400, detail="You are already a premium member")

    latest_request = first_doc(
        COLL.admin_chat_messages,
        predicate=lambda row: row.get("sender_role") == "player"
        and str(row.get("user_id")) == str(current_user.id)
        and str(row.get("message", "")).startswith("PREMIUM_UPGRADE_REQUEST"),
        sort_key="created_at",
        reverse=True,
    )

    if latest_request and not latest_request.get("is_read", False):
        raise HTTPException(status_code=400, detail="Premium request already sent. Please wait for admin approval")

    create_doc(
        COLL.admin_chat_messages,
        {
            "user_id": current_user.id,
            "sender_role": "player",
            "message": f"PREMIUM_UPGRADE_REQUEST | plan_days={request_data.plan_days} | amount=1000",
            "is_read": False,
            "created_at": now_utc(),
        },
    )

    log_action("Premium upgrade requested", user_id=user["id"], details=f"{request_data.plan_days} days")
    
    return {
        "is_premium": user.get("is_premium", False),
        "premium_expiry": user.get("premium_expiry"),
        "message": "Premium request sent to admin. You will be upgraded after approval."
    }


@router.get("/status", response_model=PremiumResponse)
async def get_premium_status(
    current_user=Depends(get_current_user),
):
    """Get current premium status"""
    
    user = first_doc(COLL.users, predicate=lambda row: row.get("id") == current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expiry = user.get("premium_expiry")
    if user.get("is_premium") and expiry:
        from datetime import timezone
        # Parse expiry to timezone-aware datetime
        expiry_dt = _parse_datetime(expiry) if isinstance(expiry, str) else expiry
        
        # Ensure expiry_dt is timezone-aware
        if isinstance(expiry_dt, datetime) and expiry_dt.tzinfo is None:
            expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
        
        # Check if premium has expired
        if expiry_dt and now_utc() >= expiry_dt:
            user = update_doc(
                COLL.users,
                user["id"],
                {"is_premium": False, "premium_expiry": None, "updated_at": now_utc()},
            ) or user
    
    if user.get("is_premium"):
        expiry = user.get("premium_expiry")
        from datetime import timezone
        # Ensure timezone-aware datetime for formatting
        if isinstance(expiry, str):
            expiry = _parse_datetime(expiry) or now_utc()
        elif isinstance(expiry, datetime) and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        message = f"Premium active until {expiry.strftime('%Y-%m-%d')}" if expiry else "Premium active"
    else:
        message = "Not a premium member. Upgrade to get featured!"
    
    return {
        "is_premium": user.get("is_premium", False),
        "premium_expiry": user.get("premium_expiry"),
        "message": message
    }


@router.post("/cancel")
async def cancel_premium(
    current_user=Depends(get_current_user),
):
    """Cancel premium membership"""
    
    user = first_doc(COLL.users, predicate=lambda row: row.get("id") == current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.get("is_premium"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a premium member"
        )
    
    update_doc(
        COLL.users,
        user["id"],
        {"is_premium": False, "premium_expiry": None, "updated_at": now_utc()},
    )
    
    log_action("Premium cancelled", user_id=user["id"])
    
    return {"message": "Premium membership cancelled"}


@router.get("/payments", response_model=list)
async def get_payment_history(
    current_user=Depends(get_current_user),
):
    """Get payment history"""
    
    payments = list_docs(
        COLL.payments,
        predicate=lambda row: row.get("user_id") == current_user.id,
        sort_key="created_at",
        reverse=True,
    )
    return [as_obj(row) for row in payments]
