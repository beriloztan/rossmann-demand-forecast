import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from xgboost import XGBRegressor
import warnings
warnings.filterwarnings('ignore')

# ── Sayfa ayarları ──────────────────────────────────────────
st.set_page_config(
    page_title="Rossmann Demand Forecast",
    page_icon="🛒",
    layout="wide"
)

# ── Veritabanı bağlantısı ───────────────────────────────────
DB_PATH = r'C:\Users\beril.oztan\Desktop\rossmann-demand-forecast\data\processed\rossmann.db'

@st.cache_data  # Veriyi cache'le, her tıklamada yeniden yükleme
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM sales_features ORDER BY Store, Date", conn)
    inventory = pd.read_sql_query("SELECT * FROM inventory_recommendations", conn)
    conn.close()
    df['Date'] = pd.to_datetime(df['Date'])
    return df, inventory

@st.cache_resource  # Modeli cache'le, bir kez eğit
def train_model(df):
    features = [
        'DayOfWeek', 'Promo', 'SchoolHoliday', 'CompetitionDistance',
        'Promo2', 'Year', 'Month', 'Week', 'Quarter', 'DayOfYear',
        'IsWeekend', 'IsDecember', 'lag_7', 'lag_14', 'lag_30',
        'rolling_mean_7', 'rolling_mean_30'
    ]
    train = df[df['Date'] < '2015-06-01']
    model = XGBRegressor(
        n_estimators=500, learning_rate=0.05,
        max_depth=6, subsample=0.8,
        colsample_bytree=0.8, random_state=42,
        verbosity=0
    )
    model.fit(train[features], train['Sales'])
    return model, features

# ── Veri ve model yükle ─────────────────────────────────────
with st.spinner("Model eğitiliyor, lütfen bekleyin..."):
    df, inventory = load_data()
    model, features = train_model(df)

# ── Başlık ──────────────────────────────────────────────────
st.title("🛒 Rossmann Talep Tahmini & Stok Optimizasyonu")
st.markdown("---")

# ── Sidebar ─────────────────────────────────────────────────
st.sidebar.header("🔧 Filtreler")
store_list = sorted(df['Store'].unique())
selected_store = st.sidebar.selectbox("Mağaza Seç", store_list)

# ── Metrik kartları ─────────────────────────────────────────
store_inv = inventory[inventory['Store'] == selected_store].iloc[0]
store_data = df[df['Store'] == selected_store]

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Haftalık Sipariş Önerisi", f"{int(store_inv['WeeklyOrderQty']):,}")
col2.metric("🛡️ Güvenlik Stoğu", f"{int(store_inv['SafetyStock']):,}")
col3.metric("📈 Ort. Günlük Tahmin", f"£{store_inv['AvgPredictedSales']:,.0f}")
col4.metric("🏪 Toplam Mağaza", f"{len(store_list)}")

st.markdown("---")

# ── Satış trendi grafiği ─────────────────────────────────────
st.subheader(f"📊 Mağaza {selected_store} — Satış Trendi")

store_df = df[df['Store'] == selected_store].copy()
test_df = store_df[store_df['Date'] >= '2015-06-01'].copy()
test_df['PredictedSales'] = model.predict(test_df[features])

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=store_df['Date'], y=store_df['Sales'],
    name='Gerçek Satış', line=dict(color='steelblue', width=1.5)
))
fig.add_trace(go.Scatter(
    x=test_df['Date'], y=test_df['PredictedSales'],
    name='Tahmin', line=dict(color='orange', dash='dash', width=2)
))
fig.update_layout(
    xaxis_title="Tarih", yaxis_title="Satış (£)",
    legend=dict(x=0, y=1), height=400
)
st.plotly_chart(fig, use_container_width=True)

# ── Stok önerisi tablosu ────────────────────────────────────
st.markdown("---")
st.subheader("🏭 Tüm Mağazalar — Stok Önerisi")

display_inv = inventory[['Store', 'AvgPredictedSales', 'SafetyStock', 'WeeklyOrderQty']].copy()
display_inv.columns = ['Mağaza', 'Ort. Günlük Tahmin (£)', 'Güvenlik Stoğu', 'Haftalık Sipariş']
display_inv = display_inv.round(0).astype({'Güvenlik Stoğu': int, 'Haftalık Sipariş': int})

st.dataframe(display_inv, use_container_width=True, height=400)

# ── ROI hesaplayıcı ─────────────────────────────────────────
st.markdown("---")
st.subheader("💰 ROI Hesaplayıcı")
st.markdown("Fazla stok maliyetini ne kadar azaltabiliriz?")

col1, col2 = st.columns(2)
with col1:
    current_overstock = st.slider("Mevcut fazla stok oranı (%)", 5, 50, 20)
    unit_cost = st.slider("Birim stok maliyeti (£)", 1, 50, 10)
with col2:
    avg_weekly = int(inventory['WeeklyOrderQty'].mean())
    overstock_cost = avg_weekly * (current_overstock / 100) * unit_cost
    optimized_cost = avg_weekly * 0.05 * unit_cost  # Model ile %5'e düşür
    savings = overstock_cost - optimized_cost

    st.metric("📉 Mevcut Fazla Stok Maliyeti", f"£{overstock_cost:,.0f}/hafta")
    st.metric("✅ Optimize Edilmiş Maliyet", f"£{optimized_cost:,.0f}/hafta")
    st.metric("💵 Tahmini Haftalık Tasarruf", f"£{savings:,.0f}", delta=f"-{current_overstock-5}%")