import mysql.connector
from mysql.connector import Error
import os
import dotenv

dotenv.load_dotenv()

class DBHelper:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        self.cursor = self.connection.cursor()
    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            return result if result != [] else "No results found."
        
        except mysql.connector.Error as err:
            self.rollback()
            print(f"Error: {err}")
            return None

    def commit(self):
        self.connection.commit()
    
    def rollback(self):
        self.connection.rollback()
    
    def close(self):
        self.cursor.close()
        self.connection.close()
        
    def get_inventory_value(self):
        try:
            self.cursor.execute("SELECT SUM(price * quantity) FROM inventory")
            result = self.cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except mysql.connector.Error as err:
            self.rollback()
            print(f"Error: {err}")
            return None
        
    def get_products(self):
        try:
            self.cursor.execute("SELECT * FROM product")
            result = self.cursor.fetchall()
            return result if result != [] else "No products found."
        except mysql.connector.Error as err:
            self.rollback()
            print(f"Error: {err}")
            return None
        

        
if __name__ == "__main__":
    db_helper = DBHelper()
    result = db_helper.get_products()
    print(result)
