
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

    def __init__(self,filepath="../inventory_data.json"):
        self.collection = []
        self.filepath = filepath
        self.load_data()

    def add_product(self, product):
        if product.price <= 0:
            raise InvalidPriceError(product.price)
        if product.quantity < 0:
            raise InvalidQuantityError(product.quantity)

        for item in self.collection:
            if item.name.lower() == product.name.lower():
                raise DuplicateProductError(product.name)

        self.collection.append(product)
        print(f"{product.name} is added to the inventory")
        

    def remove_product(self, product_id):
        for i in self.collection:
            if i.id == product_id:
                self.collection.remove(i)
                return
        raise ProductNotFoundError(product_id)

    def update_product(self, product_id, name=None, price=None, quantity=None):
        if price is not None and price <= 0:
            raise InvalidPriceError(price)
        if quantity is not None and quantity < 0:
            raise InvalidQuantityError(quantity)

        for i in self.collection:
            if i.id == product_id:
                if name is not None:
                    i.name = name
                if price is not None:
                    i.price = price
                if quantity is not None:
                    i.quantity = quantity
                print(f"Product with ID {product_id} has been updated.")
                return
        raise ProductNotFoundError(product_id)

    def get_product(self, product_id):
        for i in self.collection:
            if i.id == product_id:
                return i
        raise ProductNotFoundError(product_id)

    def display_all_products(self):
        for i in self.collection:
            i.display_details()

    #! Additional Features (Optional)

    # * Low stock check

    def low_stock_check(self, threshold):
        low_stock_products = []
        for i in self.collection:
            if i.quantity <= threshold:
                low_stock_products.append(i)
        if not low_stock_products:
            print("No products with low stock")
        return low_stock_products

    # * Search by name
    def search_name(self, name):
        results = []
        for i in self.collection:
            if name.lower() in i.name.lower():
                results.append(i)
        if not results:
            print("No products found with that name")
        return results

    # * Total inventory value
    def total_value(self):
        total = 0
        for i in self.collection:
            total += i.price * i.quantity
        return total

    # * Save/load data
    def save_data(self):
        with open(self.filepath, "w") as f:
            products_data = []
            for i in self.collection:
                products_data.append({
                    "id": i.id,
                    "name": i.name,
                    "price": i.price,
                    "quantity": i.quantity
                })
            json.dump(products_data, f, indent=2)

    def load_data(self):
        # No data file yet: start with an empty inventory.
        if not os.path.exists(self.filepath):
            return

        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
        except:
            print(f"empty json file {self.filepath}. Starting with empty inventory.")
            return
        max_id = 0
        for item in data:
            product = Product(
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"],
                product_id=item["id"]
            )
            self.collection.append(product)
            if product.id > max_id:
                max_id = product.id
        if max_id >= Product.id_counter:
            Product.id_counter = max_id + 1
