import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter

df = pd.read_csv("vehicleSet_stats.csv")

def plot_vehicle_time(df, title):
    # 1. Regroupe by number of vehicles and calculate the average creation time for each group
    df_clean = (
        df.groupby('number_of_vehicles', as_index=False)
        ['creation_time_laps']
        .mean()
        .sort_values('number_of_vehicles')
    )

    # 2. Draw the graph using matplotlib
    plt.figure(figsize=(10, 5))
    x = df_clean['number_of_vehicles']
    y = df_clean['creation_time_laps']

    plt.plot(x, y, marker='.')
    plt.title(title)
    plt.xlabel('Number of Vehicles')
    plt.ylabel('Average Creation Time in seconds')
    plt.grid(True)

    # --- FORCE decimal display on axes ---
    ax = plt.gca()
    # ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.show()

    # 3. optional: return the average creation time for each number of vehicles
    return df_clean

def plot2(df, title):
    plt.figure()
    plt.scatter(df["earliest_departure"], df["total_route_nodes_created"])
    plt.xlabel("Earliest departure time")
    plt.ylabel("Route length (number of nodes)")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


plot_vehicle_time(df, "Vehicle Creation Time Graph")
# plot2(df, "Route Length vs Earliest Departure Time")