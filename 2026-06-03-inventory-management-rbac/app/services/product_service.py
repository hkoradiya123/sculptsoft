from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas import ProductCreate, ProductUpdate
from app.models.product import Product as ProductModel


def get_product_or_404(session: Session, product_id: int) -> ProductModel:
    product = session.get(ProductModel, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def list_products(session: Session) -> list[ProductModel]:
    return session.query(ProductModel).order_by(ProductModel.product_id).all()


def create_product(session: Session, payload: ProductCreate) -> ProductModel:
    product = ProductModel(**payload.dict())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def update_product(
    session: Session, product: ProductModel, payload: ProductUpdate
) -> ProductModel:
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(product, key, value)
    session.commit()
    session.refresh(product)
    return product


def delete_product(session: Session, product: ProductModel) -> None:
    session.delete(product)
    session.commit()

