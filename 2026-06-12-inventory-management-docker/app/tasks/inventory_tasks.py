import logging
from celery_app import celery_app
from app.database.dbhelper import db
from app.models.product import Product
from app.models.stock import Stock

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.inventory_tasks.check_low_stock")
def check_low_stock(self, product_id: int):
    """
    Industry Workflow:
    Jab bhi stock update ho, ye task trigger hota hai check karne ke liye 
    ki stock 'Critical' level se niche toh nahi gaya.
    """
    with db.session_scope() as session:
        product = session.get(Product, product_id)
        if not product:
            logger.error(f"Product {product_id} not found in DB")
            return

        # Sabhi locations ka total stock nikalte hain
        total_stock = sum(s.quantity for s in product.stocks)
        
        # Maan le threshold 10 hai
        THRESHOLD = 10
        
        if total_stock < THRESHOLD:
            # Yahan Real world mein Email/Slack notification jayega
            print(f"\n[ALERT] LOW STOCK: Product '{product.name}' (ID: {product_id}) has only {total_stock} units left!\n")
            return f"Alert sent for {product.name}"
        
        return f"Stock level OK for {product.name} ({total_stock} units)"

@celery_app.task(name="app.tasks.inventory_tasks.bulk_import_products")
def bulk_import_products(product_list: list):
    """
    Problem: 1000 products insert karne mein API block ho jayegi.
    Solution: Backend mein bulk insert karo.
    """
    with db.session_scope() as session:
        new_products = [Product(name=p['name'], price=p['price']) for p in product_list]
        session.add_all(new_products)
        session.commit()
    return f"Successfully imported {len(product_list)} products."

@celery_app.task(name="app.tasks.inventory_tasks.generate_inventory_report")
def generate_inventory_report(inventory_id: int):
    """
    Industry Workflow:
    Heavy computation of stock value across all locations in an inventory.
    """
    import time
    logger.info(f"Starting report generation for inventory: {inventory_id}")
    time.sleep(10) # Simulating heavy processing

    try:
        with db.session_scope() as session:
            # Business logic: Calculate total value of inventory
            results = (
                session.query(Product.price, Stock.quantity)
                .join(Stock, Product.product_id == Stock.product_id)
                .filter(Stock.inventory_id == inventory_id)
                .all()
            )
            
            if not results:
                logger.warning(f"No stock data found for inventory {inventory_id}")
                return {
                    "inventory_id": inventory_id,
                    "error": "No data found for this inventory",
                    "status": "EMPTY"
                }

            total_value = sum((price or 0) * (quantity or 0) for price, quantity in results)
            
            report_data = {
                "inventory_id": inventory_id,
                "total_products_tracked": len(results),
                "total_inventory_value": float(total_value),
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            logger.info(f"Successfully generated report for inventory {inventory_id}")
            return report_data
    except Exception as e:
        logger.error(f"Error generating report for inventory {inventory_id}: {str(e)}", exc_info=True)
        return {"error": str(e)}
