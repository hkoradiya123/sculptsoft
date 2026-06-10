from decimal import Decimal

from database.dbhelper import db
from models.inventory import Inventory, Location
from models.product import Product
from models.stock import Stock


def seed_data():
    session = db.get_session()

    try:
        # Inventories
        central = Inventory(
            name="Central Store",
            area="Downtown",
            city="Ahmedabad"
        )

        north = Inventory(
            name="North Hub",
            area="Maninagar",
            city="Ahmedabad"
        )

        south = Inventory(
            name="South Depot",
            area="Bopal",
            city="Ahmedabad"
        )

        session.add_all([central, north, south])
        session.flush()

        # Locations
        locations = [
            Location(
                inventory_id=central.inventory_id,
                address="Central Store - Aisle 1"
            ),
            Location(
                inventory_id=central.inventory_id,
                address="Central Store - Aisle 2"
            ),
            Location(
                inventory_id=north.inventory_id,
                address="North Hub - Rack A"
            ),
            Location(
                inventory_id=north.inventory_id,
                address="North Hub - Rack B"
            ),
            Location(
                inventory_id=south.inventory_id,
                address="South Depot - Zone 1"
            ),
        ]

        session.add_all(locations)
        session.flush()

        # Products
        products = [
            Product(name="Pen", price=Decimal("10.00")),
            Product(name="Notebook", price=Decimal("55.00")),
            Product(name="Pencil", price=Decimal("5.00")),
            Product(name="Eraser", price=Decimal("3.00")),
            Product(name="Marker", price=Decimal("25.00")),
        ]

        session.add_all(products)
        session.flush()

        # Stock
        stocks = [
            Stock(
                product_id=products[0].product_id,
                inventory_id=central.inventory_id,
                location_id=locations[0].location_id,
                quantity=100,
            ),
            Stock(
                product_id=products[1].product_id,
                inventory_id=central.inventory_id,
                location_id=locations[1].location_id,
                quantity=50,
            ),
            Stock(
                product_id=products[2].product_id,
                inventory_id=north.inventory_id,
                location_id=locations[2].location_id,
                quantity=200,
            ),
            Stock(
                product_id=products[3].product_id,
                inventory_id=north.inventory_id,
                location_id=locations[3].location_id,
                quantity=150,
            ),
            Stock(
                product_id=products[4].product_id,
                inventory_id=south.inventory_id,
                location_id=locations[4].location_id,
                quantity=75,
            ),
        ]

        session.add_all(stocks)

        session.commit()

        print("Dummy data inserted successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")

    finally:
        session.close()


if __name__ == "__main__":
    seed_data()