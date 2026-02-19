# ai_sql_generator.py

from datetime import datetime, timedelta


# ===================== SCHEMA UNDERSTANDING =====================
TABLE_NAME = "sales"

COLUMNS = {
    "customer": "customer_name",
    "name": "customer_name",
    "region": "region",
    "category": "category",
    "product": "product",
    "date": "order_date"
}

# metric mapping (important fix)
METRICS = {
    "sales": "SUM(price * quantity)",
    "revenue": "SUM(price * quantity)",
    "amount": "SUM(price * quantity)",
    "orders": "COUNT(order_id)",
    "quantity": "SUM(quantity)"
}


# ===================== INTENT DETECTION =====================
def detect_intent(q):
    q = q.lower()

    if "trend" in q or "over time" in q:
        return "time_series"

    if "top" in q or "highest" in q or "best" in q:
        return "ranking"

    if "average" in q or "avg" in q:
        return "average"

    return "aggregation"


# ===================== METRIC EXTRACTION =====================
def extract_metric(q):
    for key in METRICS:
        if key in q:
            return METRICS[key], key + "_value"

    return "COUNT(*)", "count"


# ===================== DIMENSION EXTRACTION =====================
def extract_dimension(q):
    for key in COLUMNS:
        if key in q:
            return COLUMNS[key]
    return None


# ===================== TIME FILTER =====================
def extract_time_filter(q):
    q = q.lower()
    today = datetime.today()

    if "last month" in q:
        first = today.replace(day=1) - timedelta(days=1)
        start = first.replace(day=1).strftime("%Y-%m-%d")
        end = first.strftime("%Y-%m-%d")
        return f"WHERE order_date BETWEEN '{start}' AND '{end}'"

    if "this year" in q:
        year = today.year
        return f"WHERE EXTRACT(YEAR FROM order_date) = {year}"

    if "2024" in q:
        return "WHERE EXTRACT(YEAR FROM order_date) = 2024"

    return ""


# ===================== SQL GENERATOR =====================
def generate_sql(question: str):

    q = question.lower()

    intent = detect_intent(q)
    metric, metric_name = extract_metric(q)
    dimension = extract_dimension(q)
    time_filter = extract_time_filter(q)

    # ---------- AGGREGATION ----------
    if intent == "aggregation":

        if dimension:
            return f"""
SELECT {dimension}, {metric} AS {metric_name}
FROM {TABLE_NAME}
{time_filter}
GROUP BY {dimension}
ORDER BY {metric_name} DESC;
"""

        else:
            return f"""
SELECT {metric} AS {metric_name}
FROM {TABLE_NAME}
{time_filter};
"""

    # ---------- TOP / RANKING ----------
    if intent == "ranking":

        dimension = dimension or "product"

        return f"""
SELECT {dimension}, {metric} AS {metric_name}
FROM {TABLE_NAME}
{time_filter}
GROUP BY {dimension}
ORDER BY {metric_name} DESC
LIMIT 5;
"""

    # ---------- TREND ----------
    if intent == "time_series":

        return f"""
SELECT order_date, {metric} AS {metric_name}
FROM {TABLE_NAME}
{time_filter}
GROUP BY order_date
ORDER BY order_date;
"""

    # ---------- AVERAGE ----------
    if intent == "average":

        return f"""
SELECT AVG(price * quantity) AS avg_order_value
FROM {TABLE_NAME}
{time_filter};
"""
