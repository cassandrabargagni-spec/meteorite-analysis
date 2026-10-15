import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from offlineRevGeocoder import get

# Find the CSV file inside the same folder as this Python file
project_folder = Path(__file__).parent
file_path = project_folder / "meteorite_landings.csv"

# Read the meteorite dataset
data = pd.read_csv(file_path)

# Show the first 5 meteorites
print("First five rows:")
print(data.head())

# Show the names of all columns
print("\nColumns:")
print(data.columns)

# Show the size of the dataset
print("\nNumber of meteorites:")
print(len(data))

# Show basic information
print("\nDataset information:")
data.info()


# Function for the uncertainty of a percentage
# p = percentage, n = number of meteorites in the group
# formula: sqrt(p * (1 - p) / n), with p as a fraction between 0 and 1
def percentage_uncertainty(percentage, n):
    p = percentage / 100
    return np.sqrt(p * (1 - p) / n) * 100


# Plot 1: Number of Fell vs Found meteorites

# Count how many meteorites were Fell or Found
fall_counts = data["fall"].value_counts()

print("\nFell vs Found:")
print(fall_counts)

# Calculate percentages
total = fall_counts.sum()
fall_percentage = fall_counts / total * 100

# Uncertainty of the percentages
fall_error = percentage_uncertainty(fall_percentage, total)

# The same uncertainty but in number of meteorites
count_error = fall_error / 100 * total

print("\nPercentage with uncertainty:")
for category in fall_counts.index:
    print(category, round(fall_percentage[category], 1), "+/-", round(fall_error[category], 2), "%")

# Create a bigger figure
fig, ax = plt.subplots(figsize=(9, 7))

# Create bar chart
fall_counts.plot(kind="bar", ax=ax)

plt.title(
    "Number of Meteorites Observed Falling vs Found Later",
    pad=20
)

plt.xlabel("Category")
plt.ylabel("Number of meteorites")
plt.xticks(rotation=0)

# Add the number and the percentage with their uncertainty above each bar
# (the error is too small to see as an error bar, so I only write it in the label)
for bar, count, error, percentage, perc_error in zip(
    ax.patches,
    fall_counts.values,
    count_error.values,
    fall_percentage.values,
    fall_error.values
):

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{count:,} ± {error:.0f}\n({percentage:.1f} ± {perc_error:.1f}%)",
        ha="center",
        va="bottom"
    )

# Add a dashed line at the number of Fell meteorites
fell_number = fall_counts["Fell"]

plt.axhline(
    y=fell_number,
    linestyle="--",
    linewidth=1
)

# Add extra space above the tallest bar
plt.ylim(0, fall_counts.max() * 1.18)

plt.tight_layout()
plt.show()

# Plot 2: Median mass - Fell vs Found

# Keep only meteorites with a recorded positive mass
mass_comparison = data.dropna(subset=["mass (g)"])
mass_comparison = mass_comparison[mass_comparison["mass (g)"] > 0]

# Calculate median mass for Fell and Found meteorites
median_mass = mass_comparison.groupby("fall")["mass (g)"].median()
median_mass = median_mass.reindex(["Found", "Fell"])

print("\nMedian mass of Fell and Found meteorites:")
print(median_mass)

# Create figure
fig, ax = plt.subplots(figsize=(9, 7))

# Create bar chart
median_mass.plot(kind="bar", ax=ax)

plt.title("Median Mass of Fell vs Found Meteorites", pad=20)
plt.xlabel("Category")
plt.ylabel("Median mass (g)")
plt.xticks(rotation=0)

# Add the exact mass above each bar
for bar, value in zip(ax.patches, median_mass.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:,.1f} g",
        ha="center",
        va="bottom"
    )

# Add some space above the tallest bar
plt.ylim(0, median_mass.max() * 1.20)

plt.tight_layout()
plt.show()

# Plot 3: Found vs Fell meteorites by continent

# CLEAN LOCATION DATA

# Remove meteorites without latitude or longitude
continent_data = data.dropna(
    subset=["reclat", "reclong"]
).copy()

# Keep only valid coordinates
continent_data = continent_data[
    (continent_data["reclat"] >= -90) &
    (continent_data["reclat"] <= 90) &
    (continent_data["reclong"] >= -180) &
    (continent_data["reclong"] <= 180)
]

# Remove the invalid / suspicious coordinate (0, 0)
continent_data = continent_data[
    ~(
        (continent_data["reclat"] == 0) &
        (continent_data["reclong"] == 0)
    )
]

# Keep only Found and Fell meteorites
continent_data = continent_data[
    continent_data["fall"].isin(["Found", "Fell"])
].copy()


# FIND THE CONTINENT

# Store locations we already checked
# so Python does not calculate them again
location_cache = {}

continents = []

for latitude, longitude in zip(
    continent_data["reclat"],
    continent_data["reclong"]
):

    # Round coordinates slightly
    coordinates = (
        round(latitude, 3),
        round(longitude, 3)
    )

    # Only calculate the continent if
    # this location has not already been checked
    if coordinates not in location_cache:

        place = get(
            coordinates[0],
            coordinates[1]
        )

        location_cache[coordinates] = place.continent

    continents.append(
        location_cache[coordinates]
    )


# Add continent as a new column
continent_data["continent"] = continents

# Remove rows where the continent could not be identified
continent_data = continent_data.dropna(
    subset=["continent"]
)

# FOUND METEORITES

found_data = continent_data[
    continent_data["fall"] == "Found"
]

# Calculate percentage of Found meteorites
# belonging to each continent
found_percentage = (
    found_data["continent"]
    .value_counts(normalize=True)
    .mul(100)
    .sort_values(ascending=False)
)


# FELL METEORITES

fell_data = continent_data[
    continent_data["fall"] == "Fell"
]

# Calculate percentage of Fell meteorites
# belonging to each continent
fell_percentage = (
    fell_data["continent"]
    .value_counts(normalize=True)
    .mul(100)
)


# Put continents in the same order
# for both graphs
continent_order = found_percentage.index

fell_percentage = fell_percentage.reindex(
    continent_order,
    fill_value=0
)

# Uncertainty of each percentage
# n is the number of meteorites in the group that have a continent
found_error = percentage_uncertainty(found_percentage, len(found_data))
fell_error = percentage_uncertainty(fell_percentage, len(fell_data))


# Print results in terminal
print("\nNumber of Found / Fell meteorites with a continent:")
print(len(found_data), "/", len(fell_data))

print("\nFound meteorites by continent (% and uncertainty):")
print(pd.DataFrame({"percentage": found_percentage, "uncertainty": found_error}).round(2))

print("\nFell meteorites by continent (% and uncertainty):")
print(pd.DataFrame({"percentage": fell_percentage, "uncertainty": fell_error}).round(2))

# CREATE SIDE-BY-SIDE GRAPHS

# Use the same y-axis scale for both
# (include the error bars so the labels still fit)
max_percentage = max(
    (found_percentage + found_error).max(),
    (fell_percentage + fell_error).max()
) * 1.15

# Create two graphs next to each other
fig, (ax1, ax2) = plt.subplots(
    1,
    2,
    figsize=(16, 7),
    sharey=True
)


# LEFT GRAPH: FOUND

bars1 = ax1.bar(
    found_percentage.index,
    found_percentage.values,
    yerr=found_error.values,
    capsize=4
)

ax1.set_title(
    "Found Meteorites",
    pad=20
)

ax1.set_xlabel("Continent")

ax1.set_ylabel(
    "Percentage of meteorites (%)"
)

ax1.tick_params(
    axis="x",
    rotation=25
)

ax1.set_ylim(
    0,
    max_percentage
)

# Add exact percentage above each bar
# (above the error bar, so they don't overlap)
for bar, percentage, error in zip(
    bars1,
    found_percentage.values,
    found_error.values
):

    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + error,
        f"{percentage:.1f}%",
        ha="center",
        va="bottom"
    )

# RIGHT GRAPH: FELL

bars2 = ax2.bar(
    fell_percentage.index,
    fell_percentage.values,
    yerr=fell_error.values,
    capsize=4
)

ax2.set_title(
    "Fell Meteorites",
    pad=20
)

ax2.set_xlabel("Continent")

ax2.tick_params(
    axis="x",
    rotation=25
)

ax2.set_ylim(
    0,
    max_percentage
)

# Add exact percentage above each bar
for bar, percentage, error in zip(
    bars2,
    fell_percentage.values,
    fell_error.values
):

    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + error,
        f"{percentage:.1f}%",
        ha="center",
        va="bottom"
    )


# MAIN TITLE
fig.suptitle(
    "Found vs Fell Meteorites by Continent",
    fontsize=16
)

plt.tight_layout()

# Save the graph for the report
plt.savefig(project_folder / "plot_continents.png", dpi=200, bbox_inches="tight")

plt.show()

# Plot 4: Top 6 meteorite classes Found vs Fell

# Keep only rows with a meteorite class
class_data = data.dropna(subset=["recclass"]).copy()

# Keep only Found and Fell
class_data = class_data[
    class_data["fall"].isin(["Found", "Fell"])
]

# Find the 6 most common meteorite classes overall
top_classes = (
    class_data["recclass"]
    .value_counts()
    .head(6)
    .index
)

# Keep only those 6 classes
class_data = class_data[
    class_data["recclass"].isin(top_classes)
]

# Total number of Found and Fell meteorites
total_found = len(
    data[data["fall"] == "Found"]
)

total_fell = len(
    data[data["fall"] == "Fell"]
)

# Percentage of all Found meteorites in each class
found_classes = (
    class_data[
        class_data["fall"] == "Found"
    ]["recclass"]
    .value_counts()
    .reindex(top_classes, fill_value=0)
    / total_found
    * 100
)

# Percentage of all Fell meteorites in each class
fell_classes = (
    class_data[
        class_data["fall"] == "Fell"
    ]["recclass"]
    .value_counts()
    .reindex(top_classes, fill_value=0)
    / total_fell
    * 100
)

# Uncertainty of each percentage
found_classes_error = percentage_uncertainty(found_classes, total_found)
fell_classes_error = percentage_uncertainty(fell_classes, total_fell)

print("\nTop 6 classes, Found (% and uncertainty):")
print(pd.DataFrame({"percentage": found_classes, "uncertainty": found_classes_error}).round(2))

print("\nTop 6 classes, Fell (% and uncertainty):")
print(pd.DataFrame({"percentage": fell_classes, "uncertainty": fell_classes_error}).round(2))

# Position of the bars
x = np.arange(len(top_classes))

width = 0.38

fig, ax = plt.subplots(figsize=(11, 7))

# Found bars
bars_found = ax.bar(
    x - width / 2,
    found_classes.values,
    width,
    yerr=found_classes_error.values,
    capsize=4,
    label="Found"
)

# Fell bars
bars_fell = ax.bar(
    x + width / 2,
    fell_classes.values,
    width,
    yerr=fell_classes_error.values,
    capsize=4,
    label="Fell"
)

# Titles and labels
ax.set_title(
    "Top 6 Meteorite Classes: Found vs Fell",
    pad=20
)

ax.set_xlabel("Meteorite class")
ax.set_ylabel("Percentage of meteorites (%)")

ax.set_xticks(x)
ax.set_xticklabels(
    top_classes,
    rotation=0
)

ax.legend()

# Add percentages above Found bars
for bar, percentage, error in zip(
    bars_found,
    found_classes.values,
    found_classes_error.values
):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + error,
        f"{percentage:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9
    )

# Add percentages above Fell bars
for bar, percentage, error in zip(
    bars_fell,
    fell_classes.values,
    fell_classes_error.values
):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + error,
        f"{percentage:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9
    )

# Leave some space above the tallest bar (with its error bar)
max_value = max(
    (found_classes + found_classes_error).max(),
    (fell_classes + fell_classes_error).max()
)

ax.set_ylim(
    0,
    max_value * 1.18
)

plt.tight_layout()
plt.show()

# Plot 5: Mass categories Found vs Fell

# Keep meteorites with a valid positive mass
mass_category_data = data.dropna(
    subset=["mass (g)"]
).copy()

mass_category_data = mass_category_data[
    mass_category_data["mass (g)"] > 0
]

# Keep only Found and Fell meteorites
mass_category_data = mass_category_data[
    mass_category_data["fall"].isin(["Found", "Fell"])
]

# Define mass categories
bins = [
    0,
    10,
    100,
    1000,
    10000,
    float("inf")
]

labels = [
    "< 10 g",
    "10–100 g",
    "100 g–1 kg",
    "1–10 kg",
    "> 10 kg"
]

# Put each meteorite into a mass category
mass_category_data["mass_category"] = pd.cut(
    mass_category_data["mass (g)"],
    bins=bins,
    labels=labels,
    right=False
)

# FOUND percentages
found_mass = mass_category_data[
    mass_category_data["fall"] == "Found"
]

found_mass_percentage = (
    found_mass["mass_category"]
    .value_counts(normalize=True)
    .reindex(labels, fill_value=0)
    .mul(100)
)

# FELL percentages

fell_mass = mass_category_data[
    mass_category_data["fall"] == "Fell"
]

fell_mass_percentage = (
    fell_mass["mass_category"]
    .value_counts(normalize=True)
    .reindex(labels, fill_value=0)
    .mul(100)
)

# Uncertainty of each percentage
# n is the number of meteorites in the group that have a mass
found_mass_error = percentage_uncertainty(found_mass_percentage, len(found_mass))
fell_mass_error = percentage_uncertainty(fell_mass_percentage, len(fell_mass))

print("\nNumber of Found / Fell meteorites with a mass:")
print(len(found_mass), "/", len(fell_mass))

print("\nFound meteorites by mass range (% and uncertainty):")
print(pd.DataFrame({"percentage": found_mass_percentage, "uncertainty": found_mass_error}).round(2))

print("\nFell meteorites by mass range (% and uncertainty):")
print(pd.DataFrame({"percentage": fell_mass_percentage, "uncertainty": fell_mass_error}).round(2))

# Create grouped bar chart

x = np.arange(len(labels))

width = 0.38

fig, ax = plt.subplots(
    figsize=(11, 7)
)

bars_found = ax.bar(
    x - width / 2,
    found_mass_percentage.values,
    width,
    yerr=found_mass_error.values,
    capsize=4,
    label="Found"
)

bars_fell = ax.bar(
    x + width / 2,
    fell_mass_percentage.values,
    width,
    yerr=fell_mass_error.values,
    capsize=4,
    label="Fell"
)

ax.set_title(
    "Mass Distribution of Found vs Fell Meteorites",
    pad=20
)

ax.set_xlabel("Mass range")

ax.set_ylabel(
    "Percentage of meteorites (%)"
)

ax.set_xticks(x)

ax.set_xticklabels(
    labels
)

ax.legend()

# Add percentages above Found bars
for bar, percentage, error in zip(
    bars_found,
    found_mass_percentage.values,
    found_mass_error.values
):

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + error,
        f"{percentage:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9
    )

# Add percentages above Fell bars
for bar, percentage, error in zip(
    bars_fell,
    fell_mass_percentage.values,
    fell_mass_error.values
):

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + error,
        f"{percentage:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9
    )

# Add space above tallest bar (with its error bar)
max_value = max(
    (found_mass_percentage + found_mass_error).max(),
    (fell_mass_percentage + fell_mass_error).max()
)

ax.set_ylim(
    0,
    max_value * 1.18
)

plt.tight_layout()

# Save the graph for the report
plt.savefig(project_folder / "plot_mass_ranges.png", dpi=200, bbox_inches="tight")

plt.show()
