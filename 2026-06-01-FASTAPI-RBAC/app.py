from datetime import datetime, timedelta
from typing import Generator, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

APP_NAME = "FastAPI RBAC"

app = FastAPI(title=APP_NAME)

# -------------------------
# Config
# -------------------------

SECRET_KEY = "replace_this_with_a_strong_random_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

DATABASE_URL =  "sqlite:///./users.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    scopes = Column(String, nullable=True, default="")


Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    scopes: Optional[list[str]] = []


class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"
    scopes: Optional[list[str]] = None


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    scopes: list[str] = []

    class Config:
        orm_mode = True


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, password: str, role: str = "user", scopes: Optional[list[str]] = None) -> User:
    hashed = hash_password(password)
    scopes_csv = ",".join(scopes) if scopes else ""
    db_user = User(username=username, hashed_password=hashed, role=role, scopes=scopes_csv)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def ensure_default_users(db: Session):
    if not get_user_by_username(db, "admin"):
        create_user(db, "admin", "admin123", role="admin", scopes=["users:create", "users:read", "users:delete", "admin"])
    if not get_user_by_username(db, "user1"):
        create_user(db, "user1", "user123", role="user", scopes=["users:read"])


# Initialize defaults
with SessionLocal() as db:
    ensure_default_users(db)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        scopes_payload = payload.get("scopes", [])
        if username is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        token_data = TokenData(username=username, role=role, scopes=scopes_payload)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return token_data


def require_roles(*allowed_roles: str):
    def role_checker(token_data: TokenData = Depends(verify_token)):
        if token_data.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return token_data

    return role_checker


def require_scopes(*required_scopes: str):
    def scope_checker(token_data: TokenData = Depends(verify_token)):
        token_scopes = set(token_data.scopes or [])
        missing = [s for s in required_scopes if s not in token_scopes]
        if missing:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing scopes: {missing}")
        return token_data

    return scope_checker


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    # include scopes from DB in token
    user_scopes = user.scopes.split(",") if user.scopes else []
    access_token = create_access_token(data={"sub": user.username, "role": user.role, "scopes": user_scopes}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/dashboard", response_model=dict)
def dashboard(token_data: TokenData = Depends(verify_token)):
    return {"message": f"Welcome {token_data.username}", "role": token_data.role, "scopes": token_data.scopes}


@app.get("/admin", response_model=dict)
def admin_panel(token_data: TokenData = Depends(require_scopes("admin"))):
    return {"message": f"Welcome admin {token_data.username}", "scopes": token_data.scopes}


@app.post("/users", response_model=UserOut, status_code=201)
def create_new_user(user_in: UserCreate, db: Session = Depends(get_db), caller=Depends(require_scopes("users:create"))):
    if get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = create_user(db, user_in.username, user_in.password, role=user_in.role or "user", scopes=user_in.scopes)
    # convert stored CSV scopes to list for response
    out = UserOut.from_orm(new_user)
    out.scopes = new_user.scopes.split(",") if new_user.scopes else []
    return out


@app.get("/")
def home():
    return {"message": "API Running"}
