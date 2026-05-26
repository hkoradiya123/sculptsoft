from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.deps import get_db
from api.deps.auth import admin_required, get_current_user
from api.schemas import (
    InventoryCreate,
    InventoryRead,
    InventoryUpdate,
    LocationCreate,
    LocationRead,
    LocationUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    StockCreate,
    StockRead,
    StockUpdate,
)
from api.schemas.auth import LoginRequest, RegisterRequest
from core.security import create_access_token, hash_password, verify_password
from database.model.inventory import Inventory as InventoryModel
from database.model.inventory import Location as LocationModel
from database.model.product import Product as ProductModel
from database.model.stock import Stock as StockModel
from database.model.user import User

app = FastAPI(title="Inventory Management API", version="1.0.0")


@app.post("/login", tags=["auth"])
def login(payload: LoginRequest, session: Session = Depends(get_db)):
    user = session.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/register", tags=["auth"], status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Session = Depends(get_db)):
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    return {"message": "User created"}


def get_inventory_or_404(session: Session, inventory_id: int) -> InventoryModel:
    inventory = session.get(InventoryModel, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


def get_product_or_404(session: Session, product_id: int) -> ProductModel:
    product = session.get(ProductModel, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def get_stock_or_404(session: Session, inventory_id: int, stock_id: int) -> StockModel:
    stock = session.get(StockModel, stock_id)
    if stock is None or stock.inventory_id != inventory_id:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@app.get("/inventories", response_model=List[InventoryRead], tags=["inventories"])
def list_inventories(
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return session.query(InventoryModel).order_by(InventoryModel.inventory_id).all()


@app.post(
    "/inventories",
    response_model=InventoryRead,
    status_code=status.HTTP_201_CREATED,
    tags=["inventories"],
)
def create_inventory(
    payload: InventoryCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    inventory = InventoryModel(**payload.dict())
    session.add(inventory)
    session.commit()
    session.refresh(inventory)
    return inventory


@app.get(
    "/inventories/{inventory_id}",
    response_model=InventoryRead,
    tags=["inventories"],
)
def get_inventory(
    inventory_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_inventory_or_404(session, inventory_id)


@app.patch(
    "/inventories/{inventory_id}",
    response_model=InventoryRead,
    tags=["inventories"],
)
def update_inventory(
    inventory_id: int,
    payload: InventoryUpdate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    inventory = get_inventory_or_404(session, inventory_id)
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(inventory, key, value)
    session.commit()
    session.refresh(inventory)
    return inventory


@app.delete(
    "/inventories/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["inventories"],
)
def delete_inventory(
    inventory_id: int,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    inventory = get_inventory_or_404(session, inventory_id)
    session.delete(inventory)
    session.commit()
    return None


@app.get(
    "/inventories/{inventory_id}/locations",
    response_model=List[LocationRead],
    tags=["inventories"],
)
def list_locations(
    inventory_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    return (
        session.query(LocationModel)
        .filter(LocationModel.inventory_id == inventory_id)
        .order_by(LocationModel.location_id)
        .all()
    )


@app.post(
    "/inventories/{inventory_id}/locations",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["inventories"],
)
def create_location(
    inventory_id: int,
    payload: LocationCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    location = LocationModel(inventory_id=inventory_id, **payload.dict())
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@app.patch(
    "/inventories/{inventory_id}/locations/{location_id}",
    response_model=LocationRead,
    tags=["inventories"],
)
def update_location(
    inventory_id: int,
    location_id: int,
    payload: LocationUpdate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    location = session.get(LocationModel, location_id)
    if location is None or location.inventory_id != inventory_id:
        raise HTTPException(status_code=404, detail="Location not found")
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(location, key, value)
    session.commit()
    session.refresh(location)
    return location


@app.delete(
    "/inventories/{inventory_id}/locations/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["inventories"],
)
def delete_location(
    inventory_id: int,
    location_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    location = session.get(LocationModel, location_id)
    if location is None or location.inventory_id != inventory_id:
        raise HTTPException(status_code=404, detail="Location not found")
    session.delete(location)
    session.commit()
    return None


@app.get("/products", response_model=List[ProductRead], tags=["products"])
def list_products(
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return session.query(ProductModel).order_by(ProductModel.product_id).all()


@app.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    tags=["products"],
)
def create_product(
    payload: ProductCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    product = ProductModel(**payload.dict())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.get(
    "/products/{product_id}",
    response_model=ProductRead,
    tags=["products"],
)
def get_product(
    product_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_product_or_404(session, product_id)


@app.patch(
    "/products/{product_id}",
    response_model=ProductRead,
    tags=["products"],
)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    product = get_product_or_404(session, product_id)
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(product, key, value)
    session.commit()
    session.refresh(product)
    return product


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["products"],
)
def delete_product(
    product_id: int,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    product = get_product_or_404(session, product_id)
    session.delete(product)
    session.commit()
    return None


@app.get(
    "/inventories/{inventory_id}/stock",
    response_model=List[StockRead],
    tags=["stock"],
)
def list_stock(
    inventory_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    rows = (
        session.query(StockModel, ProductModel, LocationModel)
        .join(ProductModel, StockModel.product_id == ProductModel.product_id)
        .join(LocationModel, StockModel.location_id == LocationModel.location_id)
        .filter(StockModel.inventory_id == inventory_id)
        .order_by(StockModel.stock_id)
        .all()
    )
    results = []
    for stock, product, location in rows:
        results.append(
            StockRead(
                stock_id=stock.stock_id,
                product_id=stock.product_id,
                product_name=product.name,
                location_id=stock.location_id,
                location_address=location.address,
                quantity=stock.quantity,
            )
        )
    return results


@app.post(
    "/inventories/{inventory_id}/stock",
    response_model=StockRead,
    status_code=status.HTTP_201_CREATED,
    tags=["stock"],
)
def add_stock(
    inventory_id: int,
    payload: StockCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    product = session.get(ProductModel, payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    location = session.get(LocationModel, payload.location_id)
    if location is None or location.inventory_id != inventory_id:
        raise HTTPException(status_code=404, detail="Location not found")

    stock = StockModel(
        product_id=payload.product_id,
        inventory_id=inventory_id,
        location_id=payload.location_id,
        quantity=payload.quantity,
    )
    session.add(stock)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stock entry already exists for this product and location",
        )
    session.refresh(stock)

    return StockRead(
        stock_id=stock.stock_id,
        product_id=stock.product_id,
        product_name=product.name,
        location_id=stock.location_id,
        location_address=location.address,
        quantity=stock.quantity,
    )


@app.patch(
    "/inventories/{inventory_id}/stock/{stock_id}",
    response_model=StockRead,
    tags=["stock"],
)
def update_stock(
    inventory_id: int,
    stock_id: int,
    payload: StockUpdate,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    get_inventory_or_404(session, inventory_id)
    stock = get_stock_or_404(session, inventory_id, stock_id)
    stock.quantity = payload.quantity
    session.commit()
    session.refresh(stock)

    product = session.get(ProductModel, stock.product_id)
    location = session.get(LocationModel, stock.location_id)

    return StockRead(
        stock_id=stock.stock_id,
        product_id=stock.product_id,
        product_name=product.name if product else None,
        location_id=stock.location_id,
        location_address=location.address if location else None,
        quantity=stock.quantity,
    )


@app.delete(
    "/inventories/{inventory_id}/stock/{stock_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["stock"],
)
def delete_stock(
    inventory_id: int,
    stock_id: int,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    get_inventory_or_404(session, inventory_id)
    stock = get_stock_or_404(session, inventory_id, stock_id)
    session.delete(stock)
    session.commit()
    return None
