import plotly.express as px
import pandas as pd


def auto_visualize(df):

    if df is None or df.empty:
        return None

    # Work on a copy (avoid mutating original dataframe)
    df_copy = df.copy()

    # Convert numeric safely
    for col in df_copy.columns:
        df_copy[col] = pd.to_numeric(df_copy[col], errors="ignore")

    cols = df_copy.columns
    num_cols = df_copy.select_dtypes(include=["int64", "float64"]).columns
    cat_cols = df_copy.select_dtypes(include=["object"]).columns

    # ---------------- Single Value KPI ----------------
    if df_copy.shape == (1, 1):
        return None

    # ---------------- Time Series ----------------
    for col in cols:
        if "date" in col.lower() or "time" in col.lower():
            if len(num_cols) > 0:
                return px.line(
                    df_copy,
                    x=col,
                    y=num_cols[0],
                    markers=True,
                    title="Trend Over Time"
                )

    # ---------------- Bar Chart ----------------
    if len(cat_cols) >= 1 and len(num_cols) >= 1:
        return px.bar(
            df_copy,
            x=cat_cols[0],
            y=num_cols[0],
            text_auto=True,
            title="Category Comparison"
        )

    # ---------------- Histogram ----------------
    if len(num_cols) == 1 and len(cols) == 1:
        return px.histogram(
            df_copy,
            x=num_cols[0],
            title="Distribution"
        )

    # ---------------- Scatter ----------------
    if len(num_cols) >= 2:
        return px.scatter(
            df_copy,
            x=num_cols[0],
            y=num_cols[1],
            title="Relationship Between Variables"
        )

    return None