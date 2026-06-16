import json
import re
from pathlib import Path

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.auth import load_current_user
from app.database.dbhelper import db


BASE_DIR = Path(__file__).resolve().parents[1]
PERMISSIONS_FILE = BASE_DIR / "config" / "permissions.json"
ROLES_FILE = BASE_DIR / "config" / "roles.json"

PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/redoc", "/login", "/register", "/signup"}

PERMISSIONS: dict = {"routes": {}}
PERMISSION_RULES: list[tuple[str, str, list[str]]] = []
ALLOWED_ROLES: set[str] = set()


def load_permissions() -> dict:
    with PERMISSIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_roles() -> dict:
    with ROLES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_permission_map() -> None:
    global PERMISSIONS, PERMISSION_RULES, ALLOWED_ROLES

    PERMISSIONS = load_permissions()
    roles_payload = load_roles()
    ALLOWED_ROLES = {role.strip().lower() for role in roles_payload.get("roles", [])}

    permission_rules: list[tuple[str, str, list[str]]] = []
    for path, methods in PERMISSIONS.get("routes", {}).items():
        for method, roles in methods.items():
            normalized_roles = [role.strip().lower() for role in roles]
            permission_rules.append((method.upper(), path.rstrip("/") or "/", normalized_roles))

    PERMISSION_RULES = permission_rules


def _normalize_path(path: str) -> str:
    return path.rstrip("/") or "/"


def _path_matches(pattern: str, path: str) -> bool:
    escaped = re.escape(pattern)
    regex = re.sub(r"\\\{[^/]+\\\}", r"[^/]+", escaped)
    return re.fullmatch(regex, path) is not None


def resolve_allowed_roles(method: str, path: str) -> list[str] | None:
    normalized_path = _normalize_path(path)
    for configured_method, configured_path, roles in PERMISSION_RULES:
        if configured_method == method and _path_matches(configured_path, normalized_path):
            return roles
    return None


async def rbac_middleware(request: Request, call_next):
    path = _normalize_path(request.url.path)

    if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
        return await call_next(request)

    authorization = request.headers.get("authorization", "")
    if not authorization.lower().startswith("bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing bearer token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing bearer token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    session = db.get_session()
    try:
        current_user = load_current_user(session, token)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers or None,
        )
    finally:
        session.close()

    if current_user["role"] not in ALLOWED_ROLES:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Invalid role configuration"},
        )

    request.state.current_user = current_user

    allowed_roles = resolve_allowed_roles(request.method.upper(), path)
    if allowed_roles is None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Route/method not configured"},
        )

    if current_user["role"] not in allowed_roles:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Access denied"},
        )

    return await call_next(request)


build_permission_map()
