from modules import *
import os
import dotenv

dotenv.load_dotenv()

def print_wait(function):
    def inner(*args, **kwargs):
        os.system("cls" if os.name == "nt" else "clear")
        function(*args, **kwargs)
        print("-" * 40)
        input("Press Enter to continue...")
    return inner

def read_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def read_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")


@print_wait
def add_product():
    name = input("Enter product name: ")
    price = read_float("Enter product price: ")
    quantity = read_int("Enter product quantity: ")
    product = Product(name, price, quantity)
    try:
        myinventory.add_product(product)

    except ValueError as e:
        print(f"Error adding product: {e}")

@print_wait
def remove_product():
    myinventory.display_all_products()
    print("-" * 40)
    try:
        product_id = read_int("Enter product ID to remove: ")
        myinventory.remove_product(product_id)
        print(f"Product with ID {product_id} has been removed.")
    except ValueError as e:
        print(f"Error removing product: {e}")   

@print_wait
def update_product():
    product_id = read_int("Enter product ID to update: ")
    try:
        product = myinventory.get_product(product_id)
    except ValueError as e:
        print(f"Error updating product: {e}")
        return
    
    name = input("Enter new name (leave blank to keep current): ")
    
    if name == "":
        name = None
        

    price = None
    quantity = None
    price_input = input("Enter new price (leave blank to keep current): ")
    quantity_input = input("Enter new quantity (leave blank to keep current): ")
    
    if price_input:
        try:
            price = float(price_input)
            quantity = int(quantity_input)
        except ValueError:
            print("Invalid input for price or quantity. Keeping current values.")
    
    try:
        myinventory.update_product(product_id, name=name or None, price=price, quantity=quantity)
        print(f"Product with ID {product_id} has been updated.")
    except ValueError as e:
        print(f"Error updating product: {e}")

@print_wait
def save_data():
    try : 
        myinventory.save_data()
        print("Data saved successfully.")
    except Exception as e:
        print(f"Error saving data: {e}")

@print_wait
def display_all_products():
    myinventory.display_all_products()


def menu():
    print("-" * 40)
    print("Welcome to Inventory Management System")
    print("-" * 40)
    print("1. Add Product")
    print("2. Remove Product")
    print("3. Update Product")
    print("4. Display All Products")
    print("5. Save Data")
    print("6. Exit")


my_function = {
    "1": add_product,
    "2": remove_product,
    "3": update_product,
    "4": display_all_products,
    "5": save_data, 
}

@print_wait
def main():
    global myinventory
    myinventory = Inventory("inventory_data.json")
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        menu()
        print("-" * 40)
        print("Enter your choice: ", end="")
        choice = input().strip()
        if choice in my_function:
            my_function[choice]()
        elif choice == str(len(my_function) + 1):
            myinventory.save_data()
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
