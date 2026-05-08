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
    def __init__(self, name, price, id=None):
        self.id = id
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

    def update_product(self, product_id: int, name=None , price=None):
        if name is None and price is None:
            print("No updates provided.")
            return
        if price is not None and price < 0:
            print("Price cannot be negative.")
            return
        if name is not None and name.strip() == "":
            print("Product name cannot be empty.")
            return
        try:
            if name is not None:
                db.execute_query("UPDATE product SET name = %s WHERE product_id = %s",
                                (name, product_id))
            if price is not None:
                db.execute_query("UPDATE product SET price = %s WHERE product_id = %s",
                                (price, product_id))
            db.commit()
            print(f"Product with ID {product_id} has been updated.")
        except Error as e:
            db.rollback()
            print(f"Error occurred while updating product: {e}")


    def display_details(self, id):
        result = db.execute_query("SELECT * FROM product WHERE product_id = %s", (id))
        if result != "No results found.":
            product = result[0]
            print(
                f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}"
            )
        else:
            print("Product not found.")
            
    def check_product_exists(product_id):
        result = db.execute_query("SELECT product_id FROM product WHERE product_id = %s", (product_id,))
        return True if result and result != "No results found." else False
    
    def get_products(self):
        try:
            db.execute("SELECT * FROM product")
            result = db.fetchall()
            return result if result != [] else "No products found."
        except psycopg2.Error as err:
            db.rollback()
            print(f"Error: {err}")
            return None
        
    def  remove_product(product_id):
        try:
            if not Product.check_product_exists(product_id):
                print(f"Product with ID {product_id} does not exist.")
                return
            db.execute_query("DELETE FROM product WHERE product_id = %s", (product_id,))
            db.commit()
            print(f"Product with ID {product_id} has been removed.")
        except Error as e:
            db.rollback()
            print(f"Error occurred while removing product: {e}")
