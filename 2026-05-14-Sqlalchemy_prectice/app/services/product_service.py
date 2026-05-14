from sqlalchemy.orm import Session

from app.repositories import product_repository
from app.schemas.product_schema import ProductCreate


def create_product(db: Session, product_data: ProductCreate):
    return product_repository.create_product(db, product_data)


def list_products(db: Session):
    return product_repository.get_products(db)


def get_product(db: Session, product_id: int):
    return product_repository.get_product_by_id(db, product_id)
