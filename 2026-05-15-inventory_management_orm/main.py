from modules import *
import os
import dotenv
from database.dbhelper import db
from database import model

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
def read_price(prompt):
    while True:
        try:
            price = float(input(prompt))
            if price <= 0:
                print("Price must be greater than zero. Please try again.")
            else:
                return price
        except ValueError:
            print("Invalid input. Please enter a valid price.")

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
    choice = read_int("\nEnter inventory number: ")
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
    inventories = Inventory.get_all_inventories()

@print_wait
def create_inventory():
    name = read_non_empty_string("Enter inventory name: ")
    area = read_non_empty_string("Enter area: ")
    city = read_non_empty_string("Enter city: ")
    inv = Inventory.create_inventory(name, area, city)
    global inventories
    inventories.append({'id': inv.id, 'name': name, 'area': area, 'city': city})
    print(f"Created inventory: {name}")

@print_wait
def create_product():
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
    Product.display_all_products()
    try:
        product_id = int(read_non_empty_string("Enter product id: "))
    except ValueError:
        print("Invalid product ID.")
        return
    if product_id not in Product.get_all_product_ids():
        print("Product not found in product database. Please create it first.")
        return
    if product_id in current_inventory.get_all_product_ids():
        print("Product already exists in this inventory. Use update to change quantity.")
        return
    quantity = read_int("Enter product quantity: ")
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
        try:
            current_inventory.add_product(product_id, quantity, location_id)
        except ValueError as e:
            print(f"Error adding product: {e}")
    else:
        print("Invalid location choice.")
        
@print_wait
def create_add_product():
    if not current_inventory:
        print("Select an inventory first!")
        return
    name = read_non_empty_string("Enter product name: ")
    price = read_price("Enter product price: ")
    quantity = read_int("Enter product quantity: ")
    locations = current_inventory.get_all_locations()
    if not locations:
        print("No locations found for this inventory. Please create one.\n")
        print("wold you like to create a location now? (y/n): ", end="")
        choice = read_non_empty_string("").strip().lower()
        if choice == 'y':
            add_address()
        return
    print("Select location:")
    for idx, loc in enumerate(locations):
        print(f"{idx+1}. {loc[1]}")
    loc_choice = read_int("Enter location number: ")
    if 1 <= loc_choice <= len(locations):
        location_id = locations[loc_choice-1][0]
        try:
            product_id = Product.new_product(name, price)
            if product_id:
                current_inventory.add_product(product_id, quantity, location_id)
        except ValueError as e:
            print(f"Error creating and adding product: {e}")
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
        current_inventory.remove_product(product_id)
    except ValueError as e:
        print(f"Error removing product: {e}")   

@print_wait
def update_product():
    if not current_inventory:
        print("Select an inventory first!")
        return
    current_inventory.display_all_products()
    product_id = read_int("Enter product ID to update: ")
    if Product.check_product_exists(product_id):
        name = input("Enter new product name (leave blank to keep unchanged): ").strip() or None
        # Use a temporary variable for price to distinguish between 0 and an error
        raw_price = read_float("Enter new price (enter 0 to keep unchanged): ")
        price = raw_price if raw_price != 0 else None
        raw_quantity = read_int("Enter new quantity (enter 0 to keep unchanged): ")
        quantity = raw_quantity if raw_quantity != 0 else None
        

        current_inventory.update_product(product_id=product_id, name=name, price=price, quantity=quantity)
    else:
        print("Product not found.")
    
    
@print_wait
def display_all_products_in_inventory():
    if not current_inventory:
        print("Select an inventory first!")
        return
    current_inventory.display_all_products()
@print_wait
def add_address():
    if not current_inventory:
        print("Select an inventory first!")
        return
    address = read_non_empty_string("Enter new address/location: ")
    current_inventory.create_inventory_location(address)

@print_wait
def update_address():
    if not current_inventory:
        print("Select an inventory first!")
        return
    locations = current_inventory.get_all_locations()
    if not locations:
        print("No addresses found for this inventory.")
        return
    print("Select address to update:")
    for idx, loc in enumerate(locations):
        print(f"{idx+1}. {loc[1]}")
    loc_choice = read_int("Enter address number: ")
    if 1 <= loc_choice <= len(locations):
        address_id = locations[loc_choice-1][0]
        new_address = read_non_empty_string("Enter new address: ")
        current_inventory.update_location(address_id, new_address)
    else:
        print("Invalid address choice.")

@print_wait
def display_all_addresses():
    if not current_inventory:
        print("Select an inventory first!")
        return
    locations = current_inventory.get_all_locations()
    if not locations:
        print("No addresses found for this inventory.")
        return
    print(f"\n--- Addresses for {current_inventory.name} ---")
    for loc in locations:
        print(f"ID: {loc[0]} | Address: {loc[1]}")
    print()

menu_options = {
    "Change Inventory": change_inventory,
    "Add Location": add_address,
    "Update Location": update_address,
    "Display All Locations": display_all_addresses,
    "Create Product": create_product,
    "Add Existing Product": add_product,
    "Create and Add Product to Inventory": create_add_product,
    "Remove Product": remove_product,
    "Update Product": update_product,
    "Display All Products": display_all_products_in_inventory,
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
        else:
            print("Invalid input. Please enter a number corresponding to the menu options.")

if __name__ == "__main__":
    db.create_tables()
    main()
