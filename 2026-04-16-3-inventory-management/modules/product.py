import mysql.connector
from mysql.connector import Error
from modules.dbhelper import DBHelper,db
from modules.exceptions import *
# import dotenv
import os
import dotenv
from datetime import datetime

dotenv.load_dotenv()


class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def new_product(self, name, price):
        try:
            if price <= 0:
                raise InvalidPriceError(price)
            db.execute_query("""INSERT INTO product 
                             (name, price) 
                             VALUES (%s, %s)
                             """,(name, price))
            db.commit()
            print(f"Product '{name}' has been added with price {price}.")
        except Error as e:
            print(f"Error occurred while adding product: {e}")

    def update_product_name(self, product_id, name=None):
        try:

            if name is not None:
                db.execute_query("UPDATE product SET name = %s WHERE id = %s",
                                (name, product_id))
                print(f"Product with ID {product_id} has been updated.")
        except Error as e:
            print(f"Error occurred while updating product: {e}")

    def update_product_price(self, product_id, new_price):
        if new_price < 0:
            print("Price cannot be negative.")
        else:
            try:
                db.execute_query("""
                    UPDATE product 
                    SET price = %s 
                    WHERE product_id = %s
                """, (new_price, product_id))
                db.commit()

            except Error as e:
                db.rollback()
                print(f"Error occurred while updating price: {e}")


    def display_details(id):
        result = db.execute_query("SELECT * FROM product WHERE product_id = %s", (id,))
        if result != "No results found.":
            product = result[0]
            print(
                f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}"
            )
        else:
            print("Product not found.")
    
    def get_products(self):
        try:
            db.execute("SELECT * FROM product")
            result = db.fetchall()
            return result if result != [] else "No products found."
        except psycopg2.Error as err:
            db.rollback()
            print(f"Error: {err}")
            return None
