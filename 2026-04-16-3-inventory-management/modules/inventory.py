
import json
import os
from modules.product import Product
from modules.exceptions import (
    DuplicateProductError,
    InvalidPriceError,
    InvalidQuantityError,
    ProductNotFoundError,
    InsufficientStockError
)
import mysql.connector
from mysql.connector import Error
import dotenv

dotenv.load_dotenv()

from modules.dbhelper import DBHelper

db = DBHelper(
    host=os.getenv("host"),
    user=os.getenv("user"),
    password=os.getenv("password"),
    database=os.getenv("database")
)


#! Inventory Class

#! Attributes:
# collection of products

#! Methods:
# add_product(product)
# remove_product(product_id)
# update_product(product_id, data)
# get_product(product_id)
# display_all_products()
# Additional Features (Optional)
# Low stock check
# Search by name
# Total inventory value
# Save/load data

class Inventory():
    id_count = 1
    def __init__(self,name, area , city):
        self.name = name
        self.area = area
        self.city = city

    def add_product(self, product , quantity):
        if product.price <= 0:
            raise InvalidPriceError(product.price)
        if product.quantity < 0:
            raise InvalidQuantityError(product.quantity)

        try:
            db.execute_query("""INSERT INTO inventory (name, price, quantity) VALUES (%s, %s, %s)""",
                            (product.name, product.price, quantity))
        except Error as e:
            print(f"Error occurred while adding product: {e}")

        print(f"{product.name} is added to the inventory")
        

    def remove_product(self, product_id):
        try:
            db.execute_query("DELETE FROM product WHERE id = %s", (product_id,))
        except Error as e:
            print(f"Error occurred while removing product: {e}")
        print(f"Product with ID {product_id} has been removed.")

    def update_product(self, product_id, name=None, price=None, quantity=None):
        if price is not None and price <= 0:
            raise InvalidPriceError(price)
        if quantity is not None and quantity < 0:
            raise InvalidQuantityError(quantity)

        try:
            db.execute_query("UPDATE product SET name = %s, price = %s, quantity = %s WHERE id = %s",
                            (name, price, quantity, product_id))
        except Error as e:
            print(f"Error occurred while updating product: {e}")
        print(f"Product with ID {product_id} has been updated.")

    def get_product(self, product_id):
        try:
            result = db.execute_query("SELECT * FROM product WHERE id = %s", (product_id,))
            if result:
                return Product(**result[0])
        except Error as e:
            print(f"Error occurred while fetching product: {e}")
        raise ProductNotFoundError(product_id)

    def display_all_products(self):
        try:
            results = db.execute_query("SELECT * FROM product")
            for row in results:
                product = Product(**row)
                product.display_details()
        except Error as e:
            print(f"Error occurred while displaying products: {e}")

    #! Additional Features (Optional)

    # * Low stock check

    def low_stock_check(self, threshold):
        low_stock_products = []
        try:
            results = db.execute_query("SELECT * FROM product WHERE quantity < %s", (threshold,))
            for row in results:
                low_stock_products.append(Product(**row))
        except Error as e:
            print(f"Error occurred while checking low stock: {e}")
        return low_stock_products

    # * Search by name
    def search_name(self, name):
        results = []
        try:
            query = "SELECT * FROM product WHERE name LIKE %s"
            db_results = db.execute_query(query, (f"%{name}%",))
            for row in db_results:
                results.append(Product(**row))
        except Error as e:
            print(f"Error occurred while searching products: {e}")
        return results

    # * Total inventory value
    def total_value(self):
        total = 0
        try:
            results = db.execute_query("SELECT price, quantity FROM product")
            for price, quantity in results:
                total += price * quantity
        except Error as e:
            print(f"Error occurred while calculating total inventory value: {e}")
        return total

    # # * Save/load data
    # def save_data(self):
    #     with open(self.filepath, "w") as f:
    #         products_data = []
    #         for i in self.collection:
    #             products_data.append({
    #                 "id": i.id,
    #                 "name": i.name,
    #                 "price": i.price,
    #                 "quantity": i.quantity
    #             })
    #         json.dump(products_data, f, indent=2)

    # def load_data(self):
    #     # No data file yet: start with an empty inventory.
    #     if not os.path.exists(self.filepath):
    #         return

    #     try:
    #         with open(self.filepath, "r") as f:
    #             data = json.load(f)
    #     except:
    #         print(f"empty json file {self.filepath}. Starting with empty inventory.")
    #         return
    #     max_id = 0
    #     for item in data:
    #         product = Product(
    #             name=item["name"],
    #             price=item["price"],
    #             quantity=item["quantity"],
    #             product_id=item["id"]
    #         )
    #         self.collection.append(product)
    #         if product.id > max_id:
    #             max_id = product.id
    #     if max_id >= Product.id_counter:
    #         Product.id_counter = max_id + 1
