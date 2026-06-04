from fastapi import FastAPI

from app.db.session import seed_default_users
from app.middleware.rbac import build_permission_map, rbac_middleware
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router


app = FastAPI(title="FastAPI JSON RBAC")

app.middleware("http")(rbac_middleware)


@app.on_event("startup")
def startup_event() -> None:
    build_permission_map()
    # seed_default_users()


@app.get("/")
def home():
    return {"message": "RBAC API running"}


app.include_router(users_router)
app.include_router(auth_router)
