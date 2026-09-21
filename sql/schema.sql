DROP TABLE IF EXISTS markdowns;

DROP TABLE IF EXISTS price_history;

DROP TABLE IF EXISTS sales;

DROP TABLE IF EXISTS catalog;

DROP TABLE IF EXISTS stores;

CREATE TABLE
    stores (
        store_id INTEGER PRIMARY KEY,
        division TEXT,
        format TEXT,
        city TEXT,
        area TEXT
    );

CREATE TABLE
    catalog (
        item_id TEXT PRIMARY KEY,
        dept_name TEXT,
        class_name TEXT,
        subclass_name TEXT,
        item_type TEXT,
        weight_volume REAL,
        weight_netto REAL,
        fatness REAL
    );

CREATE TABLE
    sales (
        date TEXT NOT NULL,
        item_id TEXT NOT NULL,
        quantity REAL NOT NULL,
        price_base REAL,
        sum_total REAL,
        store_id INTEGER NOT NULL,
        FOREIGN KEY (item_id) REFERENCES catalog (item_id),
        FOREIGN KEY (store_id) REFERENCES stores (store_id)
    );

CREATE TABLE
    markdowns (
        date TEXT NOT NULL,
        item_id TEXT NOT NULL,
        normal_price REAL,
        price REAL,
        quantity REAL,
        store_id INTEGER NOT NULL,
        FOREIGN KEY (item_id) REFERENCES catalog (item_id),
        FOREIGN KEY (store_id) REFERENCES stores (store_id)
    );

CREATE TABLE
    price_history (
        date TEXT NOT NULL,
        item_id TEXT NOT NULL,
        price REAL,
        code TEXT,
        store_id INTEGER NOT NULL,
        FOREIGN KEY (item_id) REFERENCES catalog (item_id),
        FOREIGN KEY (store_id) REFERENCES stores (store_id)
    );

CREATE INDEX idx_sales_date ON sales (date);

CREATE INDEX idx_sales_item ON sales (item_id);

CREATE INDEX idx_sales_store ON sales (store_id);

CREATE INDEX idx_sales_store_date ON sales (store_id, date);

CREATE INDEX idx_markdowns_item ON markdowns (item_id);

CREATE INDEX idx_markdowns_store_date ON markdowns (store_id, date);

CREATE INDEX idx_price_history_item_store_date ON price_history (item_id, store_id, date);