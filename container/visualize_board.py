import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
import seaborn as sns

from matplotlib.patches import RegularPolygon
from utils.graph_generate_landscape import generate_hexagonal_grid_graph
from utils.graph_generate_random_area import add_connected_area_attribute
from utils.graph_utils import enrich_node_attributes

from cryptid.board import (
    plot_hexagonal_grid,
    generate_game_map
)

if __name__ == "__main__":
    # Example usage
    rows, cols = 11,8
    G = generate_game_map(rows, cols)
    # Select a random node from the graph
    random_node = random.choice(list(G.nodes()))

    # Get the data for the random node
    node_data = G.nodes[random_node]

    # Print the data as key: value pairs
    print(f"Data for node {random_node}:")
    for key, value in node_data.items():
        print(f"{key}: {value}")

    plot_hexagonal_grid(G, rows, cols)
