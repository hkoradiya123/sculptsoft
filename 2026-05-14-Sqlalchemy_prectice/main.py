from fastapi import FastAPI

from app.api.v1 import product_routes, user_routes
from app.config.database import Base, engine
from app.models import Product, User


Base.metadata.create_all(bind=engine)

app = FastAPI(title="SQLAlchemy Practice API")

app.include_router(user_routes.router, prefix="/api/v1")
app.include_router(product_routes.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "SQLAlchemy API is running"}
