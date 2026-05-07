
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


from modules.dbhelper import DBHelper,db


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
    def __init__(self,name, area , city):
        self.name = name
        self.area = area
        self.city = city
        try:
            db.execute_query("""INSERT INTO inventory (name, area, city) VALUES (%s, %s, %s)""",
                            (self.name, self.area, self.city))
        except Error as e:
            print(f"Error occurred while creating inventory: {e}")
        self.id = db.execute_query("SELECT LAST_INSERT_ID()")[0][0]


    # CREATE TABLE location (
    #     location_id SERIAL PRIMARY KEY,
    #     address VARCHAR(150),
    #     parent_id INT NULL,
    #     FOREIGN KEY (parent_id) REFERENCES location(location_id)
    # );
    
    def create_inventory_location(self, address):
        try:
            
            db.execute_query("""INSERT INTO location (inventory_id, address) VALUES (%s, %s)""",
                            (self.id, address))               
            print(f"Location '{address}' has been created.")
        except Error as e:
            print(f"Error occurred while creating location: {e}")
        
    def get_location(self, address_id):
        try:
            result = db.execute_query("SELECT address FROM location WHERE address_id = %s and inventory_id = %s" , (address_id, self.id))
            if result:
                return result[0][0]
            else:
                print(f"Location '{address_id}' not found.")    
                return None
        except Error as e:
            print(f"Error occurred while fetching location ID: {e}")
            return None   
        
    def get_all_locations(self):
        try:
            results = db.execute_query("SELECT address_id, address FROM location WHERE inventory_id = %s", (self.id,))
            return results if results != "No results found." else []
        except Error as e:
            print(f"Error occurred while fetching locations: {e}")
            return []  
        

    def update_location(self, address_id, new_address):
        try:
            db.execute_query("UPDATE location SET address = %s WHERE address_id = %s and inventory_id = %s",
                            (new_address, address_id, self.id))
            print(f"Location with ID {address_id} has been updated.")
        except Error as e:
            print(f"Error occurred while updating location: {e}")
            
    
    #     CREATE TABLE stock (
    #     stock_id SERIAL PRIMARY KEY,
    #     product_id INT,
    #     inventory_id INT,
    #     location_id INT,
    #     quantity INT,
    #     FOREIGN KEY (product_id) REFERENCES product(product_id),
    #     FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    #     FOREIGN KEY (location_id) REFERENCES location(location_id),
    #     UNIQUE (product_id, inventory_id, location_id)
    # );

    def add_product(self, product , quantity,location):
        if product.price <= 0:
            raise InvalidPriceError(product.price)
        if product.quantity < 0:
            raise InvalidQuantityError(product.quantity)

        try:
            db.execute_query("""INSERT INTO stock (product_id, quantity, inventory_id, location_id) VALUES (%s, %s, %s, %s)""",
                            (product.id, quantity, self.id, location.id))
        except Error as e:
            print(f"Error occurred while adding product: {e}")

        print(f"{product.name} is added to the inventory")
        
    def update_quantity(self, product_id, quantity):
        if quantity < 0:
            raise InvalidQuantityError(quantity)
        try:
            db.execute_query("UPDATE stock SET quantity = %s WHERE product_id = %s AND inventory_id = %s",
                            (quantity, product_id, self.id))
            print(f"Product with ID {product_id} has been updated with new quantity.")
        except Error as e:
            print(f"Error occurred while updating product quantity: {e}")
       


    def get_product_details(self, product_id):
        try:
            result = db.execute_query("SELECT * FROM product join stock ON product.id = stock.product_id WHERE product.id = %s AND stock.inventory_id = %s", (product_id, self.id))
            if result:
                return Product(**result[0])
        except Error as e:
            print(f"Error occurred while fetching product: {e}")
        raise ProductNotFoundError(product_id)

    def display_all_products(self):
        try:
            results = db.execute_query("SELECT * FROM product join stock ON product.id = stock.product_id WHERE stock.inventory_id = %s", (self.id,))
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
            results = db.execute_query("SELECT * FROM product join stock ON product.id = stock.product_id WHERE stock.quantity < %s AND stock.inventory_id = %s", (threshold, self.id))
            for row in results:
                low_stock_products.append(Product(**row))
        except Error as e:
            print(f"Error occurred while checking low stock: {e}")
        return low_stock_products

    # * Search by name
    def search_name(self, name):
        results = []
        try:
            query = "SELECT * FROM product join stock ON product.id = stock.product_id WHERE product.name LIKE %s AND stock.inventory_id = %s"
            db_results = db.execute_query(query, (f"%{name}%", self.id))
            for row in db_results:
                results.append(Product(**row))
        except Error as e:
            print(f"Error occurred while searching products: {e}")
        return results

    # * Total inventory value
    def total_value(self):
        total = 0
        try:
            results = db.execute_query("SELECT price, quantity FROM product join stock ON product.id = stock.product_id where stock.inventory_id = %s", (self.id,))
            for price, quantity in results:
                total += price * quantity
        except Error as e:
            print(f"Error occurred while calculating total inventory value: {e}")
        return total
    
    def get_inventory_value(self):
        try:
            self.cursor.execute("SELECT SUM(price * quantity) FROM product join stock ON product.id = stock.product_id WHERE stock.inventory_id = %s", (self.id))
            result = self.cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except psycopg2.Error as err:
            self.rollback()
            print(f"Error: {err}")
            return None
            

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
