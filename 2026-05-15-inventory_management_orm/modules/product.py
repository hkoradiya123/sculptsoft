from database.dbhelper import db
from database.model.product import Product as ProductModel
from modules.exceptions import InvalidPriceError


class Product:
    def __init__(self, name, price, id=None):
        self.id = id
        self.name = name
        self.price = price

    @staticmethod
    def _from_model(product):
        if product is None:
            return None
        return Product(
            id=product.product_id,
            name=product.name,
            price=float(product.price),
        )

    @staticmethod
    def new_product(name, price):
        if price <= 0:
            raise InvalidPriceError(price)

        with db.get_session() as session:
            product = ProductModel(name=name, price=price)
            session.add(product)
            session.commit()
            session.refresh(product)
            print(f"Product '{name}' has been added with price {price}.")
            return product.product_id

    @staticmethod
    def update_product(product_id: int, name=None, price=None):
        if name is None and price is None:
            print("No updates provided.")
            return
        if price is not None and price <= 0:
            raise InvalidPriceError(price)
        if name is not None and name.strip() == "":
            print("Product name cannot be empty.")
            return

        with db.get_session() as session:
            product = session.get(ProductModel, product_id)
            if product is None:
                print(f"Product with ID {product_id} does not exist.")
                return

            if name is not None:
                product.name = name
            if price is not None:
                product.price = price

            session.commit()
            print(f"Product with ID {product_id} has been updated.")

    @staticmethod
    def display_details(product_id):
        product = Product.search_product_by_id(product_id)
        if product:
            print(f"ID: {product.id}, Name: {product.name}, Price: {product.price}")
        else:
            print("Product not found.")

    @staticmethod
    def check_product_exists(product_id):
        with db.get_session() as session:
            return session.get(ProductModel, product_id) is not None

    @staticmethod
    def get_products():
        with db.get_session() as session:
            products = session.query(ProductModel).order_by(ProductModel.product_id).all()
            if not products:
                return "No products found."
            return [(p.product_id, p.name, p.price) for p in products]

    @staticmethod
    def remove_product(product_id):
        with db.get_session() as session:
            product = session.get(ProductModel, product_id)
            if product is None:
                print(f"Product with ID {product_id} does not exist.")
                return

            session.delete(product)
            session.commit()
            print(f"Product with ID {product_id} has been removed.")

    @staticmethod
    def search_product(name):
        with db.get_session() as session:
            products = (
                session.query(ProductModel)
                .filter(ProductModel.name.ilike(f"%{name}%"))
                .order_by(ProductModel.product_id)
                .all()
            )
            return [(p.product_id, p.name, p.price) for p in products]

    @staticmethod
    def search_product_by_id(product_id):
        with db.get_session() as session:
            product = session.get(ProductModel, product_id)
            return Product._from_model(product)

    @staticmethod
    def get_all_product_ids():
        with db.get_session() as session:
            rows = session.query(ProductModel.product_id).all()
            return [row[0] for row in rows]

    @staticmethod
    def display_all_products():
        products = Product.get_products()
        if products == "No products found.":
            print("No products found.")
            return

        print("Products:")
        for product_id, name, price in products:
            print(f"ID: {product_id}, Name: {name}, Price: {price}")
