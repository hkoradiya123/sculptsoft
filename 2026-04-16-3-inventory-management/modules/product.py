#! Product Class
# Attributes:
# product_id
# name
# price
# quantity

#! Methods:
# update_quantity()
# update_price()
# display_details()


#! Guidelines
# Use proper class design
# Keep code modular
# Handle errors
# Avoid writing everything in one file

#! Deliverables
# Source code
# README (how to run and features)
# Sample output

# * Evaluation
# * OOP usage
# * Code structure
# * Feature completeness
# * Edge case handling


class Product:
    id_counter = 1

    def __init__(self, name, price, quantity, product_id=None):
        if product_id is None:
            self.id = Product.id_counter
            Product.id_counter += 1
        else:
            self.id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def update_price(self, new_price):
        if new_price < 0:
            print("Price cannot be negative.")
            return
        self.price = new_price

    def display_details(self):
        print(
            f"ID: {self.id}, Name: {self.name}, Price: {self.price}, Quantity: {self.quantity}"
        )
