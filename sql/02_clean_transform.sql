-- Mağaza + tarih bazlı birleştirilmiş tablo
CREATE TABLE IF NOT EXISTS sales_master AS
SELECT
    s.Store,
    s.Date,
    s.DayOfWeek,
    s.Sales,
    s.Customers,
    s.Promo,
    s.StateHoliday,
    s.SchoolHoliday,
    st.StoreType,
    st.Assortment,
    st.CompetitionDistanceFilled AS CompetitionDistance,
    st.Promo2
FROM sales_clean s
LEFT JOIN store_clean st ON s.Store = st.Store;