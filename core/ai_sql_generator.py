import os
import re
from dotenv import load_dotenv
from google import genai

# ---------------------------------------------------
# LOAD ENV
# ---------------------------------------------------

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=API_KEY)

SQL_MODEL = "gemini-2.5-flash"
VALIDATION_MODEL = "gemini-2.5-flash"

# ---------------------------------------------------
# CLEAN SQL (FOR EXECUTION)
# ---------------------------------------------------

def clean_sql(sql: str) -> str:
    sql = re.sub(r"```sql|```", "", sql, flags=re.IGNORECASE)
    return sql.strip()


# ---------------------------------------------------
# CLEAN SQL (FOR DISPLAY)
# ---------------------------------------------------

def clean_sql_display(sql: str) -> str:
    return clean_sql(sql)


# ---------------------------------------------------
# QUANTIFIER DETECTION
# ---------------------------------------------------

def contains_quantifier(question: str) -> bool:
    quantifiers = [
        "each", "every", "all", "for each",
        "including those with none",
        "even if they don't have",
        "even if they do not have"
    ]
    question = question.lower()
    return any(q in question for q in quantifiers)


# ---------------------------------------------------
# SQL GENERATION
# ---------------------------------------------------

def generate_sql(question: str, schema: str) -> str:

    prompt = f"""
You are a professional Snowflake SQL expert.

Rules:
- Only generate SELECT queries.
- NEVER generate DELETE, DROP, UPDATE, TRUNCATE.
- Carefully interpret quantifiers like each, every, all.
- If question implies full base entity set → use LEFT JOIN.
- If aggregation is implied → use GROUP BY.
- If time filter is mentioned → include WHERE clause.
- Use COUNT(column) instead of COUNT(*) when using LEFT JOIN.
- Use only tables and columns provided.
- Return only SQL. No explanation.

Database Schema:
{schema}

User Question:
{question}

Return only valid SQL.
"""

    try:
        response = client.models.generate_content(
            model=SQL_MODEL,
            contents=prompt
        )

        return clean_sql(response.text)

    except Exception as e:
        print("Generation Error:", e)
        return None


# ---------------------------------------------------
# JOIN CORRECTION RULE
# ---------------------------------------------------

def apply_join_correction(question: str, sql: str) -> str:

    if (
        contains_quantifier(question)
        and "group by" in sql.lower()
        and "count(" in sql.lower()
        and "inner join" in sql.lower()
    ):
        sql = re.sub(r"\bINNER JOIN\b", "LEFT JOIN", sql, flags=re.IGNORECASE)

    return sql


# ---------------------------------------------------
# SEMANTIC VALIDATION (LLM SELF CHECK)
# ---------------------------------------------------

def semantic_validation(question: str, sql: str, schema: str) -> str:

    prompt = f"""
You are a SQL validation expert.

Database Schema:
{schema}

User Question:
{question}

Generated SQL:
{sql}

Does this SQL fully answer the question?

If YES → return the same SQL.
If NO → return corrected SQL only.

Return only SQL.
"""

    try:
        response = client.models.generate_content(
            model=VALIDATION_MODEL,
            contents=prompt
        )

        return clean_sql(response.text)

    except Exception as e:
        print("Validation Error:", e)
        return sql


# ---------------------------------------------------
# VERIFY SQL (USED BY APP.PY)
# ---------------------------------------------------

def verify_sql(question: str, sql: str, schema: str) -> bool:
    """
    Returns True if SQL is semantically correct,
    False if correction was required.
    """

    corrected_sql = semantic_validation(question, sql, schema)

    if corrected_sql.strip().lower() == sql.strip().lower():
        return True
    else:
        return False


# ---------------------------------------------------
# EXPLAIN QUERY
# ---------------------------------------------------

def explain_query(sql_query: str) -> str:

    prompt = f"""
Explain the following Snowflake SQL query in simple business language.

SQL Query:
{sql_query}

Explain clearly step by step.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        return f"Explanation error: {str(e)}"