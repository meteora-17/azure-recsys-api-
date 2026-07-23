-- Schema + seed data for the recommendation API's Azure SQL Database.
-- Mirrors the in-memory PRODUCTS / USER_HISTORY used in local dev and tests.

CREATE TABLE Products (
    id INT PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    category NVARCHAR(50) NOT NULL
);

CREATE TABLE UserHistory (
    user_id NVARCHAR(50) NOT NULL,
    product_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

INSERT INTO Products (id, name, category) VALUES
    (1, 'Wireless Mouse', 'Electronics'),
    (2, 'Mechanical Keyboard', 'Electronics'),
    (3, 'Notebook', 'Stationery'),
    (4, 'Water Bottle', 'Home'),
    (5, 'Desk Lamp', 'Home');

INSERT INTO UserHistory (user_id, product_id) VALUES
    ('u1', 1), ('u1', 2),
    ('u2', 3), ('u2', 4),
    ('u3', 1), ('u3', 5);
