from fastapi import FastAPI

from .api import router
from .db import init_db, seed_data

app = FastAPI(title="FastAPI CRUD")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    await seed_data()


app.include_router(router)
