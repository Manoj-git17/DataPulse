-- ==============================================================================
-- DataPulse — Relational Star Schema DDL (PostgreSQL & SQLite Compatible)
-- ==============================================================================

-- 1. Customer Dimension Table
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id     VARCHAR(50) PRIMARY KEY,
    customer_name   VARCHAR(150) NOT NULL,
    customer_email  VARCHAR(200),
    customer_region VARCHAR(50) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_customers_region ON dim_customers(customer_region);

-- 2. Product Dimension Table
CREATE TABLE IF NOT EXISTS dim_products (
    product_id   VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category     VARCHAR(100) NOT NULL,
    unit_price   NUMERIC(10, 2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_products_category ON dim_products(category);

-- 3. Sales Fact Table
CREATE TABLE IF NOT EXISTS fact_sales (
    order_id          VARCHAR(50) PRIMARY KEY,
    order_date        TIMESTAMP NOT NULL,
    customer_id       VARCHAR(50) NOT NULL,
    product_id        VARCHAR(50) NOT NULL,
    quantity          INTEGER NOT NULL,
    discount_percent  NUMERIC(5, 4) DEFAULT 0.0,
    gross_amount      NUMERIC(12, 2) NOT NULL,
    discount_amount   NUMERIC(12, 2) DEFAULT 0.0,
    net_amount        NUMERIC(12, 2) NOT NULL,
    estimated_cogs    NUMERIC(12, 2) NOT NULL,
    estimated_profit  NUMERIC(12, 2) NOT NULL,
    profit_margin_pct NUMERIC(6, 2) DEFAULT 0.0,
    payment_method    VARCHAR(50) NOT NULL,
    order_status      VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON fact_sales(order_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON fact_sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_product ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_status ON fact_sales(order_status);

-- 4. Analytical Views for Business Intelligence

-- View: Regional Revenue Summary
CREATE VIEW IF NOT EXISTS v_regional_performance AS
SELECT 
    c.customer_region,
    COUNT(s.order_id) AS total_orders,
    SUM(s.net_amount) AS total_revenue,
    SUM(s.estimated_profit) AS total_profit,
    ROUND(AVG(s.net_amount), 2) AS avg_order_value,
    ROUND((SUM(s.estimated_profit) / NULLIF(SUM(s.net_amount), 0)) * 100, 2) AS profit_margin_pct
FROM fact_sales s
JOIN dim_customers c ON s.customer_id = c.customer_id
WHERE s.order_status = 'Delivered'
GROUP BY c.customer_region;

-- View: Category Performance
CREATE VIEW IF NOT EXISTS v_category_performance AS
SELECT 
    p.category,
    COUNT(s.order_id) AS total_orders,
    SUM(s.quantity) AS total_units_sold,
    SUM(s.net_amount) AS total_revenue,
    SUM(s.estimated_profit) AS total_profit
FROM fact_sales s
JOIN dim_products p ON s.product_id = p.product_id
WHERE s.order_status = 'Delivered'
GROUP BY p.category;
