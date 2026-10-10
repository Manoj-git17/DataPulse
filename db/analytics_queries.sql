-- ==============================================================================
-- DataPulse — Analytical SQL Queries & Business Intelligence Marts
-- ==============================================================================

-- 1. Executive Summary KPIs
-- Computes overall business health metrics
SELECT 
    COUNT(order_id) AS total_orders,
    SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
    ROUND(SUM(net_amount), 2) AS total_net_revenue,
    ROUND(SUM(estimated_profit), 2) AS total_profit,
    ROUND(AVG(net_amount), 2) AS average_order_value,
    ROUND((SUM(estimated_profit) / NULLIF(SUM(net_amount), 0)) * 100, 2) AS overall_profit_margin_pct
FROM fact_sales;

-- 2. Monthly Revenue Trend with Cumulative Running Total (Window Function)
-- Demonstrates temporal grouping and window functions
SELECT 
    strftime('%Y-%m', order_date) AS month,
    COUNT(order_id) AS orders_count,
    ROUND(SUM(net_amount), 2) AS monthly_revenue,
    ROUND(SUM(estimated_profit), 2) AS monthly_profit,
    ROUND(SUM(SUM(net_amount)) OVER (ORDER BY strftime('%Y-%m', order_date)), 2) AS cumulative_revenue
FROM fact_sales
WHERE order_status != 'Cancelled'
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month ASC;

-- 3. Regional Performance Breakdown
-- Demonstrates multi-table JOINs and dimensional aggregations
SELECT 
    c.customer_region,
    COUNT(s.order_id) AS order_count,
    ROUND(SUM(s.net_amount), 2) AS regional_revenue,
    ROUND(SUM(s.estimated_profit), 2) AS regional_profit,
    ROUND(AVG(s.net_amount), 2) AS avg_order_value,
    ROUND((SUM(s.estimated_profit) / NULLIF(SUM(s.net_amount), 0)) * 100, 2) AS profit_margin_pct
FROM fact_sales s
JOIN dim_customers c ON s.customer_id = c.customer_id
WHERE s.order_status = 'Delivered'
GROUP BY c.customer_region
ORDER BY regional_revenue DESC;

-- 4. Top 5 Performing Products by Revenue
-- Demonstrates dimensional grouping, sorting, and LIMIT
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(s.quantity) AS units_sold,
    ROUND(SUM(s.net_amount), 2) AS total_revenue,
    ROUND(SUM(s.estimated_profit), 2) AS total_profit,
    ROUND((SUM(s.estimated_profit) / NULLIF(SUM(s.net_amount), 0)) * 100, 2) AS profit_margin_pct
FROM fact_sales s
JOIN dim_products p ON s.product_id = p.product_id
WHERE s.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;

-- 5. Customer Lifetime Value (CLV) & Ranking
-- Demonstrates analytical window function RANK()
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_region,
    COUNT(s.order_id) AS total_orders,
    ROUND(SUM(s.net_amount), 2) AS total_spend,
    ROUND(AVG(s.net_amount), 2) AS avg_spend_per_order,
    RANK() OVER (ORDER BY SUM(s.net_amount) DESC) AS customer_rank
FROM fact_sales s
JOIN dim_customers c ON s.customer_id = c.customer_id
WHERE s.order_status != 'Cancelled'
GROUP BY c.customer_id, c.customer_name, c.customer_region
ORDER BY customer_rank ASC;

-- 6. Payment Method Distribution & Health
-- Analyzes customer checkout preferences and cancellation rates
SELECT 
    payment_method,
    COUNT(order_id) AS total_transactions,
    ROUND(SUM(net_amount), 2) AS total_revenue,
    ROUND((COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM fact_sales)), 2) AS share_of_transactions_pct,
    ROUND((SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(order_id)), 2) AS cancellation_rate_pct
FROM fact_sales
GROUP BY payment_method
ORDER BY total_transactions DESC;
