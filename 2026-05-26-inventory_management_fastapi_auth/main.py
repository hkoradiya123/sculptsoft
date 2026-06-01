from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.inventories import router as inventories_router
from app.api.routes.locations import router as locations_router
from app.api.routes.products import router as products_router
from app.api.routes.stock import router as stock_router

app = FastAPI(title="Inventory Management API", version="1.0.0")

app.include_router(auth_router)
app.include_router(inventories_router)
app.include_router(locations_router)
app.include_router(products_router)
app.include_router(stock_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)

