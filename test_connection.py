'''
import snowflake.connector
from config import *

try:
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    print("Snowflake connected successfully!")

    conn.close()

except Exception as e:
    print("Connection failed")
    print(e)
'''
from snowflake_connector import execute_query

df = execute_query("SELECT * FROM sales")

print(df)
