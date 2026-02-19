import re

def clean_sql(query: str) -> str:
    query = query.strip()
    query = re.sub(r"```sql", "", query, flags=re.IGNORECASE)
    query = query.replace("```", "")
    return query.strip()


def validate_query(query: str) -> bool:

    query = clean_sql(query)
    q = query.upper()

    if not q.startswith("SELECT"):
        return False

    forbidden = [
        "DELETE","DROP","UPDATE","INSERT",
        "ALTER","TRUNCATE","MERGE","CALL",
        "CREATE","REPLACE"
    ]

    for word in forbidden:
        if word in q:
            return False

    if ";" in q[:-1]:
        return False

    if "--" in q or "/*" in q:
        return False

    return True
