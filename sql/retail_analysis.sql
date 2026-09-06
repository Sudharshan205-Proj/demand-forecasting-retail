-- ============================================================================
-- Phase 4 — Retail Demand Forecasting SQL Analysis
-- ============================================================================


-- ============================================================================
-- Query 1 — Basic SELECT and ORDER BY
-- Question:
-- Which stores are present in the database?
-- ============================================================================

SELECT
    store_id,
    division,
    format,
    city,
    area
FROM stores
ORDER BY store_id;


-- ============================================================================
-- Query 2 — WHERE filtering and ORDER BY
-- Question:
-- Which sales records have relatively high quantities?
-- ============================================================================

SELECT
    date,
    item_id,
    quantity,
    price_base,
    sum_total,
    store_id
FROM sales
WHERE quantity > 100
ORDER BY quantity DESC
LIMIT 20;


-- ============================================================================
-- Query 3 — Aggregate functions
-- Question:
-- What are the overall sales totals?
-- ============================================================================

SELECT
    COUNT(*) AS transaction_rows,
    COUNT(DISTINCT item_id) AS unique_items,
    COUNT(DISTINCT store_id) AS unique_stores,
    SUM(quantity) AS total_quantity,
    SUM(sum_total) AS total_sales_value,
    AVG(quantity) AS average_quantity
FROM sales;


-- ============================================================================
-- Query 4 — GROUP BY
-- Question:
-- How does demand differ between stores?
-- ============================================================================

SELECT
    store_id,
    SUM(quantity) AS total_quantity,
    SUM(sum_total) AS total_sales_value,
    COUNT(*) AS transaction_rows
FROM sales
GROUP BY store_id
ORDER BY total_quantity DESC;


-- ============================================================================
-- Query 5 — GROUP BY + HAVING
-- Question:
-- Which stores have more than one million units of recorded demand?
-- ============================================================================

SELECT
    store_id,
    SUM(quantity) AS total_quantity
FROM sales
GROUP BY store_id
HAVING SUM(quantity) > 1000000
ORDER BY total_quantity DESC;


-- ============================================================================
-- Query 6 — Calculated field
-- Question:
-- What is the average recorded sales value per unit by store?
-- ============================================================================

SELECT
    store_id,
    SUM(sum_total) AS total_sales_value,
    SUM(quantity) AS total_quantity,
    CASE
        WHEN SUM(quantity) = 0 THEN NULL
        ELSE SUM(sum_total) / SUM(quantity)
    END AS sales_value_per_unit
FROM sales
GROUP BY store_id
ORDER BY sales_value_per_unit DESC;


-- ============================================================================
-- Query 7 — JOIN
-- Question:
-- How does store demand look when store city information is included?
-- ============================================================================

SELECT
    s.store_id,
    s.city,
    s.format,
    SUM(sa.quantity) AS total_quantity,
    SUM(sa.sum_total) AS total_sales_value
FROM sales AS sa
INNER JOIN stores AS s
    ON sa.store_id = s.store_id
GROUP BY
    s.store_id,
    s.city,
    s.format
ORDER BY total_quantity DESC;


-- ============================================================================
-- Query 8 — JOIN sales to catalog
-- Question:
-- How does demand vary across departments?
-- ============================================================================

SELECT
    c.dept_name,
    SUM(s.quantity) AS total_quantity,
    SUM(s.sum_total) AS total_sales_value,
    COUNT(DISTINCT s.item_id) AS unique_items
FROM sales AS s
INNER JOIN catalog AS c
    ON s.item_id = c.item_id
GROUP BY c.dept_name
ORDER BY total_quantity DESC;


-- ============================================================================
-- Query 9 — Multiple-table JOIN
-- Question:
-- Which departments generate the greatest demand by store?
-- ============================================================================

SELECT
    st.city,
    c.dept_name,
    SUM(sa.quantity) AS total_quantity,
    SUM(sa.sum_total) AS total_sales_value
FROM sales AS sa
INNER JOIN stores AS st
    ON sa.store_id = st.store_id
INNER JOIN catalog AS c
    ON sa.item_id = c.item_id
GROUP BY
    st.city,
    c.dept_name
ORDER BY
    st.city,
    total_quantity DESC;


-- ============================================================================
-- Query 10 — Subquery
-- Question:
-- Which items have demand above the average item demand?
-- ============================================================================

SELECT
    item_id,
    total_quantity
FROM (
    SELECT
        item_id,
        SUM(quantity) AS total_quantity
    FROM sales
    GROUP BY item_id
)
WHERE total_quantity > (
    SELECT AVG(item_total)
    FROM (
        SELECT
            item_id,
            SUM(quantity) AS item_total
        FROM sales
        GROUP BY item_id
    )
)
ORDER BY total_quantity DESC
LIMIT 20;


-- ============================================================================
-- Query 11 — CTE / temporary analytical result
-- Question:
-- Which stores were responsible for the greatest monthly demand?
-- ============================================================================

WITH monthly_store_demand AS (
    SELECT
        substr(date, 1, 7) AS sales_month,
        store_id,
        SUM(quantity) AS total_quantity
    FROM sales
    GROUP BY
        sales_month,
        store_id
)
SELECT
    sales_month,
    store_id,
    total_quantity
FROM monthly_store_demand
ORDER BY
    sales_month,
    total_quantity DESC;


-- ============================================================================
-- Query 12 — Daily demand pattern
-- Question:
-- How does demand change over time?
-- ============================================================================

SELECT
    date,
    SUM(quantity) AS total_quantity,
    SUM(sum_total) AS total_sales_value
FROM sales
GROUP BY date
ORDER BY date;


-- ============================================================================
-- Query 13 — Top items
-- Question:
-- Which items have the greatest total recorded demand?
-- ============================================================================

SELECT
    item_id,
    SUM(quantity) AS total_quantity,
    SUM(sum_total) AS total_sales_value
FROM sales
GROUP BY item_id
ORDER BY total_quantity DESC
LIMIT 20;


-- ============================================================================
-- Query 14 — Markdown analysis
-- Question:
-- What markdown activity is recorded by store?
--
-- This is descriptive/associational analysis only.
-- It does not establish that markdowns caused demand changes.
-- ============================================================================

SELECT
    store_id,
    COUNT(*) AS markdown_records,
    SUM(quantity) AS markdown_quantity,
    AVG(
        CASE
            WHEN normal_price = 0 THEN NULL
            ELSE (normal_price - price) / normal_price
        END
    ) AS average_markdown_percentage
FROM markdowns
GROUP BY store_id
ORDER BY markdown_quantity DESC;


-- ============================================================================
-- Query 15 — Markdown and demand by date
-- ============================================================================

WITH markdown_daily AS (
    SELECT
        date,
        store_id,
        SUM(quantity) AS markdown_quantity
    FROM markdowns
    GROUP BY date, store_id
),
sales_daily AS (
    SELECT
        date,
        store_id,
        SUM(quantity) AS sales_quantity
    FROM sales
    GROUP BY date, store_id
)
SELECT
    s.date,
    s.store_id,
    s.sales_quantity,
    COALESCE(m.markdown_quantity, 0) AS markdown_quantity
FROM sales_daily AS s
LEFT JOIN markdown_daily AS m
    ON s.date = m.date
    AND s.store_id = m.store_id
ORDER BY s.date, s.store_id;


-- ============================================================================
-- Query 16 — Data validation
-- Question:
-- Are there sales records that do not have a matching store?
-- ============================================================================

SELECT
    COUNT(*) AS unmatched_store_records
FROM sales AS s
LEFT JOIN stores AS st
    ON s.store_id = st.store_id
WHERE st.store_id IS NULL;


-- ============================================================================
-- Query 17 — Data validation
-- Question:
-- Are there sales records that do not have matching catalog items?
-- ============================================================================

SELECT
    COUNT(*) AS unmatched_catalog_records
FROM sales AS s
LEFT JOIN catalog AS c
    ON s.item_id = c.item_id
WHERE c.item_id IS NULL;


-- ============================================================================
-- Query 18 — Date coverage
-- ============================================================================

SELECT
    MIN(date) AS earliest_sales_date,
    MAX(date) AS latest_sales_date,
    COUNT(DISTINCT date) AS distinct_sales_dates
FROM sales;