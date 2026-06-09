import logging
import os
from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI

from app.api.routes import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Checking Redis connection...")
    try:
        r = redis.from_url(REDIS_URL)
        if r.ping():
            logger.info(f"Successfully connected to Redis at {REDIS_URL}")
        else:
            logger.error(f"Failed to connect to Redis at {REDIS_URL}")
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        logger.warning("Application might not be able to process background tasks.")
    
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title="FastAPI + Celery + Redis Demo",
    description="Background job processing with Celery and Redis broker",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api", tags=["jobs"])


@app.get("/")
def root():
    return {
        "message": "FastAPI + Celery + Redis is running",
        "docs": "/docs",
        "redis_url": REDIS_URL,
    }
