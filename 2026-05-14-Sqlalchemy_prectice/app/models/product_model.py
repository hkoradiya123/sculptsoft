from sqlalchemy import Column, Float, Integer, String, Text

from app.config.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
