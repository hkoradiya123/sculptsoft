from modules import *
import os
import dotenv
from modules.dbhelper import db

current_inventory = None
inventories = []


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
def read_non_empty_string(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")

# Inventory selection
@print_wait
def change_inventory():
    global current_inventory
    if not inventories:
        print("No inventories found. Please create one.")
        return
    
    print("-" * 40)
    print("Select Inventory:")
    print("-" * 40)
    for idx, inv in enumerate(inventories):
        print(f"{idx+1}. {inv['name']} ({inv['area']}, {inv['city']})")
    print(f"{len(inventories)+1}. Create Inventory")
    choice = read_int("Enter inventory number: ")
    if 1 <= choice <= len(inventories):
        inv_info = inventories[choice-1]
        current_inventory = Inventory(inv_info['name'], inv_info['area'], inv_info['city'])
        current_inventory.id = inv_info['id']
        print(f"\nSelected inventory: {current_inventory.name}")
    elif choice == len(inventories)+1:
        create_inventory()
    else:
        print("Invalid choice.")

def load_inventories():
    global inventories
    # Load all inventories from DB
    results = db.execute_query("SELECT inventory_id, name, area, city FROM inventory")
    if results and results != "No results found.":
        inventories = [
            {'id': row[0], 'name': row[1], 'area': row[2], 'city': row[3]}
            for row in results
        ]
    else:
        inventories = []

@print_wait
def create_inventory():
    name = read_non_empty_string("Enter inventory name: ")
    area = read_non_empty_string("Enter area: ")
    city = read_non_empty_string("Enter city: ")
    inv = Inventory.create_inventory(name, area, city)
    global inventories
    id = db.execute_query("")
    inventories.append({'id': inv.id, 'name': name, 'area': area, 'city': city})
    print(f"Created inventory: {name}")

@print_wait
def new_product():
    if not current_inventory:
        print("Select an inventory first!")
        return
    name = read_non_empty_string("Enter product name: ")
    price = read_float("Enter product price: ")
    try:
        Product.new_product(name, price)
    except ValueError as e:
        print(f"Error creating product: {e}")


@print_wait
def add_product():
    if not current_inventory:
        print("Select an inventory first!")
        return
    name = read_non_empty_string("Enter product name: ")
    price = read_float("Enter product price: ")
    quantity = read_int("Enter product quantity: ")
    # For simplicity, pick first location
    locations = current_inventory.get_all_locations()
    if not locations:
        print("No locations found for this inventory. Please create one.")
        return
    print("Select location:")
    for idx, loc in enumerate(locations):
        print(f"{idx+1}. {loc[1]}")
    loc_choice = read_int("Enter location number: ")
    if 1 <= loc_choice <= len(locations):
        location_id = locations[loc_choice-1][0]
        class DummyLocation:
            def __init__(self, id):
                self.id = id
        location = DummyLocation(location_id)
        # Find product by name or create
        prod_result = db.execute_query("SELECT product_id, name, price FROM product WHERE name = %s", (name,))
        if prod_result and prod_result != "No results found.":
            prod_id, prod_name, prod_price = prod_result[0]
            class DummyProduct:
                def __init__(self, id, name, price):
                    self.id = id
                    self.name = name
                    self.price = price
            product = DummyProduct(prod_id, prod_name, prod_price)
        else:
            product = Product(name, price)
            # Insert and get id
            db.execute_query("INSERT INTO product (name, price) VALUES (%s, %s)", (name, price))
            prod_id = db.execute_query("SELECT LAST_INSERT_ID()")
            product.id = prod_id[0][0] if prod_id else None
        try:
            current_inventory.add_product(product, quantity, location)
        except ValueError as e:
            print(f"Error adding product: {e}")
    else:
        print("Invalid location choice.")

@print_wait
def remove_product():
    if not current_inventory:
        print("Select an inventory first!")
        return
    print("-" * 40)
    try:
        current_inventory.display_all_products()
        product_id = read_int("Enter product ID to remove: ")
        Product.remove_product(product_id)
    except ValueError as e:
        print(f"Error removing product: {e}")   

@print_wait
def update_product():
    if not current_inventory:
        print("Select an inventory first!")
        return
    current_inventory.display_all_products()
    product_id = read_int("Enter product ID to update: ")
    if Product.check_product_exists(current_inventory, product_id):
        name = input("Enter new product name (leave blank to keep unchanged): ").strip() or None
        # Use a temporary variable for price to distinguish between 0 and an error
        raw_price = read_float("Enter new price (enter 0 to keep unchanged): ")
        price = raw_price if raw_price != 0 else None

        Product.update_product(current_inventory, product_id=product_id, name=name, price=price)
    else:
        print("Product not found.")
    
    
@print_wait
def display_all_products():
    if not current_inventory:
        print("Select an inventory first!")
        return
    current_inventory.display_all_products()


menu_options = {
    "Change Inventory": change_inventory,
    "Create Product": new_product,
    "Add Existing Product": add_product,
    "Create and Add Product to Inventory": lambda: (new_product(), add_product()),
    "Remove Product": remove_product,
    "Update Product": update_product,
    "Display All Products": display_all_products,
    }


def menu():
    print("-" * 40)
    print("Welcome to Inventory Management System")
    print("-" * 40)
    print("-" * 40)
    print("Current Inventory:", current_inventory.name if current_inventory else "None")
    print("-" * 40)
    for idx, option in enumerate(menu_options.keys(), 1):
        print(f"{idx}. {option}")
    print(f"{len(menu_options) + 1}. Exit")


def main():
    load_inventories()
    while True:
        if not current_inventory and inventories:
            change_inventory()
        os.system("cls" if os.name == "nt" else "clear")
        menu()
        print("-" * 40)
        print("Enter your choice: ", end="")
        choice = input().strip()
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(menu_options):
                list(menu_options.values())[choice_num - 1]()
            elif choice_num == len(menu_options) + 1:
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
        elif choice == len(menu_options) + 1:
            print("Exiting...")
            break
        else:
            print("Invalid input. Please enter a number corresponding to the menu options.")

if __name__ == "__main__":
    main()
