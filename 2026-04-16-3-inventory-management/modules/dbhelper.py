import psycopg2
from psycopg2 import Error
import os
import dotenv

dotenv.load_dotenv()




class DBHelper:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        self.cursor = self.connection.cursor()
    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            # Only fetch if it's a SELECT statement
            if query.strip().upper().startswith("SELECT"):
                result = self.cursor.fetchall()
                return result if result else "No results found."
            
            # For INSERT/UPDATE/DELETE, return success message
            return "Query executed successfully."
            
        except Error as err:
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
        
db = DBHelper()

        

        
if __name__ == "__main__":
    db_helper = DBHelper()
    result = db_helper.get_products()
    print(result)
