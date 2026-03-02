import re


# ---------------------------------------------------
# CLEAN SQL
# ---------------------------------------------------

def clean_sql(query: str) -> str:
    """
    Remove markdown formatting and extra text
    """

    if not query:
        return ""

    # Remove markdown blocks
    query = re.sub(r"```sql", "", query, flags=re.IGNORECASE)
    query = re.sub(r"```", "", query)

    # Remove leading/trailing whitespace
    query = query.strip()

    return query


# ---------------------------------------------------
# VALIDATE QUERY
# ---------------------------------------------------

def validate_query(query: str) -> bool:
    """
    Allow ONLY safe SELECT queries.
    Block destructive or multi-statement queries.
    """

    query = clean_sql(query)

    if not query:
        return False

    q = query.upper().strip()

    #Must start with SELECT
    if not q.startswith("SELECT"):
        return False

    #Forbidden keywords
    forbidden = [
        "DELETE",
        "DROP",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "MERGE",
        "CALL",
        "CREATE",
        "REPLACE",
        "GRANT",
        "REVOKE"
    ]

    for word in forbidden:
        # Match whole word only
        if re.search(rf"\b{word}\b", q):
            return False

    #Block multiple statements
    if ";" in q[:-1]:
        return False

    #Block SQL comments (basic injection prevention)
    if "--" in q or "/*" in q or "*/" in q:
        return False

    #Block UNION-based injection attempts
    if re.search(r"\bUNION\b", q):
        return False

    #Block system access
    if re.search(r"\bINFORMATION_SCHEMA\b", q):
        return False

    return True