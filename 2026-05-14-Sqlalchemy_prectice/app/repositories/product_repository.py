from sqlalchemy.orm import Session

from app.models.product_model import Product
from app.schemas.product_schema import ProductCreate


def create_product(db: Session, product_data: ProductCreate) -> Product:
    product = Product(**product_data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_products(db: Session) -> list[Product]:
    return db.query(Product).all()


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()
