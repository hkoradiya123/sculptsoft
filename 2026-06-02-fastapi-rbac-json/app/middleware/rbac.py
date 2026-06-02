import json
from pathlib import Path

from fastapi import Depends, HTTPException, Request, status

from app.auth.jwt_auth import get_current_user


BASE_DIR = Path(__file__).resolve().parents[1]
PERMISSIONS_FILE = BASE_DIR / "config" / "permissions.json"

PERMISSIONS: dict = {"routes": {}}
PERMISSION_MAP: dict[str, list[str]] = {}


def load_permissions() -> dict:
    with PERMISSIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_permission_map() -> None:
    global PERMISSIONS, PERMISSION_MAP

    PERMISSIONS = load_permissions()
    permission_map: dict[str, list[str]] = {}

    for path, methods in PERMISSIONS.get("routes", {}).items():
        for method, roles in methods.items():
            permission_map[f"{method.upper()}:{path}"] = roles

    PERMISSION_MAP = permission_map
    

def rbac():
    async def checker(
        request: Request,
        current_user: dict = Depends(get_current_user),
    ):
        route = request.scope.get("route")
        if route is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Route not resolved",
            )

        path = route.path
        method = request.method.upper()
        role = current_user["role"]

        key = f"{method}:{path}"
        allowed_roles = PERMISSION_MAP.get(key)

        if allowed_roles is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Route/method not configured",
            )

        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    return checker
