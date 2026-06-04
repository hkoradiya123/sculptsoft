from fastapi import FastAPI

from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.db.session import create_all_and_seed


app = FastAPI(title="FastAPI RBAC")

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(products_router)


@app.get("/")
def home():
    return {"message": "API Running"}


@app.on_event("startup")
def on_startup():
    # create tables and seed default data
    create_all_and_seed()
