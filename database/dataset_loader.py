import snowflake.connector
import pandas as pd
from config import *

def upload_dataframe_to_snowflake(df, table_name="uploaded_data"):

    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    cursor = conn.cursor()

    # Create table
    columns = df.columns

    create_cols = ", ".join([f"{col} STRING" for col in columns])

    create_query = f"""
    CREATE OR REPLACE TEMP TABLE {table_name} (
        {create_cols}
    )
    """

    cursor.execute(create_query)

    # Insert rows
    for _, row in df.iterrows():

        values = "', '".join(str(v) for v in row)

        insert_query = f"""
        INSERT INTO {table_name}
        VALUES ('{values}')
        """

        cursor.execute(insert_query)

    conn.commit()
    cursor.close()
    conn.close()

    return table_name
