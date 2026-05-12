

INSERT INTO inventory (name, area, city) VALUES
('Main Warehouse', 'Andheri', 'Mumbai'),
('Secondary Warehouse', 'Navrangpura', 'Ahmedabad');

-- 2. Products
INSERT INTO product (name, price) VALUES
('Laptop', 55000.00),
('Mouse', 500.00),
('Keyboard', 1500.00);



-- 3. Price History
INSERT INTO price_history (product_id, price, changed_at) VALUES
(1, 50000.00, '2024-01-01 10:00:00'),
(1, 55000.00, '2025-01-01 10:00:00'),
(2, 450.00, '2024-06-01 10:00:00'),
(2, 500.00, '2025-02-01 10:00:00');

-- 4. Location (Hierarchy)
INSERT INTO location (address, parent_id) VALUES
('3rd Floor', NULL),   -- 1
('Room 202', 1),       -- 2
('HR Office Table', 2),-- 3
('Drawer 1', 3),       -- 4
('Room 101', 1),       -- 5
('Shelf A', 5);        -- 6

-- 5. Stock
INSERT INTO stock (product_id, inventory_id, location_id, quantity) VALUES
(1, 1, 4, 10),
(2, 1, 3, 50),
(3, 1, 6, 30),
(1, 2, 6, 5),
(2, 2, 5, 20);

COMMIT;



select * from price_history;