from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import load_users, save_users
from app.permissions.permissions import require_permissions


router = APIRouter()


@router.delete("/users/{username}")
def delete_user(username: str, user=Depends(require_permissions("delete_user"))):
    users = load_users()
    updated_users = [item for item in users if item["username"] != username]

    if len(updated_users) == len(users):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    save_users(updated_users)

    return {
        "message": f"User '{username}' deleted",
        "deleted_by": user["sub"],
    }
