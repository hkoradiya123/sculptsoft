-- Schema
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    area VARCHAR(100),
    city VARCHAR(100)
);

CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id INT,
    price DECIMAL(10,2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

CREATE TABLE location (
    location_id SERIAL PRIMARY KEY,
    inventory_id INT NOT NULL,
    address VARCHAR(150),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id) ON DELETE CASCADE
);

CREATE TABLE stock (
    stock_id SERIAL PRIMARY KEY,
    product_id INT,
    inventory_id INT,
    location_id INT,
    quantity INT,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (location_id) REFERENCES location(location_id),
    UNIQUE (product_id, inventory_id, location_id)
);

-- Trigger for price history
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        INSERT INTO price_history (product_id, price)
        VALUES (NEW.product_id, NEW.price);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_price_update
AFTER UPDATE ON product
FOR EACH ROW
EXECUTE FUNCTION log_price_change();

-- Dummy data
INSERT INTO inventory (name, area, city) VALUES
('Central Store', 'Downtown', 'Ahmedabad'),
('North Hub', 'Maninagar', 'Ahmedabad'),
('South Depot', 'Bopal', 'Ahmedabad');

INSERT INTO location (inventory_id, address) VALUES
(1, 'Central Store - Aisle 1'),
(1, 'Central Store - Aisle 2'),
(2, 'North Hub - Rack A'),
(2, 'North Hub - Rack B'),
(3, 'South Depot - Zone 1');

INSERT INTO product (name, price) VALUES
('Pen', 10.00),
('Notebook', 55.00),
('Pencil', 5.00),
('Eraser', 3.00),
('Marker', 25.00);

INSERT INTO stock (product_id, inventory_id, location_id, quantity) VALUES
(1, 1, 1, 100),
(2, 1, 2, 50),
(3, 2, 3, 200),
(4, 2, 4, 150),
(5, 3, 5, 75);
