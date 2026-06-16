-- ==========================================
-- INVENTORY MANAGEMENT SYSTEM
-- ==========================================

-- ==========================================
-- INVENTORY
-- ==========================================

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    area VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL
);

-- ==========================================
-- PRODUCT
-- ==========================================

CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0)
);

-- ==========================================
-- PRICE HISTORY
-- ==========================================

CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_price_history_product
        FOREIGN KEY (product_id)
        REFERENCES product(product_id)
        ON DELETE CASCADE
);

-- ==========================================
-- LOCATION
-- ==========================================

CREATE TABLE location (
    location_id SERIAL PRIMARY KEY,
    inventory_id INT NOT NULL,
    address VARCHAR(150) NOT NULL,

    CONSTRAINT fk_location_inventory
        FOREIGN KEY (inventory_id)
        REFERENCES inventory(inventory_id)
        ON DELETE CASCADE
);

-- ==========================================
-- STOCK
-- ==========================================

CREATE TABLE stock (
    stock_id SERIAL PRIMARY KEY,

    product_id INT NOT NULL,
    inventory_id INT NOT NULL,
    location_id INT NOT NULL,

    quantity INT NOT NULL DEFAULT 0
        CHECK (quantity >= 0),

    CONSTRAINT fk_stock_product
        FOREIGN KEY (product_id)
        REFERENCES product(product_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_stock_inventory
        FOREIGN KEY (inventory_id)
        REFERENCES inventory(inventory_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_stock_location
        FOREIGN KEY (location_id)
        REFERENCES location(location_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_stock
        UNIQUE (
            product_id,
            inventory_id,
            location_id
        )
);

-- ==========================================
-- INDEXES
-- ==========================================

CREATE INDEX idx_stock_product
ON stock(product_id);

CREATE INDEX idx_stock_inventory
ON stock(inventory_id);

CREATE INDEX idx_stock_location
ON stock(location_id);

CREATE INDEX idx_price_history_product
ON price_history(product_id);

CREATE INDEX idx_inventory_city
ON inventory(city);

-- ==========================================
-- TRIGGER FUNCTION
-- LOG PRICE CHANGES
-- ==========================================

CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS
$$
BEGIN
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        INSERT INTO price_history (
            product_id,
            price
        )
        VALUES (
            NEW.product_id,
            NEW.price
        );
    END IF;

    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- ==========================================
-- TRIGGER
-- AFTER PRODUCT PRICE UPDATE
-- ==========================================

CREATE TRIGGER trg_product_price_update
AFTER UPDATE ON product
FOR EACH ROW
EXECUTE FUNCTION log_price_change();

-- ==========================================
-- TRIGGER FUNCTION
-- STORE INITIAL PRICE
-- ==========================================

CREATE OR REPLACE FUNCTION log_initial_price()
RETURNS TRIGGER AS
$$
BEGIN
    INSERT INTO price_history (
        product_id,
        price
    )
    VALUES (
        NEW.product_id,
        NEW.price
    );

    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

-- ==========================================
-- TRIGGER
-- AFTER PRODUCT INSERT
-- ==========================================

CREATE TRIGGER trg_product_price_insert
AFTER INSERT ON product
FOR EACH ROW
EXECUTE FUNCTION log_initial_price();

-- ==========================================
-- SAMPLE DATA
-- ==========================================

INSERT INTO inventory (
    name,
    area,
    city
)
VALUES
('Central Store', 'Downtown', 'Ahmedabad'),
('North Hub', 'Maninagar', 'Ahmedabad'),
('South Depot', 'Bopal', 'Ahmedabad');

INSERT INTO location (
    inventory_id,
    address
)
VALUES
(1, 'Central Store - Aisle 1'),
(1, 'Central Store - Aisle 2'),
(2, 'North Hub - Rack A'),
(2, 'North Hub - Rack B'),
(3, 'South Depot - Zone 1');

INSERT INTO product (
    name,
    price
)
VALUES
('Pen', 10.00),
('Notebook', 55.00),
('Pencil', 5.00),
('Eraser', 3.00),
('Marker', 25.00);

INSERT INTO stock (
    product_id,
    inventory_id,
    location_id,
    quantity
)
VALUES
(1, 1, 1, 100),
(2, 1, 2, 50),
(3, 2, 3, 200),
(4, 2, 4, 150),
(5, 3, 5, 75);

-- ==========================================
-- TEST PRICE HISTORY
-- ==========================================

UPDATE product
SET price = 12.50
WHERE product_id = 1;

UPDATE product
SET price = 60.00
WHERE product_id = 2;

-- ==========================================
-- INVENTORY REPORT
-- ==========================================

SELECT
    p.product_id,
    p.name AS product_name,
    p.price,
    i.name AS inventory_name,
    i.city,
    l.address,
    s.quantity
FROM stock s
JOIN product p
    ON s.product_id = p.product_id
JOIN inventory i
    ON s.inventory_id = i.inventory_id
JOIN location l
    ON s.location_id = l.location_id
ORDER BY p.name;