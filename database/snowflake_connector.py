import snowflake.connector
import pandas as pd
import re
import os
from dotenv import load_dotenv

load_dotenv()


# -------------------------------
# Snowflake Connection
# -------------------------------

def get_connection():
    try:
        return snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )
    except Exception as e:
        raise Exception(f"Snowflake connection failed: {str(e)}")


# -------------------------------
# Upload DataFrame to Snowflake
# -------------------------------

def upload_dataframe(df, table_name):
    conn = get_connection()
    cursor = conn.cursor()

    df.columns = [col.strip().upper() for col in df.columns]

    columns_sql = ", ".join([f"{col} STRING" for col in df.columns])
    cursor.execute(f"CREATE OR REPLACE TABLE {table_name} ({columns_sql})")

    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

    for _, row in df.iterrows():
        cursor.execute(insert_sql, tuple(str(v) for v in row))

    conn.commit()
    cursor.close()
    conn.close()


# -------------------------------
# Convert Logical SQL → Physical SQL
# -------------------------------

def convert_logical_to_physical(sql, table_mapping):
    converted_sql = sql

    for logical, physical in table_mapping.items():
        converted_sql = re.sub(
            rf'\b{logical}\b',
            physical,
            converted_sql,
            flags=re.IGNORECASE
        )

    return converted_sql


# -------------------------------
# Execute Query
# -------------------------------

def run_query(physical_sql):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(physical_sql) #virtual warehouse cache
        df = cursor.fetch_pandas_all()
    except Exception as e:
        conn.close()
        raise Exception(f"Query execution failed: {str(e)}")

    conn.close()
    return df


# -------------------------------
# Drop Temporary Table
# -------------------------------

def drop_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.commit()
    cursor.close()
    conn.close()
