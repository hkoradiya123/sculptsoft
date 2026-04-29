import mysql.connector
from mysql.connector import Error
import os
import dotenv

# dotenv.load_dotenv()


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
            print(f"Error: {err}")
            return None

    def commit(self):
        self.connection.commit()
    
    def rollback(self):
        self.connection.rollback()
    
    def close(self):
        self.cursor.close()
        self.connection.close()
        
if __name__ == "__main__":
    db_helper = DBHelper()
    result = db_helper.execute_query("SELECT * FROM product")  
    print(result)
