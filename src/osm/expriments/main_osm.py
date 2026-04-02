import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import osmnx as ox

def main():
    G = ox.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='drive')
    G_projected = ox.project_graph(G)
    ox.plot_graph(G_projected)

if __name__ == "__main__":
    main()
