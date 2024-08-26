import psycopg2
import json
import pandas as pd

with open("config.json", "r") as f:
    config = json.load(f)

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=config["DB_NAME"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
            host=config["DB_HOST"],
            port=config["DB_PORT"]
        )
        return conn
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def select_table(table_name):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()

    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"ERROR: Could not retrieve data from {table_name}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def check_missing_values(df, table_name):
    missing_count = df.isnull().sum()
    total_missing = missing_count.sum()

    total_rows = len(df)
    missing_perc = (missing_count / total_rows) * 100

    rows_with_missing = df[df.isnull().any(axis=1)]

    result = (
        f"Table Name: {table_name}\n"
        f"Total Missing: {total_missing}\n"
        f"Missing Percentage:\n{missing_perc}\n"
        f"Total Rows: {total_rows}\n"
        f"Rows with Missing Values:\n{rows_with_missing}"
    )
    return result