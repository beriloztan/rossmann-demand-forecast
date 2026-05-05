-- Haftalık satış özeti (EDA için)
CREATE TABLE IF NOT EXISTS weekly_sales AS
SELECT
    Store,
    StoreType,
    strftime('%Y-%W', Date) AS YearWeek,
    SUM(Sales)              AS TotalSales,
    AVG(Sales)              AS AvgDailySales,
    SUM(Customers)          AS TotalCustomers,
    SUM(Promo)              AS PromoDays
FROM sales_master
GROUP BY Store, YearWeek;

-- Promosyon etkisi özeti
CREATE TABLE IF NOT EXISTS promo_effect AS
SELECT
    StoreType,
    Promo,
    ROUND(AVG(Sales), 2)     AS AvgSales,
    COUNT(*)                  AS DayCount
FROM sales_master
GROUP BY StoreType, Promo;