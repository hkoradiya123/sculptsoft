from fastapi import FastAPI

from database import Base, engine
from routes import router

# CREATE TABLES
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)
