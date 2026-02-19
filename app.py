import streamlit as st
from ai_sql_generator import generate_sql
from snowflake_connector import execute_query
from validator import validate_query, clean_sql
from visualization import auto_visualize

st.set_page_config(page_title="AI Analytics Assistant", layout="wide")

st.title("AI-Powered Natural Language Analytics Assistant")

user_question = st.text_input("Ask your business question:")

if st.button("Generate Insights"):

    if not user_question.strip():
        st.warning("Enter a question")
        st.stop()

    raw_sql = generate_sql(user_question)

    st.subheader("Generated SQL")
    st.code(raw_sql)

    sql_query = clean_sql(raw_sql)

    if validate_query(sql_query):

        df = execute_query(sql_query)

        st.subheader("Results")
        st.dataframe(df, use_container_width=True)

        fig = auto_visualize(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Unsafe query detected")
