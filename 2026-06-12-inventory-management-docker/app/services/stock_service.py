from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas import StockCreate, StockRead, StockUpdate
from app.models.inventory import Location as LocationModel
from app.models.product import Product as ProductModel
from app.models.stock import Stock as StockModel
from app.tasks.inventory_tasks import check_low_stock


def get_stock_or_404(
    session: Session, inventory_id: int, stock_id: int
) -> StockModel:
    stock = session.get(StockModel, stock_id)
    if stock is None or stock.inventory_id != inventory_id:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


def list_stock(session: Session, inventory_id: int) -> list[StockRead]:
    rows = (
        session.query(StockModel, ProductModel, LocationModel)
        .join(ProductModel, StockModel.product_id == ProductModel.product_id)
        .join(LocationModel, StockModel.location_id == LocationModel.location_id)
        .filter(StockModel.inventory_id == inventory_id)
        .order_by(StockModel.stock_id)
        .all()
    )
    results: list[StockRead] = []
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


def add_stock(
    session: Session, inventory_id: int, payload: StockCreate
) -> StockRead:
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
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stock entry already exists for this product and location",
        ) from exc
    session.refresh(stock)

    # Trigger async low stock check
    check_low_stock.delay(stock.product_id)

    return StockRead(
        stock_id=stock.stock_id,
        product_id=stock.product_id,
        product_name=product.name,
        location_id=stock.location_id,
        location_address=location.address,
        quantity=stock.quantity,
    )


def update_stock(
    session: Session, stock: StockModel, payload: StockUpdate
) -> StockRead:
    stock.quantity = payload.quantity
    session.commit()
    session.refresh(stock)

    # Trigger async low stock check
    check_low_stock.delay(stock.product_id)

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


def delete_stock(session: Session, stock: StockModel) -> None:
    session.delete(stock)
    session.commit()

