#!/usr/bin/env python3
import os
import sys
from decimal import Decimal

# Ensure project root is in path
sys.path.append(os.getcwd())

from app.database.dbhelper import db
from app.models.user import User
from app.models.product import Product
from app.models.inventory import Inventory, Location
from app.models.stock import Stock
from app.core.security import hash_password

def seed_db():
    session = db.get_session()
    try:
        print("[SEED] Starting Database Seeding...")

        # 1. Seed Users
        print("\n--- Seeding Users ---")
        dummy_users = [
            {"email": "admin@ss.com", "password": "admin123", "role": "admin"},
            {"email": "manager@ss.com", "password": "manager123", "role": "manager"},
            {"email": "editor@ss.com", "password": "editor123", "role": "editor"},
            {"email": "viewer@ss.com", "password": "viewer123", "role": "viewer"},
        ]
        for u_data in dummy_users:
            if not session.query(User).filter(User.email == u_data["email"]).first():
                user = User(
                    email=u_data["email"],
                    hashed_password=hash_password(u_data["password"]),
                    role=u_data["role"]
                )
                session.add(user)
                print(f"- Created user: {u_data['email']}")
        session.commit()

        # 2. Seed Inventories & Locations
        print("\n--- Seeding Inventories & Locations ---")
        inventories_data = [
            {
                "name": "North Hub", "area": "GIFT City", "city": "Gandhinagar",
                "locations": ["Floor 1, A-Block", "Floor 2, B-Block"]
            },
            {
                "name": "South Warehouse", "area": "Whitefield", "city": "Bangalore",
                "locations": ["Zone 1, Rack A1", "Zone 2, Rack B2"]
            }
        ]
        
        for inv_data in inventories_data:
            inv = session.query(Inventory).filter(Inventory.name == inv_data["name"]).first()
            if not inv:
                inv = Inventory(name=inv_data["name"], area=inv_data["area"], city=inv_data["city"])
                session.add(inv)
                session.flush() # Get ID
                print(f"- Created inventory: {inv_data['name']}")
                
                for loc_addr in inv_data["locations"]:
                    loc = Location(inventory_id=inv.inventory_id, address=loc_addr)
                    session.add(loc)
                    print(f"  - Created location: {loc_addr}")
        session.commit()

        # 3. Seed Products
        print("\n--- Seeding Products ---")
        products_data = [
            {"name": "MacBook Pro M3", "price": Decimal("199999.00")},
            {"name": "iPhone 15 Pro", "price": Decimal("134900.00")},
            {"name": "Logitech MX Master 3S", "price": Decimal("10995.00")},
            {"name": "Keychron K2 V2", "price": Decimal("8500.00")},
            {"name": "Dell UltraSharp 27", "price": Decimal("45000.00")}
        ]
        for p_data in products_data:
            if not session.query(Product).filter(Product.name == p_data["name"]).first():
                prod = Product(name=p_data["name"], price=p_data["price"])
                session.add(prod)
                print(f"- Created product: {p_data['name']}")
        session.commit()

        # 4. Seed Stock (Link everything)
        print("\n--- Seeding Stock ---")
        all_prods = session.query(Product).all()
        all_locs = session.query(Location).all()
        
        if all_prods and all_locs:
            for i, prod in enumerate(all_prods):
                # Assign to a location (cycle through them)
                loc = all_locs[i % len(all_locs)]
                # Check if stock already exists
                existing_stock = session.query(Stock).filter(
                    Stock.product_id == prod.product_id,
                    Stock.inventory_id == loc.inventory_id,
                    Stock.location_id == loc.location_id
                ).first()
                
                if not existing_stock:
                    stock = Stock(
                        product_id=prod.product_id,
                        inventory_id=loc.inventory_id,
                        location_id=loc.location_id,
                        quantity=(i + 1) * 10
                    )
                    session.add(stock)
                    print(f"- Stock added: {prod.name} at {loc.address} (Qty: {stock.quantity})")
        
        session.commit()
        print("\n[SEED] Database Seeding Completed Successfully!")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error during seeding: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_db()
