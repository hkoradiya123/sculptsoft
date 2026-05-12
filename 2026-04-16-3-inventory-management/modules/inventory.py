
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
import psycopg2
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
        self.id = None
        self.name = name
        self.area = area
        self.city = city
    



    # CREATE TABLE location (
    #     location_id SERIAL PRIMARY KEY,
    #     address VARCHAR(150),
    #     parent_id INT NULL,
    #     FOREIGN KEY (parent_id) REFERENCES location(location_id)
    # );
    
    def create_inventory(self, name, area, city):
        try:
            inventory_id = db.execute_query(
                """
                INSERT INTO inventory (name, area, city) 
                VALUES (%s, %s, %s)
                returning inventory_id
                """,
                (name, area, city)
            )
        
            self.id = inventory_id[0][0] if inventory_id else None
            db.commit()
            print(f"Inventory '{name}' has been created in {area}, {city}.")
        except Exception as e:
            print(f"Error occurred while creating inventory: {e}")
    
    
    def create_inventory_location(self, address):
        try:
            
            db.execute_query(
                """
                INSERT INTO location (inventory_id, address) 
                VALUES (%s, %s)
                """,
                (self.id, address))               
            print(f"Location '{address}' has been created.")
        except Error as e:
            print(f"Error occurred while creating location: {e}")
        
    def get_location(self, address_id):
        try:
            result = db.execute_query(
                """
                SELECT address FROM location WHERE address_id = %s and inventory_id = %s
                """,
                (address_id, self.id)
            )
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
            results = db.execute_query(
                """
                SELECT location_id, address FROM location WHERE inventory_id = %s
                """,
                (self.id,)
            )
            return results if results != "No results found." else []
        except Exception as e:
            print(f"Error occurred while fetching locations: {e}")
            return []  
        

    def update_location(self, address_id, new_address):
        try:
            db.execute_query(
                """
                UPDATE location SET address = %s WHERE address_id = %s and inventory_id = %s
                """,
                (new_address, address_id, self.id)
            )
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

    def add_product(self, product_id , quantity,location_id):
        if quantity < 0:
            raise InvalidQuantityError(product.quantity)
        if location_id not in [loc[0] for loc in self.get_all_locations()]:
            print("Invalid location ID.")
            return
        if product_id not in Product.get_all_product_ids():
            print("Product not found in product database. Please create it first.")
            return
        try:
            db.execute_query(
                """
                INSERT INTO stock (product_id, quantity, inventory_id, location_id) VALUES (%s, %s, %s, %s)
                """,
                (product_id, quantity, self.id, location_id)
            )
        except Error as e:
            print(f"Error occurred while adding product: {e}")

        print(f"Product added to the inventory")
        
    def update_quantity(self, product_id, quantity):
        if quantity < 0:
            raise InvalidQuantityError(quantity)
        try:
            db.execute_query(
                """
                UPDATE stock SET quantity = %s WHERE product_id = %s AND inventory_id = %s
                """,
                (quantity, product_id, self.id)
            )       
                
            print(f"Product with ID {product_id} has been updated with new quantity.")
        except Error as e:
            print(f"Error occurred while updating product quantity: {e}")
       


    def get_product_details(self, product_id):
        try:
            result = db.execute_query(
                """
                SELECT * FROM product join stock ON product.id = stock.product_id WHERE product.id = %s AND stock.inventory_id = %s
                """,
                (product_id, self.id)
            )
            if result:
                return Product(**result[0])
        except Error as e:
            print(f"Error occurred while fetching product: {e}")
        raise ProductNotFoundError(product_id)

    def display_all_products(self):
        try:
            results = db.execute_query(
                """
                SELECT p.product_id, p.name, p.price, s.quantity 
                FROM product p 
                JOIN stock s ON p.product_id = s.product_id 
                WHERE s.inventory_id = %s
                """,
                (self.id,)
            )

            if not results or results == "No results found.":
                print(f"No products found in the {self.name} inventory.")
                return

            print(f"\n--- Products in {self.name} ({self.area}) ---")
            print()
            for row in results:
                p_id, p_name, p_price, p_qty = row                
                print(f"ID: {p_id:<4} | Name: {p_name:<20} | Price: ₹{p_price:>8} | Qty: {p_qty}")
            print()
        except Exception as e:
            print(f"Error occurred while displaying products: {e}")


    #! Additional Features (Optional)

    # * Low stock check

    def low_stock_check(self, threshold):
        low_stock_products = []
        try:
            results = db.execute_query(
                """
                SELECT * FROM product join stock ON product.id = stock.product_id WHERE stock.quantity < %s AND stock.inventory_id = %s
                """,
                (threshold, self.id)
            )
            if results == "No results found.":
                print("No products found with low stock.")
                return []
            for row in results:
                low_stock_products.append(Product(**row))
        except Exception as e:
            print(f"Error occurred while checking low stock: {e}")
        return low_stock_products

    # * Search by name
    def search_name(self, name):
        results = []
        try:
            query = """
                SELECT * FROM product join stock ON product.id = stock.product_id WHERE product.name LIKE %s AND stock.inventory_id = %s
            """
            db_results = db.execute_query(query, (f"%{name}%", self.id))
            for row in db_results:
                results.append(Product(**row))
        except Exception as e:
            print(f"Error occurred while searching products: {e}")
        return results

    # * Total inventory value
    def total_value(self):
        total = 0
        try:
            results = db.execute_query(
                """
                SELECT price, quantity FROM product join stock ON product.id = stock.product_id where stock.inventory_id = %s
                """,
                (self.id,)
            )
            for price, quantity in results:
                total += price * quantity
        except Exception as e:
            print(f"Error occurred while calculating total inventory value: {e}")
        return total
    
    def get_inventory_value(self):
        try:
            self.cursor.execute(
                """
                SELECT SUM(price * quantity) FROM product join stock ON product.id = stock.product_id WHERE stock.inventory_id = %s
                """,
                (self.id,)
            )
            result = self.cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except psycopg2.Error as err:
            db.rollback()
            print(f"Error: {err}")
            return None
    def update_product(self, product_id=None, name=None, price=None , quantity=None):
        if not Product.check_product_exists(product_id):
            print(f"Product with ID {product_id} does not exist.")
            return
        try:
            if product_id not in self.get_all_product_ids():
                print(f"Product with ID {product_id} is not in the inventory. Please add it first.")
                return
            if quantity is not None:
                db.execute_query(
                    """
                    UPDATE stock SET quantity = %s WHERE product_id = %s AND inventory_id = %s
                    """,
                    (quantity, product_id, self.id)
                )
            Product.update_product(product_id=product_id, name=name, price=price)
        except Exception as e:
            print(f"Error occurred while updating product: {e}")
            
    def get_all_product_ids(self):
        try:
            results = db.execute_query(
                """
                SELECT product_id FROM stock WHERE inventory_id = %s
                """,
                (self.id,)
            )
            return [row[0] for row in results] if results != "No results found." else []
        except Exception as e:
            print(f"Error occurred while fetching product IDs: {e}")
            return []       

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

class Location:
    def __init__(self, id, address):
        self.id = id
        self.address = address
        
    @staticmethod
    def create_location(inventory_id, address):
        try:
            db.execute_query(
                """
                INSERT INTO location (inventory_id, address) 
                VALUES (%s, %s)
                """,
                (inventory_id, address))               
            print(f"Location '{address}' has been created.")
        except Error as e:
            print(f"Error occurred while creating location: {e}")