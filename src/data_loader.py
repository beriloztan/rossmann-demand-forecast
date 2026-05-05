import pandas as pd
import sqlite3
import os

DB_PATH = "data/processed/rossmann.db"
RAW_PATH = "data/raw"

def load_raw_data():
    train = pd.read_csv(f"{RAW_PATH}/train.csv", low_memory=False)
    store = pd.read_csv(f"{RAW_PATH}/store.csv")
    print(f"Train: {train.shape}, Store: {store.shape}")
    return train, store

def create_database(train, store):
    os.makedirs("data/processed", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    train.to_sql("sales_raw", conn, if_exists="replace", index=False)
    store.to_sql("store_info", conn, if_exists="replace", index=False)
    print(f"Veritabanı oluşturuldu: {DB_PATH}")
    conn.close()

def run_sql_file(sql_path):
    conn = sqlite3.connect(DB_PATH)
    with open(sql_path, "r") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print(f"Çalıştırıldı: {sql_path}")

def query(sql):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

if __name__ == "__main__":
    train, store = load_raw_data()
    create_database(train, store)
    run_sql_file("sql/01_create_tables.sql")
    run_sql_file("sql/02_clean_transform.sql")
    run_sql_file("sql/03_feature_queries.sql")
    
    # Kontrol
    df = query("SELECT COUNT(*) as total FROM sales_master")
    print(f"sales_master satır sayısı: {df['total'][0]}")
    
    df2 = query("SELECT StoreType, AVG(Sales) as AvgSales FROM sales_master GROUP BY StoreType")
    print(df2)
    
    print("SQL pipeline tamamlandı!")