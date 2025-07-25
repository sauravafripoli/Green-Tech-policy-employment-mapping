import marimo

__generated_with = "0.14.10"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    return np, pd, plt


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
        plt.xlabel('Count of Policy classes addressed')
        plt.ylabel('Policy Class')
        plt.legend(title='Region', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

    def plot_policy_classes_by_region():
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))
        axes = axes.flatten()

        for i, (region, counts) in enumerate(top_policy_classes_per_region.items()):
            counts.plot(kind='barh', ax=axes[i], title=f'Top Policy Classes in {region}')
            axes[i].set_xlabel('Number of Focus areas')
            axes[i].set_ylabel('Policy Class')
            axes[i].invert_yaxis()  # Invert y-axis for better readability

        plt.tight_layout()
        plt.show()

    plot_policy_classes_by_region()
    plot_top_policy_classes()

    return


@app.cell
def _(plt, top_focus_areas_df, top_focus_areas_per_region):
    # # plotting the top 10 focus areas graphs for all regions in percentage

    def plot_top_focus_areas1():
        top_focus_areas_df.plot(kind='barh', figsize=(12, 8), stacked=True)
        plt.title('Top 10 Focus Areas by Region')
        plt.xlabel('Count of Focus areas')
        plt.ylabel('Focus Area')
        plt.legend(title='Region', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

    def plot_top_focus_areas_by_region():
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))
        axes = axes.flatten()

        for i, (region, counts) in enumerate(top_focus_areas_per_region.items()):
            counts.plot(kind='barh', ax=axes[i], title=f'Top Focus Areas in {region}')
            axes[i].set_xlabel('Number of Policies')
            axes[i].set_ylabel('Focus Area')
            axes[i].invert_yaxis()  # Invert y-axis for better readability

        plt.tight_layout()
        plt.show()

    plot_top_focus_areas_by_region()
    plot_top_focus_areas1()
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


@app.cell
def _(data, plt, regions):
    # plotting the countriey with least and most number of policies promoting youth employments in each region

    def plot_youth_employment_by_region():
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))
        axes = axes.flatten()

        for i, (region, countries) in enumerate(regions.items()):
            # Filter data for the current region
            region_data = data[data['Country name'].isin(countries)]

            # Count occurrences of youth employment promotion
            youth_counts = region_data['Policy promotes youth employment'].value_counts()

            # Plotting
            youth_counts.plot(kind='barh', ax=axes[i], title=f'Youth Employment Promotion in {region}')
            axes[i].set_xlabel('Number of Policies')
            axes[i].set_ylabel('Promotion Status')
            axes[i].invert_yaxis()  # Invert y-axis for better readability

        plt.tight_layout()
        plt.show()

    plot_youth_employment_by_region()


    return


@app.cell
def _(data, plt):
    # plotting the country with least and most number of policies promoting youth employments in each region

    def plot_youth_employment_by_country():
        # Count occurrences of youth employment promotion by country
        youth_counts = data['Policy promotes youth employment'].value_counts()

        # Plotting
        plt.figure(figsize=(12, 6))
        youth_counts.plot(kind='barh', title='Youth Employment Promotion by Country')
        plt.xlabel('Number of Policies')
        plt.ylabel('Country')
        plt.tight_layout()
        plt.show()

    plot_youth_employment_by_country()
    return


@app.cell
def _(data, plt):
    # country with least number of policies promoting youth employments  i.e no

    def plot_least_youth_employment_country():
        # Filter data for policies that do not promote youth employment
        no_youth_data = data[data['Policy promotes youth employment'] == 'No']

        # Count occurrences of each Country
        country_counts = no_youth_data['Country name'].value_counts()

        # Plotting
        plt.figure(figsize=(12, 6))
        country_counts.plot(kind='barh', title='Countries with Least Youth Employment Promotion')
        plt.xlabel('Number of Policies')
        plt.ylabel('Country')
        plt.tight_layout()
        plt.show()

    plot_least_youth_employment_country()

    return


@app.cell
def _(data, plt):
    # country with most youth employment policies

    def plot_most_youth_employment_country():
        # Filter data for policies that promote youth employment
        yes_youth_data = data[data['Policy promotes youth employment'] == 'Yes']

        # Count occurrences of each Country
        country_counts = yes_youth_data['Country name'].value_counts()

        # Plotting
        plt.figure(figsize=(12, 6))
        country_counts.plot(kind='barh', title='Countries with Most Youth Employment Promotion')
        plt.xlabel('Number of Policies')
        plt.ylabel('Country')
        plt.tight_layout()
        plt.show()

    plot_most_youth_employment_country()
    return


@app.cell
def _(data):
    # lets create a dictionary like country, promoptes youth employment and count yes, promiotes women employment and count yes , promotes disability employment and count yes for all countries

    def create_employment_promotion_dict():
        employment_dict = {}

        for country in data['Country name'].unique():
            country_data = data[data['Country name'] == country]

            youth_count = country_data['Policy promotes youth employment'].value_counts().get('Yes', 0)

            women_count = country_data['Policy promotes women employment'].value_counts().get('Yes', 0)

            disability_count = country_data['policy promotes employment of people with disabilities'].value_counts().get('Yes', 0)

            employment_dict[country] = {
                'Youth Employment Count': youth_count,
                'Women Employment Count': women_count,
                'Disability Employment Count': disability_count
            }

            return employment_dict

    employment_promotion_dict = create_employment_promotion_dict()
    employment_promotion_dict




    return


@app.cell
def _():
    # employment columns 

    employment_columns = [
        'Policy promotes youth employment',
        'Policy promotes women employment',
        'policy promotes employment of people with disabilities'
    ]

    return (employment_columns,)


@app.cell
def _(data, employment_columns):
    # Initialize an empty dictionary to store the results
    country_employment_counts = {}

    # Group by 'Country name' and iterate through each group
    for country_name, group in data.groupby('Country name'):
        # Initialize a dictionary for the current country's counts
        country_counts = {}
        for col in employment_columns:
            # Count 'Yes' occurrences in the current column for the current country's group
            # Using .str.strip() to handle potential leading/trailing spaces if any
            yes_count = (group[col].astype(str).str.strip().str.lower() == 'yes').sum()
            country_counts[col] = yes_count
        # Add the country's counts to the main dictionary
        country_employment_counts[country_name] = country_counts

    # Print the resulting dictionary
    print(country_employment_counts)
    return (country_employment_counts,)


@app.function
# --- Plotting Function ---
def plot_employment_data(data_series, title, color, ax):
    """
    Plots a horizontal bar chart for employment data.

    Args:
        data_series (pd.Series): Series with country names as index and counts as values.
        title (str): Title of the plot.
        color (str): Color of the bars.
        ax (matplotlib.axes.Axes): The axes object to plot on.
    """
    ax.set_facecolor('white') # Set axes background to white
    ax.barh(data_series.index, data_series.values, color=color, height=0.7) # Adjust bar thickness
    ax.set_title(title, fontsize=14, fontweight='bold', color='black')
    ax.set_xlabel('Number of Policies Promoting Employment', fontsize=12, color='black')
    ax.set_ylabel('Country', fontsize=12, color='black')
    ax.tick_params(axis='x', rotation=0, labelsize=10, colors='black')
    ax.tick_params(axis='y', labelsize=12, colors='black')
    ax.invert_yaxis() # To have the highest value at the top of the bar chart (for 'top' plots)

    # Customize spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.grid(False) # No grid lines


@app.cell
def _(country_employment_counts, pd):
    df_counts = pd.DataFrame.from_dict(country_employment_counts, orient='index')
    df_counts.head()
    return (df_counts,)


@app.cell
def _(df_counts, employment_columns, plt):
    title_mapping = {
        'Policy promotes youth employment': 'Youth Employment',
        'Policy promotes women employment': 'Women Employment',
        'policy promotes employment of people with disabilities': 'Employment of People with Disabilities'
    }

    for col1 in employment_columns:
        # Get the clean title from the mapping
        clean_title_part = title_mapping.get(col1, col1.replace("_", " ").title())

        # Sort for Top 5
        top_5 = df_counts[col1].nlargest(5)
        # Sort for Least 5 (handling cases where there are fewer than 5 countries or all counts are zero)
        least_5 = df_counts[col1].nsmallest(5)

        # Create figure and axes for Top 5 plot
        fig_top, ax_top = plt.subplots(figsize=(10, 6))
        fig_top.patch.set_facecolor('white')
        plot_employment_data(top_5, f'Top 5 Countries Promoting {clean_title_part}', 'forestgreen', ax_top)
        plt.tight_layout()
        plt.show()

        # Create figure and axes for Least 5 plot
        if len(df_counts) > 5 or least_5.sum() > 0:
            fig_least, ax_least = plt.subplots(figsize=(10, 6))
            fig_least.patch.set_facecolor('white')
            plot_employment_data(least_5, f'Least 5 Countries Promoting {clean_title_part}', 'indianred', ax_least)
            plt.tight_layout()
            plt.show()
    return (title_mapping,)


@app.cell
def _(df_counts, employment_columns, plt, regions, title_mapping):
    # Outer loop for regions
    for region_name, countries_in_region in regions.items():
        # Filter df_counts for the current region's countries
        # Use .reindex to handle cases where a country in the list might not be in df_counts
        # and then drop NaN rows.
        regional_df_counts = df_counts.reindex(countries_in_region).dropna()

        # Skip plotting for regions with no data
        if regional_df_counts.empty:
            print(f"No data available for {region_name}. Skipping plots for this region.")
            continue

        # Inner loop for employment types
        for col_idx, col2 in enumerate(employment_columns): # Use col_idx for unique naming
            current_clean_title_part = title_mapping.get(col2, col2.replace("_", " ").title())

            # Sort for Top 5 within the current region
            top_n = min(5, len(regional_df_counts))
            top_countries_data = regional_df_counts[col2].nlargest(top_n)

            # Sort for Least 5 within the current region
            least_n = min(5, len(regional_df_counts))
            least_countries_data = regional_df_counts[col2].nsmallest(least_n)

            # --- Plot Top countries for the current employment type and region ---
            # Only plot if there's actual data (count > 0 for top, or if it's not empty)
            if not top_countries_data.empty and top_countries_data.sum() > 0:
                # Create unique figure and axes variable names
                fig_top_name = f'fig_top_{region_name.replace(" ", "_")}_{col_idx}'
                ax_top_name = f'ax_top_{region_name.replace(" ", "_")}_{col_idx}'

                exec(f'{fig_top_name}, {ax_top_name} = plt.subplots(figsize=(10, 6))')
                exec(f'{fig_top_name}.patch.set_facecolor("white")')
                exec(f'plot_employment_data(top_countries_data, f"Top {{top_n}} Countries Promoting {{current_clean_title_part}} in {region_name}", "forestgreen", {ax_top_name})')
                plt.tight_layout()
                plt.show()
                plt.close(eval(fig_top_name)) # Close the figure to free memory
            else:
                print(f"No 'Yes' policies found for {current_clean_title_part} in {region_name} for Top countries. Skipping plot.")


            # --- Plot Least countries for the current employment type and region ---
            # Only plot if there's actual data and it makes sense to show 'least'
            if not least_countries_data.empty and (least_countries_data.sum() > 0 or len(least_countries_data) > 0):
                # Add a check to avoid plotting "least" if it's identical to "top" when N < 5
                if not top_countries_data.equals(least_countries_data):
                    # Create unique figure and axes variable names
                    fig_least_name = f'fig_least_{region_name.replace(" ", "_")}_{col_idx}'
                    ax_least_name = f'ax_least_{region_name.replace(" ", "_")}_{col_idx}'

                    exec(f'{fig_least_name}, {ax_least_name} = plt.subplots(figsize=(10, 6))')
                    exec(f'{fig_least_name}.patch.set_facecolor("white")')
                    exec(f'plot_employment_data(least_countries_data, f"Least {{least_n}} Countries Promoting {{current_clean_title_part}} in {region_name}", "indianred", {ax_least_name})')
                    plt.tight_layout()
                    plt.show()
                    plt.close(eval(fig_least_name)) # Close the figure to free memory
                else:
                    print(f"Top and Least {current_clean_title_part} in {region_name} are the same (likely due to few countries). Skipping 'Least' plot.")
            else:
                print(f"No data or meaningful 'Least' policies found for {current_clean_title_part} in {region_name}. Skipping plot.")

    return


@app.cell
def _(df_counts, employment_columns, np, pd, plt, regions, title_mapping):
    # Create a DataFrame to store regional sums for each employment type
    regional_employment_sums = pd.DataFrame(index=regions.keys(), columns=employment_columns).fillna(0)

    # Populate the regional_employment_sums DataFrame
    for region_name_stacked, countries_in_region_stacked in regions.items(): # Unique loop variables
        # Filter df_counts for the current region's countries
        regional_df_stacked = df_counts.reindex(countries_in_region_stacked).dropna()
        if not regional_df_stacked.empty:
            for employment_col_stacked in employment_columns: # Unique loop variable
                regional_employment_sums.loc[region_name_stacked, employment_col_stacked] = regional_df_stacked[employment_col_stacked].sum()

    # Clean up column names for the legend
    stacked_column_names = [title_mapping.get(col, col.replace("_", " ").title()) for col in employment_columns]
    regional_employment_sums.columns = stacked_column_names

    # Sort regions by total employment promotion for better visualization (optional)
    regional_employment_sums['Total'] = regional_employment_sums.sum(axis=1)
    regional_employment_sums = regional_employment_sums.sort_values('Total', ascending=True).drop('Total', axis=1)

    # Plotting the stacked bar chart
    fig_stacked_chart, ax_stacked_chart = plt.subplots(figsize=(12, 8)) # Unique figure and axes names
    fig_stacked_chart.patch.set_facecolor('white')
    ax_stacked_chart.set_facecolor('white')

    # Define colors for each employment type in the stack
    colors = ['#4CAF50', '#FFC107', '#2196F3'] # Green for Youth, Amber for Women, Blue for Disabilities

    # Plot the stacked bars
    left_offsets = np.zeros(len(regional_employment_sums))
    for i_stacked, col_name_stacked in enumerate(stacked_column_names): # Unique loop variables
        ax_stacked_chart.barh(regional_employment_sums.index, regional_employment_sums[col_name_stacked],
                        left=left_offsets, height=0.7, color=colors[i_stacked], label=col_name_stacked)
        left_offsets += regional_employment_sums[col_name_stacked].values

    ax_stacked_chart.set_title('Regional Promotion of Youth, Women, and Disability Employment', fontsize=16, fontweight='bold', color='black')
    ax_stacked_chart.set_xlabel('Total Number of Focus areas', fontsize=12, color='black')
    ax_stacked_chart.set_ylabel('Region', fontsize=12, color='black')
    ax_stacked_chart.tick_params(axis='x', rotation=0, labelsize=10, colors='black')
    ax_stacked_chart.tick_params(axis='y', labelsize=12, colors='black')

    # Customize spines
    ax_stacked_chart.spines['top'].set_visible(False)
    ax_stacked_chart.spines['right'].set_visible(False)
    ax_stacked_chart.spines['bottom'].set_color('black')
    ax_stacked_chart.spines['left'].set_color('black')
    ax_stacked_chart.grid(False) # No grid lines

    # Add legend outside the plot area, similar to the reference image
    ax_stacked_chart.legend(title='Employment Type', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for the legend
    plt.show()
    plt.close(fig_stacked_chart) # Close the figure to free memory

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
