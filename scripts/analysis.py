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


@app.cell
def _():

    # Define the regions and their corresponding countries
    regions = {
        "North Africa": ["Algeria", "Egypt", "Libya", "Morocco", "Sudan", "Tunisia", "Western Sahara"],
        "West Africa": ["Benin", "Burkina Faso", "Cape Verde", "Gambia", "Ghana",
                        "Guinea", "Guinea-Bissau", "Ivory Coast", "Liberia", "Mali",
                        "Mauritania", "Niger", "Nigeria", "Senegal", "Sierra Leone", "Togo"],
        "Central Africa": ["Burundi", "Cameroon", "Central African Republic",
                           "Chad", "Democratic Republic of Congo",
                           "Republic of the Congo", "Equatorial Guinea",
                           "Gabon", "São Tomé and Príncipe"],
        "East Africa": ["Comoros", "Djibouti", "Eritrea", "Ethiopia",
                        "Kenya", "Madagascar", "Mauritius", "Rwanda",
                        "Seychelles", "Somalia", "South Sudan",
                        "Tanzania", "Uganda"],
        "Southern Africa": ["Angola", "Botswana", "Eswatini",
                            "Lesotho", "Malawi", "Mozambique",
                            "Namibia", "South Africa",
                            "Zambia",  "Zimbabwe"]
    }
    return (regions,)


@app.cell
def _(data, pd, regions):
    # finding the top policy classes per region with counts
    top_policy_classes_per_region = {}
    for region, countries in regions.items():
        # Filter data for the current region
        region_data = data[data['Country name'].isin(countries)]

        # Count occurrences of each Policy class
        policy_counts = region_data['Policy class'].value_counts()

        # Get the top 10 Policy classes
        top_policy_classes = policy_counts.head(10)

        # Store the results
        top_policy_classes_per_region[region] = top_policy_classes

    # Convert the results to a DataFrame for better visualization
    top_policy_classes_df = pd.DataFrame(top_policy_classes_per_region).fillna(0).astype(int).T

    top_policy_classes_df.head()
    return top_policy_classes_df, top_policy_classes_per_region


@app.cell
def _(data, pd, regions):
    def _():
        # finding top 10 focus areas per region with counts
        top_focus_areas_per_region = {}
        for region, countries in regions.items():
            # Filter data for the current region
            region_data = data[data['Country name'].isin(countries)]

            # Count occurrences of each Focus area
            focus_counts = region_data['Focus areas'].value_counts()

            # Get the top 10 Focus areas
            top_focus_areas = focus_counts.head(10)

            # Store the results
            top_focus_areas_per_region[region] = top_focus_areas

        # Convert the results to a DataFrame for better visualization
        top_focus_areas_df = pd.DataFrame(top_focus_areas_per_region).fillna(0).astype(int).T
        return top_focus_areas_df.head()


    _()
    return


@app.cell
def _(plt, top_policy_classes_df, top_policy_classes_per_region):
    # plotting the policy class graphs for all regions in percentage
    def plot_top_policy_classes():
        top_policy_classes_df.plot(kind='barh', figsize=(12, 8), stacked=True)
        plt.title('Top 10 Policy Classes by Region')
        plt.xlabel('Number of Policies')
        plt.ylabel('Policy Class')
        plt.legend(title='Region', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

    def plot_policy_classes_by_region():
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))
        axes = axes.flatten()

        for i, (region, counts) in enumerate(top_policy_classes_per_region.items()):
            counts.plot(kind='barh', ax=axes[i], title=f'Top Policy Classes in {region}')
            axes[i].set_xlabel('Number of Policies')
            axes[i].set_ylabel('Policy Class')
            axes[i].invert_yaxis()  # Invert y-axis for better readability

        plt.tight_layout()
        plt.show()

    plot_policy_classes_by_region()
    plot_top_policy_classes()

    return


@app.cell
def _(data, pd, regions):
        # finding top 10 focus areas per region with counts
    top_focus_areas_per_region = {}
    for reg, country in regions.items():
        # Filter data for the current region
        regional_data = data[data['Country name'].isin(country)]

        # Count occurrences of each Focus area
        focus_counts = regional_data['Focus areas'].value_counts()

        # Get the top 10 Focus areas
        top_focus_areas = focus_counts.head(10)

        # Store the results
        top_focus_areas_per_region[reg] = top_focus_areas

    # Convert the results to a DataFrame for better visualization
    top_focus_areas_df = pd.DataFrame(top_focus_areas_per_region).fillna(0).astype(int).T

    top_focus_areas_df.head()
    return top_focus_areas_df, top_focus_areas_per_region


@app.cell
def _(plt, top_focus_areas_df, top_focus_areas_per_region):
    # potting the focus areas graphs for all regions in percentage

    def plot_top_focus_areas():
        top_focus_areas_df.plot(kind='barh', figsize=(12, 8), stacked=True)
        plt.title('Top 10 Focus Areas by Region')
        plt.xlabel('Number of Policies')
        plt.ylabel('Focus Area')
        plt.legend(title='Region', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

    def plot_focus_areas_by_region():
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))
        axes = axes.flatten()

        for i, (region, counts) in enumerate(top_focus_areas_per_region.items()):
            counts.plot(kind='barh', ax=axes[i], title=f'Top Focus Areas in {region}')
            axes[i].set_xlabel('Number of Policies')
            axes[i].set_ylabel('Focus Area')
            axes[i].invert_yaxis()  # Invert y-axis for better readability

        plt.tight_layout()
        plt.show()

    plot_focus_areas_by_region()
    return


@app.cell
def _(plt, top_policy_classes_per_region):
    #plotting the policy classes graphs for all regions one by one
    def plot_policy_classes_for_region(region):
        if region in top_policy_classes_per_region:
            counts = top_policy_classes_per_region[region]
            counts.plot(kind='barh', figsize=(12, 6), title=f'Top Policy Classes in {region}')
            plt.xlabel('Number of Policies')
            plt.ylabel('Policy Class')
            plt.tight_layout()
            plt.show()
        else:
            print(f"No data available for region: {region}")


    return (plot_policy_classes_for_region,)


@app.cell
def _(plot_policy_classes_for_region):
    # Example usage:
    plot_policy_classes_for_region("North Africa")
    return


@app.cell
def _(plot_policy_classes_for_region):
    plot_policy_classes_for_region("West Africa")
    return


@app.cell
def _(plot_policy_classes_for_region):
    plot_policy_classes_for_region("Central Africa")
    return


@app.cell
def _(plot_policy_classes_for_region):
    plot_policy_classes_for_region("East Africa")
    return


@app.cell
def _(plot_policy_classes_for_region):
    plot_policy_classes_for_region("Southern Africa")
    return


@app.cell
def _(plt, top_focus_areas_per_region):
    # Plotting focus areas for all regions one by one

    def plot_focus_areas_for_region(region):
        if region in top_focus_areas_per_region:
            counts = top_focus_areas_per_region[region]
            counts.plot(kind='barh', figsize=(12, 6), title=f'Top Focus Areas in {region}')
            plt.xlabel('Number of Policies')
            plt.ylabel('Focus Area')
            plt.tight_layout()
            plt.show()
        else:
            print(f"No data available for region: {region}")

    # Example usage:
    plot_focus_areas_for_region("North Africa")
    return (plot_focus_areas_for_region,)


@app.cell
def _(plot_focus_areas_for_region):
    plot_focus_areas_for_region("East Africa")
    return


@app.cell
def _(plot_focus_areas_for_region):
    plot_focus_areas_for_region("West Africa")
    return


@app.cell
def _(plot_focus_areas_for_region):
    plot_focus_areas_for_region("Southern Africa")
    return


@app.cell
def _(plot_focus_areas_for_region):
    plot_focus_areas_for_region("Central Africa")
    return


if __name__ == "__main__":
    app.run()
