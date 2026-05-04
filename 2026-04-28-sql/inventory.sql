create database inventory_management;


use inventory_management;

CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    area VARCHAR(100),
    city VARCHAR(100)
);

CREATE TABLE product (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE price_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    price DECIMAL(10,2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

describe price_history;

CREATE TABLE location (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    address VARCHAR(150),
    parent_id INT NULL,

    FOREIGN KEY (parent_id) REFERENCES location(location_id)
);




CREATE TABLE stock (
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    inventory_id INT,
    location_id INT,
    quantity INT,

    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (location_id) REFERENCES location(location_id),

    UNIQUE (product_id, inventory_id, location_id)
);

DELIMITER $$

CREATE TRIGGER after_price_update
AFTER UPDATE ON product
FOR EACH ROW
BEGIN
    IF OLD.price <> NEW.price THEN
        INSERT INTO price_history (product_id, price)
        VALUES (NEW.product_id, NEW.price);
    END IF;
END$$

DELIMITER ;





ALTER TABLE post 
ADD like_count INT DEFAULT 0,
ADD comment_count INT DEFAULT 0;

DELIMITER $$

CREATE TRIGGER after_post_like_insert
AFTER INSERT ON post_likelike_count
FOR EACH ROW
BEGIN
    UPDATE post
    SET like_count = like_count + 1
    WHERE id = NEW.post_id;
END$$

CREATE TRIGGER after_post_like_delete
AFTER DELETE ON post_like
FOR EACH ROW
BEGIN
    UPDATE post
    SET like_count = GREATEST(like_count - 1, 0)
    WHERE id = OLD.post_id;
END$$

CREATE TRIGGER after_comment_insert
AFTER INSERT ON comment
FOR EACH ROW
BEGIN
    UPDATE post
    SET comment_count = comment_count + 1
    WHERE id = NEW.post_id;
END$$

CREATE TRIGGER after_comment_delete
AFTER DELETE ON comment
FOR EACH ROW
BEGIN
    UPDATE post
    SET comment_count = GREATEST(comment_count - 1, 0)
    WHERE id = OLD.post_id;
END$$

DELIMITER ;

ALTER TABLE user 
DROP COLUMN last_seen,
ADD status ENUM('online','offline') DEFAULT 'offline';










