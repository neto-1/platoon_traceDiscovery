import pandas as pd
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np



# Data preparation for box plot

# 0. We Load files 
platoon = pd.read_csv("platoon_stats.csv")
vehicle = pd.read_csv("vehicleSet_stats.csv")

# 1. Sum events per vehicle_set (id)
events_sum = (
    platoon.groupby("vehicle_set")["number_of_events"]
    .sum()
    .reset_index()
)


# 2. We Join with vehicleSet_stats file  to get number_of_vehicles for each vehicle_set
merged = events_sum.merge(
    vehicle,
    left_on="vehicle_set",
    right_on="vehicle_set_id",
    how="left"
)

# 3. Build JSON structure
result = defaultdict(list)

for _, row in merged.iterrows():
    label = int(row["number_of_vehicles"])
    result[label].append(int(row["number_of_events"]))

# 4. Save to JSON ---
with open("boxPlot_data.json", "w") as f:
    json.dump(result, f, indent=2)

print("-"*50+"-")
print("Data prepared for box plot:")
print(dict(result))

# -----------------------------------------------------------------------------------------------------------
# Box plotting 

data = dict(result)  # Convert defaultdict to regular dict for plotting

# sort keys for consistent ordering
keys_sorted = sorted(data.keys())

labels = [str(k) for k in keys_sorted]
values = [data[k] for k in keys_sorted]


# PLOT
plt.figure(figsize=(8, 5))

# main box plot
box = plt.boxplot(
    values,
    labels=labels,
    patch_artist=True,
    showfliers=True  # show outliers
)

# --- overlay individual points (pro feature) ---
for i, y in enumerate(values, start=1):
    x = np.random.normal(i, 0.04, size=len(y))  # small horizontal jitter
    plt.plot(x, y, "o", alpha=0.6)


# STYLE
colors = ["#FF9999", "#99FF99", "#9999FF", "#FFCC99"]  # pastel colors
for patch, color in zip(box["boxes"], colors):
    patch.set_facecolor(color)

plt.title("Distribution of Platoon per Number of Vehicles for 50 different test cases in the Bayern road network")
plt.xlabel("Number of Vehicles")
plt.ylabel("Platoons per Vehicle Set")

plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()

plt.show()

