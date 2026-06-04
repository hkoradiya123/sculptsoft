from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
import json
import os

app = FastAPI()


SECRET_KEY = "my_super_secret_key_change_this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


DEFAULT_USERS = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "user1", "password": "user123", "role": "user"},
]

USERS_FILE = "users.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump(DEFAULT_USERS, f, indent=4)

with open(USERS_FILE, "r") as f:
    users = json.load(f)

for user in users:
    user.setdefault("role", "user")

print("Loaded users:", users)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        if username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return payload

    except JWTError as e:
        print("JWT ERROR:", str(e))

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def require_roles(*allowed_roles: str):
    def role_checker(user=Depends(verify_token)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return user

    return role_checker


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = next(
        (
            u for u in users
            if u["username"] == form_data.username
            and u["password"] == form_data.password
        ),
        None
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user["username"],
        "role": user["role"],
        "exp": expire
    }

    access_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/dashboard")
def dashboard(user=Depends(verify_token)):
    return {
        "message": f"Welcome {user['sub']}",
        "role": user["role"]
    }


@app.get("/admin")
def admin_panel(user=Depends(require_roles("admin"))):
    return {
        "message": f"Welcome admin {user['sub']}"
    }


@app.get("/")
def home():
    return {
        "message": "API Running"
    }