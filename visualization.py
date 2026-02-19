import plotly.express as px

def auto_visualize(df):

    if df.shape[1] < 2:
        return None

    col1 = df.columns[0]
    col2 = df.columns[1]

    # time series
    if "date" in col1.lower():
        return px.line(df, x=col1, y=col2, markers=True)

    # categorical
    if df[col1].dtype == "object":
        return px.bar(df, x=col1, y=col2, text_auto=True)

    # numeric comparison
    return px.scatter(df, x=col1, y=col2)
