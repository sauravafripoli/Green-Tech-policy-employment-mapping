import marimo

__generated_with = "0.14.10"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    return pd, plt


@app.cell
def _(pd):
    df = pd.read_csv('../data/Wilma-climate tech policies.csv')
    df
    return (df,)


@app.cell
def _(df):
    # finding the number of unique values in each column
    unique_counts = df.nunique()
    unique_counts
    return


@app.cell
def _(df):
    # removing the last 2 unnamed columns
    data  = df.iloc[:, :-2]
    data
    return (data,)


@app.cell
def _(df):
    # value counts for key features
    # Value counts for key features
    print("Green Tech Targeting:")
    print(df['Policy targets green technology'].value_counts(dropna=False))

    print("\nFocus Areas (Top 10):")
    print(df['Focus areas'].value_counts(dropna=False).head(10))

    print("\nAction or Strategy:")
    print(df['action or strategy'].value_counts(dropna=False))

    print("\nYouth Employment Promotion:")
    print(df['Policy promotes youth employment'].value_counts(dropna=False))

    print("\nWomen Employment Promotion:")
    print(df['Policy promotes women employment'].value_counts(dropna=False))

    print("\nDisability Employment Promotion:")
    print(df['policy promotes employment of people with disabilities'].value_counts(dropna=False))
    return


@app.cell
def _(data, plt):
    # Policies per Country
    data['Country name'].value_counts().head(10).plot(kind='barh', figsize=(10,5), title='Top 10 Countries by Number of Policies')
    plt.xlabel("Number of Policies")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(data):
    import altair as alt
    _chart = (
        alt.Chart(data)
        .mark_bar()
        .transform_aggregate(count="count()", groupby=["Policy class"])
        .transform_window(
            rank="rank()",
            sort=[
                alt.SortField("count", order="descending"),
                alt.SortField("Policy class", order="ascending"),
            ],
        )
        .transform_filter(alt.datum.rank <= 10)
        .encode(
            y=alt.Y(
                "Policy class:N",
                sort="-x",
                axis=alt.Axis(title=None),
            ),
            x=alt.X("count:Q", title="Number of records"),
            tooltip=[
                alt.Tooltip("Policy class:N"),
                alt.Tooltip("count:Q", format=",.0f", title="Number of records"),
            ],
        )
        .properties(title="Top 10 {column}", width="container")
        .configure_view(stroke=None)
        .configure_axis(grid=False)
    )
    _chart
    return


@app.cell
def _(data):
    #count of focus areas per country
    focus_areas_per_country = (
        data.groupby('Country name')['Focus areas']
        .apply(lambda x: ', '.join(x.dropna().unique()))
        .reset_index()
    )
    focus_areas_per_country

    return


@app.cell
def _(data):

    # lis of policy class per country
    policy_class_per_country = (
        data.groupby('Country name')['Policy class']
        .apply(lambda x: ', '.join(x.dropna().unique()))
        .reset_index()
    )

    policy_class_per_country
    return


@app.cell
def _(data):
    # counting the number of unique focus areas per country
    unique_focus_areas_per_country = (
        data.groupby('Country name')['Focus areas']
        .nunique()
        .reset_index(name='Unique Focus Areas Count')
    )
    unique_focus_areas_per_country

    return


@app.cell
def _(data):
    #counting the number of unique policy classes per country
    unique_policy_classes_per_country = (
        data.groupby('Country name')['Policy class']
        .nunique()
        .reset_index(name='Unique Policy Classes Count')
    )

    unique_policy_classes_per_country
    return


@app.cell
def _(data):
    data.columns
    return


@app.cell
def _(data):


    # Group all rows per country and aggregate data into lists (not unique counts)
    grouped = data.groupby("Country name").agg({
        "Focus areas": lambda x: list(x.dropna()),
        "Policy class": lambda x: list(x.dropna()),
        "Government document": lambda x: list(x.dropna()),
        "Policy targets green technology": lambda x: list(x.dropna()),
        "action or strategy": lambda x: list(x.dropna()),
        "Policy promotes youth employment": lambda x: list(x.dropna()),
        "Policy promotes women employment": lambda x: list(x.dropna()),
        "policy promotes employment of people with disabilities": lambda x: list(x.dropna())
    }).reset_index()


    return (grouped,)


@app.cell
def _(grouped):
    # Rename the key for consistency with frontend (optional)
    grouped_data = grouped.rename(columns={"Country name": "country"})

    # Save to JSON as an array of records (VALID JSON for D3/Flask)
    grouped_data.to_json("../data/africa_policy_data.json", orient="records", indent=2)

    return


if __name__ == "__main__":
    app.run()
