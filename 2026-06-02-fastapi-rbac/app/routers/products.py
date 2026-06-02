from fastapi import APIRouter, Depends

from app.permissions.permissions import require_permissions


router = APIRouter()


@router.post("/products")
def create_product(user=Depends(require_permissions("manage_products"))):
    return {
        "message": "product created",
        "created_by": user["sub"],
    }
