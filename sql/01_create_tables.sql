-- Temizlenmiş satış tablosu
CREATE TABLE IF NOT EXISTS sales_clean AS
SELECT
    Store,
    Date,
    DayOfWeek,
    Sales,
    Customers,
    Open,
    Promo,
    StateHoliday,
    SchoolHoliday
FROM sales_raw
WHERE
    Open = 1          -- Sadece açık günler
    AND Sales > 0     -- Sıfır satışlı günleri çıkar
    AND Store IS NOT NULL;

-- Mağaza bilgisi tablosu
CREATE TABLE IF NOT EXISTS store_clean AS
SELECT
    Store,
    StoreType,
    Assortment,
    CompetitionDistance,
    Promo2,
    COALESCE(CompetitionDistance, 0) AS CompetitionDistanceFilled
FROM store_info;