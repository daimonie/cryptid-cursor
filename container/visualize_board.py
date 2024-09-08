import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
import seaborn as sns

from matplotlib.patches import RegularPolygon
from utils.graph_generate_landscape import generate_hexagonal_grid_graph
from utils.graph_generate_random_area import add_connected_area_attribute
from utils.graph_utils import enrich_node_attributes


def calculate_hex_coordinates(row, col, hex_size):
    """Calculate the x, y coordinates for a hexagon in the grid."""
    x = col * np.sqrt(3) * hex_size
    y = row * np.sqrt(2) * hex_size
    if row % 2 == 1:
        x += 0.5 * np.sqrt(3) * hex_size
    
    # Adjust for horizontal overlap and vertical margin
    x *= 0.99  # Reduce horizontal spacing slightly
    y *= 1.05  # Increase vertical spacing slightly
    
    return x, y

def create_hex_patch(x, y, hex_size, color):
    """Create a hexagon patch for matplotlib."""
    return RegularPolygon((x, y), numVertices=6, radius=hex_size,
                          orientation=0, facecolor=color, edgecolor='k')

def create_inner_hex_patch(x, y, hex_size, is_bear):
    """Create an inner hexagon patch for bear or cougar areas."""
    inner_hex_size = hex_size * 0.9
    edge_color = 'black' if is_bear else 'red'
    return RegularPolygon((x, y), numVertices=6, radius=inner_hex_size,
                          orientation=0, facecolor='none', 
                          edgecolor=edge_color, linestyle='--', linewidth=3)

def get_node_color(data, color_map):
    """Determine the color of a node based on its attributes."""
    return next((color_map[attr] for attr, value in data.items() if value), 'white')

def add_node_id_text(ax, x, y, row, col):
    """Add node ID text to the plot."""
    node_id = f"{chr(row + ord('A'))}{chr(col + ord('A'))}"
    ax.text(x, y, node_id, ha='center', va='center', fontsize=8)

def setup_plot(rows, cols, hex_size):
    """Set up the matplotlib plot."""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(-hex_size, 2*hex_size + cols * 1.5 * hex_size)
    ax.set_ylim(-hex_size, rows * 1.5 * hex_size)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax

def plot_hexagonal_grid(G, rows, cols):
    color_map = {
        'is_Desert': 'yellow',
        'is_Water': 'blue',
        'is_Forest': 'green',
        'is_Mountain': 'gray',
        'is_Swamp': 'brown'
    }

    hex_size = 1 / (cols * 1.5)
    fig, ax = setup_plot(rows, cols, hex_size)

    for node, data in G.nodes(data=True):
        row, col = node
        x, y = calculate_hex_coordinates(row, col, hex_size)
        color = get_node_color(data, color_map)

        filterattr = 'neighbor_standing_stone_blue'
        if data.get(filterattr):
            print(f"Coloring node {node} red because: {filterattr}")
            color = 'red'

        hex_patch = create_hex_patch(x, y, hex_size, color)
        ax.add_patch(hex_patch)
        
        if data.get('is_Bear') or data.get('is_Cougar'):
            inner_hex = create_inner_hex_patch(x, y, hex_size, data.get('is_Bear'))
            ax.add_patch(inner_hex)
        # Check for structures and add them to the plot
        add_node_id_text(ax, x, y, row, col)
        structure_patch = add_structures_to_plot(ax, data, x, y, hex_size)
        if structure_patch:
            ax.add_patch(structure_patch)

    plt.title('Hexagonal Grid Map')
    plt.tight_layout()
    plt.savefig('hexagonal_grid_map.png', dpi=300, bbox_inches='tight')
    plt.close()

def add_structures_to_plot(ax, data, x, y, hex_size):
    """Add structures (standing stones or abandoned shacks) to the plot."""
    for structure in ['standing_stone', 'abandoned_shack']:
        for color in ['blue', 'green', 'white', 'black']:
            structure_key = f"{structure}_{color}"
            if data.get(structure_key):
                structure_patch = create_structure_patch(structure, x, y, hex_size, color)
                ax.add_patch(structure_patch)
                return  # Only one structure per tile

def create_structure_patch(structure, x, y, hex_size, color):
    """Create a patch for a structure (standing stone or abandoned shack)."""
    print(f"Created a structure {structure} of color {color} at {x}, {y}")
    # Displace the structure to the left of the node ID label
    displaced_x = x - hex_size * 0.4  # Adjust this value as needed
    color_map = {
        'blue': '#00BFFF',    # Light Blue
        'green': '#32CD32',   # Lime Green
        'white': '#FFFFFF',   # White (unchanged)
        'black': '#1A1A1A'    # Dark Grey (almost black)
    }
    color = color_map.get(color, color)  # Use mapped color if available, else use original
    if structure == 'standing_stone':
        return RegularPolygon((displaced_x, y), numVertices=6, radius=hex_size*0.3,
                              orientation=0, facecolor=color, edgecolor='black')
    else:  # abandoned_shack
        return RegularPolygon((displaced_x, y), numVertices=3, radius=hex_size*0.3,
                              orientation=0, facecolor=color, edgecolor='black')
       


def generate_structure_combinations():
    structures = ['standing_stone', 'abandoned_shack']
    colors = ['blue', 'green', 'white', 'black']
    return [f"{s}_{c}" for s in structures for c in colors]

def select_random_structures(all_structures, min_structures, max_structures):
    num_structures = random.randint(min_structures, max_structures)
    return random.sample(all_structures, num_structures)
def try_location(G, rows, cols, all_structures):
    row = random.randint(0, rows - 1)
    col = random.randint(0, cols - 1)
    print(all_structures)
    if not any(G.nodes[(row, col)].get(s, False) for s in all_structures):
        return row, col
    return None

def find_empty_location(G, rows, cols, all_structures):
    result = try_location(G, rows, cols, all_structures)
    if result:
        return result
    else:
        return find_empty_location(G, rows, cols, all_structures)

def add_structure_to_graph(G, structure, location):
    row, col = location
    parts = structure.split('_')
    color = parts.pop()
    structure_type = '_'.join(parts)
    G.nodes[(row, col)][structure] = True
    G.nodes[(row, col)][structure_type] = True
    G.nodes[(row, col)][color] = True

def add_random_structures(G, rows, cols, min_structures=4, max_structures=6):
    """
    Add random structures to the hexagonal grid.
    
    Args:
    G (networkx.Graph): The hexagonal grid graph.
    rows (int): Number of rows in the grid.
    cols (int): Number of columns in the grid.
    min_structures (int): Minimum number of structures to add.
    max_structures (int): Maximum number of structures to add.
    """
    all_structures = generate_structure_combinations()
    # Initialize all structures to False for all nodes
    for node in G.nodes:
        for structure in all_structures:
            G.nodes[node][structure] = False
    selected_structures = select_random_structures(all_structures, min_structures, max_structures)
    
    print("Selected structures:", selected_structures)

    for structure in selected_structures:
        location = find_empty_location(G, rows, cols, all_structures)
        add_structure_to_graph(G, structure, location)

def generate_game_map(rows, cols):
    print("Generating hexagonal grid graph...")
    G = generate_hexagonal_grid_graph(rows, cols)

    print("Adding bear areas...")
    # Add bear areas
    add_connected_area_attribute(G, 'is_Bear', 2)
    add_connected_area_attribute(G, 'is_Bear', 3)

    print("Adding cougar areas...")
    # Add cougar areas
    add_connected_area_attribute(G, 'is_Cougar', 2)
    add_connected_area_attribute(G, 'is_Cougar', 3)

    print("Adding random structures to the board...")
    # Add random structures to the board
    add_random_structures(G, rows, cols)

    print("Generating structure combinations...")
    # Get all structure attributes
    # Enrich node attributes for Bear and Cougar 
    all_structures = generate_structure_combinations()
    all_attrs = ['is_Bear', 'is_Cougar'] + all_structures

    print("Enriching node attributes for all structures...")
    # Enrich node attributes for all structures
    
    G = enrich_node_attributes(G)

    return G
if __name__ == "__main__":
    # Generate an 11x8 hexagonal grid graph
    rows, cols = 11, 8

    # Generate the game map
    G = generate_game_map(rows, cols)

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
