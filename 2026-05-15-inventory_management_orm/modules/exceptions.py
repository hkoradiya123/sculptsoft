class InventoryError(Exception):
    """Base exception for inventory app."""
    pass


class ProductNotFoundError(InventoryError):
    def __init__(self, product_id):
        super().__init__(f"Product with ID {product_id} not found")


class DuplicateProductError(InventoryError):
    def __init__(self, name):
        super().__init__(f"Product '{name}' already exists")


class InvalidQuantityError(InventoryError):
    def __init__(self, quantity):
        super().__init__(f"Quantity must be >= 0, got {quantity}")


class InvalidPriceError(InventoryError):
    def __init__(self, price):
        super().__init__(f"Price must be > 0, got {price}")


class InsufficientStockError(InventoryError):
    def __init__(self, name, requested, available):
        super().__init__(
            f"Insufficient stock for '{name}'. Requested: {requested}, Available: {available}"
        )