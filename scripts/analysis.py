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
        "West Africa": ["Benin", "Burkina Faso", "Cape Verde", "The Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Côte d'Ivoire", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Senegal", "Sierra Leone", "Togo"],
        "Central Africa": ["Burundi", "Cameroon", "Central African Republic", "Chad", "Democratic Republic of Congo", "Republic of Congo", "Equatorial Guinea", "Gabon", "São Tomé and Príncipe"],
        "East Africa": ["Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya", "Madagascar", "Mauritius", "Rwanda", "Seychelles", "Somalia", "South Sudan", "Tanzania", "Uganda"],
        "Southern Africa": ["Angola", "Botswana", "Eswatini", "Lesotho", "Malawi", "Mozambique", "Namibia", "South Africa", "Zambia", "Zimbabwe"],
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
def _(data, plt):
    # plotting percentage policy class distribution for  north africa

    def plot_north_africa_policy_class_distribution():
        north_africa_countries = ["Algeria", "Egypt", "Libya", "Morocco", "Sudan", "Tunisia", "Western Sahara"]
        north_africa_data = data[data['Country name'].isin(north_africa_countries)]

        # Count occurrences of each Policy class
        policy_counts = north_africa_data['Policy class'].value_counts()

        # Plotting
        plt.figure(figsize=(10, 10))
        plt.pie(policy_counts, labels=policy_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Policy Classes in North Africa')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.show()

    plot_north_africa_policy_class_distribution()
    return


@app.cell
def _(plot_policy_classes_for_region):
    plot_policy_classes_for_region("West Africa")
    return


@app.cell
def _(data, plt):
    # # plotting percentage policy class distribution for  west africa

    def plot_west_africa_policy_class_distribution():
        west_africa_countries = ["Benin", "Burkina Faso", "Cabo Verde", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Côte d'Ivoire", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Senegal", "Sierra Leone", "Togo"]
        west_africa_data = data[data['Country name'].isin(west_africa_countries)]

        # Count occurrences of each Policy class
        policy_counts = west_africa_data['Policy class'].value_counts()

        # Plotting
        plt.figure(figsize=(10, 10))
        plt.pie(policy_counts, labels=policy_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Policy Classes in West Africa')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.show()

    plot_west_africa_policy_class_distribution()
    return


@app.cell
def _(plot_policy_classes_for_region):
    plot_policy_classes_for_region("Central Africa")
    return


@app.cell
def _(data, plt):
    # # plotting percentage policy class distribution for  central africa

    def plot_central_africa_policy_class_distribution():
        central_africa_countries = ["Burundi", "Cameroon", "Central African Republic", "Chad", "Democratic Republic of Congo", "Republic of Congo", "Equatorial Guinea", "Gabon", "Sao Tome and Principe"]
        central_africa_data = data[data['Country name'].isin(central_africa_countries)]

        # Count occurrences of each Policy class
        policy_counts = central_africa_data['Policy class'].value_counts()

        # Plotting
        plt.figure(figsize=(10, 10))
        plt.pie(policy_counts, labels=policy_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Policy Classes in Central Africa')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.show()

    plot_central_africa_policy_class_distribution()
    return


@app.cell
def _(plot_policy_classes_for_region):
    plot_policy_classes_for_region("East Africa")
    return


@app.cell
def _(data, plt):
    # plotting percentage policy class distribution for  east africa

    def plot_east_africa_policy_class_distribution():
        east_africa_countries = ["Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya", "Madagascar", "Mauritius", "Rwanda", "Seychelles", "Somalia", "South Sudan", "Tanzania", "Uganda"]
        east_africa_data = data[data['Country name'].isin(east_africa_countries)]

        # Count occurrences of each Policy class
        policy_counts = east_africa_data['Policy class'].value_counts()

        # Plotting
        plt.figure(figsize=(10, 10))
        plt.pie(policy_counts, labels=policy_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Policy Classes in East Africa')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.show()

    plot_east_africa_policy_class_distribution()
    return


@app.cell
def _(plot_policy_classes_for_region):
    plot_policy_classes_for_region("Southern Africa")
    return


@app.cell
def _(data, plt):
    # # plotting percentage policy class distribution for  southern africa

    def plot_southern_africa_policy_class_distribution():
        southern_africa_countries = ["Angola", "Botswana", "Eswatini", "Lesotho", "Malawi", "Mozambique", "Namibia", "South Africa", "Zambia", "Zimbabwe"]
        southern_africa_data = data[data['Country name'].isin(southern_africa_countries)]

        # Count occurrences of each Policy class
        policy_counts = southern_africa_data['Policy class'].value_counts()

        # Plotting
        plt.figure(figsize=(10, 10))
        plt.pie(policy_counts, labels=policy_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Policy Classes in Southern Africa')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.show()

    plot_southern_africa_policy_class_distribution()
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


@app.cell
def _(data, plt):
    # lets plot top focus areas of whole continent

    def plot_top_focus_areas_continent():
        # Count occurrences of each Focus area across all regions
        focus_counts = data['Focus areas'].value_counts()

        # Get the top 10 Focus areas
        top_focus_areas = focus_counts.head(10)

        # Plotting
        top_focus_areas.plot(kind='barh', figsize=(12, 6), title='Top 10 Focus Areas in Africa')
        plt.xlabel('Number of mentions')
        plt.ylabel('Focus Area')
        plt.tight_layout()
        plt.show()

    plot_top_focus_areas_continent()
    return


@app.cell
def _(data, plt):
    # plotting top policies in africa
    def plot_top_policy_classes_continent():
        # Count occurrences of each Policy class across all regions
        policy_counts = data['Policy class'].value_counts()

        # Get the top 10 Policy classes
        top_policy_classes = policy_counts.head(10)

        # Plotting
        top_policy_classes.plot(kind='barh', figsize=(12, 6), title='Top 10 Policy Classes in Africa')
        plt.xlabel('Number of instances')
        plt.ylabel('Policy Class')
        plt.tight_layout()
        plt.show()

    plot_top_policy_classes_continent()
    return


@app.cell
def _(data, plt):
    # showing the continental data for policy class in percentage in a circle

    def plot_policy_class_distribution():
        # Count occurrences of each Policy class
        policy_counts = data['Policy class'].value_counts()

        # Plotting
        plt.figure(figsize=(10, 10))
        plt.pie(policy_counts, labels=policy_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Policy Classes in Africa')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.show()
    plot_policy_class_distribution()
    return


@app.cell
def _(data, plt):
    # top 10 focus areas that promotes youth employment

    def plot_youth_employment_focus_areas():
        # Filter data for policies that promote youth employment
        youth_data = data[data['Policy promotes youth employment'] == 'Yes']

        # Count occurrences of each Focus area in this subset
        focus_counts = youth_data['Focus areas'].value_counts()

        # Get the top 10 Focus areas
        top_focus_areas = focus_counts.head(10)

        # Plotting
        top_focus_areas.plot(kind='barh', figsize=(12, 6), title='Top 10 Focus Areas Promoting Youth Employment')
        plt.xlabel('Number of employment created')
        plt.ylabel('Focus Area')
        plt.tight_layout()
        plt.show()

    plot_youth_employment_focus_areas()
    return


@app.cell
def _(data, plt):
    #top focus areas promoting women employment

    def plot_women_employment_focus_areas():
        # Filter data for policies that promote youth employment
        youth_data = data[data['Policy promotes women employment'] == 'Yes']

        # Count occurrences of each Focus area in this subset
        focus_counts = youth_data['Focus areas'].value_counts()

        # Get the top 10 Focus areas
        top_focus_areas = focus_counts.head(10)

        # Plotting
        top_focus_areas.plot(kind='barh', figsize=(12, 6), title='Top 10 Focus Areas Promoting women Employment')
        plt.xlabel('Number of employment created')
        plt.ylabel('Focus Area')
        plt.tight_layout()
        plt.show()

    plot_women_employment_focus_areas()
    return


@app.cell
def _(data, plt):
    # top focus areas promoting disability

    def plot_disability_employment_focus_areas():
        # Filter data for policies that promote disability employment
        disability_data = data[data['policy promotes employment of people with disabilities'] == 'Yes']

        # Count occurrences of each Focus area in this subset
        focus_counts = disability_data['Focus areas'].value_counts()

        # Get the top 10 Focus areas
        top_focus_areas = focus_counts.head(10)

        # Plotting
        top_focus_areas.plot(kind='barh', figsize=(12, 6), title='Top 10 Focus Areas Promoting Disability Employment')
        plt.xlabel('Number of employment created')
        plt.ylabel('Focus Area')
        plt.tight_layout()
        plt.show()

    plot_disability_employment_focus_areas()
    return


@app.cell
def _(data, plt):
    # top focus areas that promote all 3

    def plot_combined_employment_focus_areas():
        # Filter data for policies that promote youth and women and disability
        combined_data = data[
            (data['Policy promotes youth employment'] == 'Yes') &
            (data['Policy promotes women employment'] == 'Yes') &
            (data['policy promotes employment of people with disabilities'] == 'Yes')]
        # Count occurrences of each Focus area in this subset
        focus_counts = combined_data['Focus areas'].value_counts()
        # Get the top 10 Focus areas
        top_focus_areas = focus_counts.head(10)
        # Plotting
        top_focus_areas.plot(kind='barh', figsize=(12, 6), title='Top 10 Focus Areas promoting all employments')
        plt.xlabel('Number of employment created')
        plt.ylabel('Focus Area')
        plt.tight_layout()
        plt.show()

    plot_combined_employment_focus_areas()
    return


@app.cell
def _(data, regions):
    #check which countries are missing in regional among all the countries

    len(set(data['Country name'].unique()) - set(sum(regions.values(), [])))
    


    return


@app.cell
def _(data, regions):
    #print which are missing

    missing_countries = set(data['Country name'].unique()) - set(sum(regions.values(), []))
    missing_countries
    return


if __name__ == "__main__":
    app.run()
