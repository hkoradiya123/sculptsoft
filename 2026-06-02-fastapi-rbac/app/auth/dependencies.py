import json
from pathlib import Path

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt_handler import decode_access_token


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

DEFAULT_USERS = [
    {"username": "admin", "password": "admin123", "roles": ["admin"]},
    {"username": "seller1", "password": "seller123", "roles": ["seller"]},
    {"username": "user1", "password": "user123", "roles": ["user"]},
]


def ensure_users_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps(DEFAULT_USERS, indent=4), encoding="utf-8")


def load_users() -> list[dict]:
    ensure_users_file()

    with USERS_FILE.open("r", encoding="utf-8") as file:
        users = json.load(file)

    normalized_users = []

    for user in users:
        roles = user.get("roles")
        if not isinstance(roles, list):
            legacy_role = user.get("role")
            roles = [legacy_role] if legacy_role else ["user"]

        normalized_users.append(
            {
                "username": user["username"],
                "password": user["password"],
                "roles": roles,
            }
        )

    return normalized_users


def save_users(users: list[dict]) -> None:
    ensure_users_file()

    USERS_FILE.write_text(json.dumps(users, indent=4), encoding="utf-8")


def find_user_by_username(username: str) -> dict | None:
    return next((user for user in load_users() if user["username"] == username), None)


def verify_token(token: str = Depends(oauth2_scheme)):
    return decode_access_token(token)
