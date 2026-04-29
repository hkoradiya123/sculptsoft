import mysql.connector
from mysql.connector import Error
from dbhelper import DBHelper
from exceptions import (
    DuplicateProductError,
    InvalidPriceError,
    InvalidQuantityError,
    ProductNotFoundError,
    InsufficientStockError
)
# import dotenv
import os
import dotenv
from datetime import datetime

dotenv.load_dotenv()

try:
    db = DBHelper()
    print("Database connection successful.")
except Error as e:
    print(f"Error occurred while connecting to the database: {e}")

class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def new_product(self, name, price, quantity):
        try:
            if price <= 0:
                raise InvalidPriceError(price)
            if quantity < 0:
                raise InvalidQuantityError(quantity)
            db.execute_query("""INSERT INTO product 
                             (name, price) 
                             VALUES (%s, %s)
                             """,(name, price))
            
            db.execute_query("""
                             insert into price_history 
                             (product_id, price) 
                             values (LAST_INSERT_ID(), %s)
                             """, (price))
        except Error as e:
            print(f"Error occurred while adding product: {e}")

    def update_price(self, new_price):
        if new_price < 0:
            print("Price cannot be negative.")
        else:
            try:
                db.execute_query("""
                    UPDATE product 
                    SET price = %s 
                    WHERE product_id = %s
                """, (new_price, self.id))
                db.commit()

            except Error as e:
                db.rollback()
                print(f"Error occurred while updating price: {e}")


    def display_details(id):
        result = db.execute_query("SELECT * FROM product WHERE product_id = %s", (id,))
        if result != "No results found.":
            product = result[0]
            print(
                f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Quantity: {product[3]}"
            )
        else:
            print("Product not found.")
