import snowflake.connector
import pandas as pd
from config import *

def execute_query(query):

    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    cursor = conn.cursor()

    try:
        cursor.execute(query)
        df = cursor.fetch_pandas_all()
        return df

    except Exception as e:
        print("Error:", e)
        return pd.DataFrame()

    finally:
        cursor.close()
        conn.close()
