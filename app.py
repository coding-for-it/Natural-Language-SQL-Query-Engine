import streamlit as st
import pandas as pd
import uuid

from core.ai_sql_generator import (
    generate_sql,
    verify_sql,
    explain_query,
    clean_sql_display,
    apply_join_correction
)
from core.validator import validate_query, clean_sql
from core.visualization import auto_visualize
from database.snowflake_connector import upload_dataframe, run_query, drop_table, convert_logical_to_physical

st.set_page_config(page_title="AI Analytics Assistant", layout="wide")
st.title("AI-Powered Natural Language Analytics Assistant")


# ---------------------------
# SESSION INIT
# ---------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "tables" not in st.session_state:
    st.session_state.tables = {}

if "schema_text" not in st.session_state:
    st.session_state.schema_text = ""

if "last_sql" not in st.session_state:
    st.session_state.last_sql = None


# ---------------------------
# FILE UPLOAD
# ---------------------------

uploaded_files = st.file_uploader(
    "Upload Dataset",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

if uploaded_files:

    st.session_state.schema_text = ""
    st.session_state.tables = {}

    for file in uploaded_files:

        try:
            df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
        except Exception as e:
            st.error(f"File read error: {str(e)}")
            st.stop()

        df.columns = [c.lower().strip() for c in df.columns]

        logical_name = file.name.split('.')[0].upper()
        physical_name = f"{logical_name}_{st.session_state.session_id}"

        try:
            upload_dataframe(df, physical_name)
        except Exception as e:
            st.error(str(e))
            st.stop()

        st.session_state.tables[logical_name] = physical_name

        st.success(f"{file.name} uploaded successfully")

        #metadata cache
        st.session_state.schema_text += (
            f"\nTable: {logical_name}\n"
            f"Columns: {', '.join(df.columns)}\n"
        )


# ---------------------------
# QUESTION
# ---------------------------

user_question = st.text_input("Ask your business question")


if st.button("Generate Insights"):

    if not user_question:
        st.warning("Enter a question")
        st.stop()

    if not st.session_state.tables:
        st.warning("Upload a dataset first")
        st.stop()

    # 1. Generate SQL
    raw_sql = generate_sql(user_question, schema=st.session_state.schema_text)

    if not raw_sql:
        st.error("SQL generation failed.")
        st.stop()

    # 2. Apply join correction rule
    corrected_sql = apply_join_correction(user_question, raw_sql)

    # 3. Verify semantic correctness
    if not verify_sql(user_question, corrected_sql, st.session_state.schema_text):
        st.error("Generated SQL does not fully match the question intent.")
        st.stop()

    # 4. Clean
    sql_query = clean_sql(corrected_sql)

    if not validate_query(sql_query):
        st.error("Unsafe or invalid query detected.")
        st.stop()

    # 5. Convert logical → physical
    physical_sql = convert_logical_to_physical(
        sql_query,
        st.session_state.tables
    )

    # 6. Execute
    try:
        result_df = run_query(physical_sql)
    except Exception as e:
        st.error(str(e))
        st.stop()

    # 7. Display
    display_sql = clean_sql_display(corrected_sql)

    st.subheader("Generated SQL (Logical)")
    st.code(display_sql, language="sql")

    st.session_state.last_sql = display_sql

    st.subheader("Results")
    st.dataframe(result_df, use_container_width=True, hide_index=True)

    fig = auto_visualize(result_df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)


# ---------------------------
# EXPLAIN
# ---------------------------

if st.session_state.last_sql:

    if st.button("Explain Query"):
        explanation = explain_query(st.session_state.last_sql)
        st.subheader("Query Explanation")
        st.write(explanation)


# ---------------------------
# CLEAR
# ---------------------------

if st.button("Clear Session Data"):

    for physical in st.session_state.tables.values():
        drop_table(physical)

    st.session_state.tables = {}
    st.session_state.schema_text = ""
    st.session_state.last_sql = None

    st.success("All temporary tables deleted")
