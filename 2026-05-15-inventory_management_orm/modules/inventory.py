from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from database.dbhelper import db
from database.model.inventory import Inventory as InventoryModel
from database.model.inventory import Location as LocationModel
from database.model.product import Product as ProductModel
from database.model.stock import Stock as StockModel
from modules.exceptions import InvalidQuantityError, ProductNotFoundError
from modules.product import Product


class Inventory:
    def __init__(self, name, area, city, id=None):
        self.id = id
        self.name = name
        self.area = area
        self.city = city

    @classmethod
    def create_inventory(cls, name, area, city):
        with db.get_session() as session:
            inventory = InventoryModel(name=name, area=area, city=city)
            session.add(inventory)
            session.commit()
            session.refresh(inventory)

            print(f"Inventory '{name}' has been created in {area}, {city}.")
            return cls(
                id=inventory.inventory_id,
                name=inventory.name,
                area=inventory.area,
                city=inventory.city,
            )

    @staticmethod
    def get_all_inventories():
        with db.get_session() as session:
            inventories = (
                session.query(InventoryModel)
                .order_by(InventoryModel.inventory_id)
                .all()
            )
            return [
                {
                    "id": inv.inventory_id,
                    "name": inv.name,
                    "area": inv.area,
                    "city": inv.city,
                }
                for inv in inventories
            ]

    def create_inventory_location(self, address):
        with db.get_session() as session:
            location = LocationModel(inventory_id=self.id, address=address)
            session.add(location)
            session.commit()
            print(f"Location '{address}' has been created.")

    def get_location(self, address_id):
        with db.get_session() as session:
            location = (
                session.query(LocationModel)
                .filter(
                    LocationModel.location_id == address_id,
                    LocationModel.inventory_id == self.id,
                )
                .first()
            )
            if location is None:
                print(f"Location '{address_id}' not found.")
                return None
            return location.address

    def get_all_locations(self):
        with db.get_session() as session:
            locations = (
                session.query(LocationModel)
                .filter(LocationModel.inventory_id == self.id)
                .order_by(LocationModel.location_id)
                .all()
            )
            return [(loc.location_id, loc.address) for loc in locations]

    def update_location(self, address_id, new_address):
        with db.get_session() as session:
            location = (
                session.query(LocationModel)
                .filter(
                    LocationModel.location_id == address_id,
                    LocationModel.inventory_id == self.id,
                )
                .first()
            )
            if location is None:
                print(f"Location with ID {address_id} not found.")
                return

            location.address = new_address
            session.commit()
            print(f"Location with ID {address_id} has been updated.")

    def add_product(self, product_id, quantity, location_id):
        if quantity < 0:
            raise InvalidQuantityError(quantity)

        with db.get_session() as session:
            product = session.get(ProductModel, product_id)
            if product is None:
                print("Product not found in product database. Please create it first.")
                return

            location = (
                session.query(LocationModel)
                .filter(
                    LocationModel.location_id == location_id,
                    LocationModel.inventory_id == self.id,
                )
                .first()
            )
            if location is None:
                print("Invalid location ID.")
                return

            stock = StockModel(
                product_id=product_id,
                quantity=quantity,
                inventory_id=self.id,
                location_id=location_id,
            )
            session.add(stock)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                print("Product already exists in this inventory location. Use update to change quantity.")
                return

            print("Product added to the inventory")

    def update_quantity(self, product_id, quantity):
        if quantity < 0:
            raise InvalidQuantityError(quantity)

        with db.get_session() as session:
            stocks = (
                session.query(StockModel)
                .filter(
                    StockModel.product_id == product_id,
                    StockModel.inventory_id == self.id,
                )
                .all()
            )
            if not stocks:
                raise ProductNotFoundError(product_id)

            for stock in stocks:
                stock.quantity = quantity
            session.commit()
            print(f"Product with ID {product_id} has been updated with new quantity.")

    def remove_product(self, product_id):
        with db.get_session() as session:
            deleted = (
                session.query(StockModel)
                .filter(
                    StockModel.product_id == product_id,
                    StockModel.inventory_id == self.id,
                )
                .delete(synchronize_session=False)
            )
            session.commit()

            if deleted:
                print(f"Product with ID {product_id} has been removed from this inventory.")
            else:
                print(f"Product with ID {product_id} is not in this inventory.")

    def get_product_details(self, product_id):
        with db.get_session() as session:
            product = (
                session.query(ProductModel)
                .join(StockModel, ProductModel.product_id == StockModel.product_id)
                .filter(
                    ProductModel.product_id == product_id,
                    StockModel.inventory_id == self.id,
                )
                .first()
            )
            if product is None:
                raise ProductNotFoundError(product_id)
            return Product._from_model(product)

    def display_all_products(self):
        with db.get_session() as session:
            rows = (
                session.query(
                    ProductModel.product_id,
                    ProductModel.name,
                    ProductModel.price,
                    func.sum(StockModel.quantity).label("quantity"),
                )
                .join(StockModel, ProductModel.product_id == StockModel.product_id)
                .filter(StockModel.inventory_id == self.id)
                .group_by(ProductModel.product_id, ProductModel.name, ProductModel.price)
                .order_by(ProductModel.product_id)
                .all()
            )

        if not rows:
            print(f"No products found in the {self.name} inventory.")
            return

        print(f"\n--- Products in {self.name} ({self.area}) ---\n")
        for product_id, name, price, quantity in rows:
            print(f"ID: {product_id:<4} | Name: {name:<20} | Price: Rs.{price:>8} | Qty: {quantity}")
        print()

    def low_stock_check(self, threshold):
        with db.get_session() as session:
            rows = (
                session.query(ProductModel)
                .join(StockModel, ProductModel.product_id == StockModel.product_id)
                .filter(
                    StockModel.quantity < threshold,
                    StockModel.inventory_id == self.id,
                )
                .all()
            )
            return [Product._from_model(product) for product in rows]

    def search_name(self, name):
        with db.get_session() as session:
            rows = (
                session.query(ProductModel)
                .join(StockModel, ProductModel.product_id == StockModel.product_id)
                .filter(
                    ProductModel.name.ilike(f"%{name}%"),
                    StockModel.inventory_id == self.id,
                )
                .all()
            )
            return [Product._from_model(product) for product in rows]

    def total_value(self):
        with db.get_session() as session:
            value = (
                session.query(func.sum(ProductModel.price * StockModel.quantity))
                .join(StockModel, ProductModel.product_id == StockModel.product_id)
                .filter(StockModel.inventory_id == self.id)
                .scalar()
            )
            return value or 0

    def get_inventory_value(self):
        return self.total_value()

    def update_product(self, product_id=None, name=None, price=None, quantity=None):
        if not Product.check_product_exists(product_id):
            print(f"Product with ID {product_id} does not exist.")
            return
        if product_id not in self.get_all_product_ids():
            print(f"Product with ID {product_id} is not in the inventory. Please add it first.")
            return

        if quantity is not None:
            self.update_quantity(product_id, quantity)
        Product.update_product(product_id=product_id, name=name, price=price)

    def get_all_product_ids(self):
        with db.get_session() as session:
            rows = (
                session.query(StockModel.product_id)
                .filter(StockModel.inventory_id == self.id)
                .distinct()
                .all()
            )
            return [row[0] for row in rows]


class Location:
    def __init__(self, id, address):
        self.id = id
        self.address = address

    @staticmethod
    def create_location(inventory_id, address):
        with db.get_session() as session:
            location = LocationModel(inventory_id=inventory_id, address=address)
            session.add(location)
            session.commit()
            print(f"Location '{address}' has been created.")
