import networkx as nx
from utils.graph_generate_landscape import (
    generate_hexagonal_grid_graph, 
)
from utils.graph_generate_random_area import ( 
    add_connected_area_attribute,
)

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Generate an 11x8 hexagonal grid graph
rows, cols = 11, 8
G = generate_hexagonal_grid_graph(rows, cols)
def plot_hexagonal_grid(G, rows, cols):
    fig, ax = plt.subplots(figsize=(12, 10))
    # Define color mapping
    color_map = {
        'is_Desert': 'yellow',
        'is_Water': 'blue',
        'is_Forest': 'green',
        'is_Mountain': 'gray',
        'is_Swamp': 'brown'  # Added Swamp color for completeness
    }

    # Calculate hexagon size
    hex_size = 1 / (cols * 1.5)

    for node, data in G.nodes(data=True):
        row, col = node
        # Offset every other row
        x = col * 1.5 * hex_size
        y = row * np.sqrt(3) * hex_size
        if row % 2 == 1:
            x += 0.75 * hex_size
        # Determine color based on node attributes
        color = next((color_map[attr] for attr, value in data.items() if value), 'white')
        # Adjust the x and y coordinates for proper hexagonal grid layout
        x = col * np.sqrt(3) * hex_size
        y = row * np.sqrt(2) * hex_size
        if row % 2 == 1:  # Change to odd rows
            x += 0.5*np.sqrt(3) * hex_size
        
        # Adjust for horizontal overlap and vertical margin
        x *= 0.99  # Reduce horizontal spacing slightly
        y *= 1.05  # Increase vertical spacing slightly

        # Create and add the hexagon patch
        from matplotlib.patches import RegularPolygon
        hex_patch = RegularPolygon((x, y), numVertices=6, radius=hex_size,
                                   orientation=0, facecolor=color, edgecolor='k')
        ax.add_patch(hex_patch)
        # Check if the node is a bear or cougar area
        if data.get('is_Bear') or data.get('is_Cougar'):
            inner_hex_size = hex_size * 0.9  # Slightly smaller
            inner_color = 'none'  # Transparent fill
            edge_color = 'black' if data.get('is_Bear') else 'red'
            inner_hex = RegularPolygon((x, y), numVertices=6, radius=inner_hex_size,
                                       orientation=0, facecolor=inner_color, 
                                       edgecolor=edge_color, linestyle='--', linewidth=3)
            ax.add_patch(inner_hex)
        # Add nodeID text in the middle of the hexagon
        node_id = f"{chr(row + ord('A'))}{chr(col + ord('A'))}"
        ax.text(x, y, node_id, ha='center', va='center', fontsize=8)

    # Set plot limits and remove axes
    ax.set_xlim(-hex_size, 2*hex_size + cols * 1.5 * hex_size)
    ax.set_ylim(-hex_size, rows * 1.5 * hex_size)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.title('Hexagonal Grid Map')
    
    plt.tight_layout()
    
    plt.savefig('hexagonal_grid_map.png', dpi=300, bbox_inches='tight')
    
    plt.close()

# Add bear areas
add_connected_area_attribute(G, 'is_Bear', 2)
add_connected_area_attribute(G, 'is_Bear', 3)

# Add cougar areas
add_connected_area_attribute(G, 'is_Cougar', 2)
add_connected_area_attribute(G, 'is_Cougar', 3)

# Visualize the hexagonal grid 
plot_hexagonal_grid(G, rows, cols)

# At this point, G is a networkx graph representing the hexagonal grid
# Each node in G has attributes for terrain type (is_Swamp, is_Forest, etc.)
# and is connected to its neighbors according to hexagonal grid rules

# You can now use this graph for further processing or visualization
# For example, to get the terrain type of a specific node:
# node = (0, 0)  # Example node
# terrain = [attr for attr, value in G.nodes[node].items() if value][0]

# To iterate over all nodes and their attributes:
# for node in G.nodes(data=True):
#     node_id, attributes = node
#     # Process node attributes here

# Note: Further visualization or processing steps would depend on your specific requirements
