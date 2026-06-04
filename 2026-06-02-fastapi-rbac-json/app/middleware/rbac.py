import json
import re
from pathlib import Path

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.auth.jwt_auth import load_current_user
from app.db.session import SessionLocal


BASE_DIR = Path(__file__).resolve().parents[1]
PERMISSIONS_FILE = BASE_DIR / "config" / "permissions.json"
ROLES_FILE = BASE_DIR / "config" / "roles.json"
PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/redoc", "/api/v1/auth/login", "/api/v1/auth/me","/api/v1/signup"}

PERMISSIONS: dict = {"routes": {}}
PERMISSION_MAP: dict[str, list[str]] = {}
PERMISSION_RULES: list[tuple[str, str, list[str]]] = []
ROLES_RULES: list[tuple[str, str, list[str]]] = []


def load_permissions() -> dict:
    with PERMISSIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)
    
def load_roles() -> dict:
    with ROLES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_permission_map() -> None:
    global PERMISSIONS, PERMISSION_MAP, PERMISSION_RULES, ROLES_RULES

    PERMISSIONS = load_permissions()
    ROLES = load_roles()
    ROLES = ROLES.get("roles", [])
    permission_map: dict[str, list[str]] = {}
    permission_rules: list[tuple[str, str, list[str]]] = []
    roles_rules: list[tuple[str, str, list[str]]] = []

    for path, methods in PERMISSIONS.get("routes", {}).items():
        for method, roles in methods.items():
            permission_map[f"{method.upper()}:{path}"] = roles
            permission_rules.append((method.upper(), path, roles))
            
    # for role in ROLES.get("roles", []):
    #     roles_rules.append((role, role, [role]))
    ROLES_RULES = ROLES
    # print("Loaded roles rules:", ROLES_RULES)
    PERMISSION_MAP = permission_map
    PERMISSION_RULES = permission_rules
    ROLES_RULES = roles_rules


def _path_matches(pattern: str, path: str) -> bool:
    escaped = re.escape(pattern)
    regex = re.sub(r"\\\{[^/]+\\\}", r"[^/]+", escaped)
    return re.fullmatch(regex, path) is not None


def resolve_allowed_roles(method: str, path: str) -> list[str] | None:
    for configured_method, configured_path, roles in PERMISSION_RULES:
        if configured_method == method and _path_matches(configured_path, path):
            return roles
    return None


async def rbac_middleware(request: Request, call_next):
    path = request.url.path

    if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
        return await call_next(request)

    if not path.startswith("/api/v1/"):
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

    db = SessionLocal()
    try:
        current_user = load_current_user(db, token)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers or None,
        )
    finally:
        db.close()

    request.state.current_user = current_user

    if path.startswith("/api/v1/auth/"):
        return await call_next(request)

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
