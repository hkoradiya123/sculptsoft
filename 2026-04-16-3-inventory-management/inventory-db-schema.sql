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
    location_i- 2. Create Tables (Your Schema)
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

-- 3. Create Trigger Function and Binding
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
EXECUTE FUNCTION log_price_change();d SERIAL PRIMARY KEY,
    inventory_id INT NOT NULL,
    address VARCHAR(150),
        
    FOREIGN KEY (inventory_id)
        REFERENCES inventory(inventory_id)
        ON DELETE CASCADE
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

-- 1. Create the Trigger Function
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if price actually changed
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        INSERT INTO price_history (product_id, price)
        VALUES (NEW.product_id, NEW.price);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Bind the Function to the Product Table
CREATE TRIGGER after_price_update
AFTER UPDATE ON product
FOR EACH ROW
EXECUTE FUNCTION log_price_change();
