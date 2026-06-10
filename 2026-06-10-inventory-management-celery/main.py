from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.inventories import router as inventories_router
from app.api.v1.locations import router as locations_router
from app.api.v1.products import router as products_router
from app.api.v1.stock import router as stock_router
from app.api.v1.admin import router as admin_router
from app.api.v1.tasks import router as tasks_router
import app.models  # noqa: F401
from app.database.dbhelper import db
from app.middleware.rbac import build_permission_map, rbac_middleware
from app.services.auth_service import ensure_default_admin

app = FastAPI(title="Inventory Management API", version="1.0.0")

build_permission_map()
app.middleware("http")(rbac_middleware)


@app.get("/", tags=["Health Check"])
def read_root():
    """
    Industry Workflow:
    Root endpoint for Health Checks. 
    Load balancers use this to verify if the service is up.
    """
    return {
        "title": "Inventory Management API",
        "version": "1.0.0",
        "status": "Healthy",
        "documentation": "/docs"
    }


app.include_router(auth_router)
app.include_router(inventories_router)
app.include_router(locations_router)
app.include_router(products_router)
app.include_router(stock_router)
app.include_router(admin_router)
app.include_router(tasks_router)


@app.on_event("startup")
def bootstrap_auth_data() -> None:
    db.create_tables()
    with db.session_scope() as session:
        ensure_default_admin(session)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)
