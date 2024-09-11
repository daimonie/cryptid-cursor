import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
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

def create_inner_octopus_patch(x, y, hex_size):
    """Create an inner octopus-like patch."""
    inner_size = hex_size * 0.7
    
    # Create the main body (circle)
    body = plt.Circle((x, y), inner_size * 0.5, facecolor='none', 
                      edgecolor='purple', linestyle='-', linewidth=2)
    
    # Create tentacles (8 lines radiating from the center)
    tentacles = []
    for angle in range(0, 360, 45):
        dx = inner_size * np.cos(np.radians(angle))
        dy = inner_size * np.sin(np.radians(angle))
        tentacle = plt.Line2D([x, x+dx], [y, y+dy], color='purple', 
                              linestyle='-', linewidth=2)
        tentacles.append(tentacle)
    
    return [body] + tentacles

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

def plot_hexagonal_grid(G, rows, cols, cryptid_markers=[], hints=[], prefix=""):
    color_map = {
        'is_desert': 'yellow',
        'is_water': 'blue',
        'is_forest': 'green',
        'is_mountain': 'gray',
        'is_swamp': 'brown'
    }

    hex_size = 1 / (cols * 1.5)
    fig, ax = setup_plot(rows, cols, hex_size)

    for node, data in G.nodes(data=True):
        row, col = node
        x, y = calculate_hex_coordinates(row, col, hex_size)
        color = get_node_color(data, color_map)

        filterattr = 'neighbor_standing_stone_blue'
        if data.get(filterattr):
            color = 'red'

        hex_patch = create_hex_patch(x, y, hex_size, color)
        ax.add_patch(hex_patch) 
        if data.get('is_bear') or data.get('is_cougar'):
            inner_hex = create_inner_hex_patch(x, y, hex_size, data.get('is_bear'))
            ax.add_patch(inner_hex)
        # Check for structures and add them to the plot
        add_node_id_text(ax, x, y, row, col)
        structure_patch = add_structures_to_plot(ax, data, x, y, hex_size)
        if structure_patch:
            ax.add_patch(structure_patch)
        if  node in cryptid_markers: 
                create_inner_octopus_patch(ax, x, y, hex_size)
    title = f'Hexagonal Grid Map {prefix}'
    if hints:
        title += f'\nHints: {", ".join(str(hint) for hint in hints)}'
    if cryptid_markers:
        title += f'\nCryptid Markers: {len(cryptid_markers)}'
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f'{prefix}hexagonal_grid_map.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_inner_octopus_patch(ax, x, y, hex_size):
    """Create a small Hydra symbol from Marvel's Avengers."""
    marker_y = y + hex_size * 0.6
    marker_x = x - hex_size * 0.4
    
    # Create Hydra skull
    skull = ax.add_patch(plt.Circle((marker_x, marker_y), radius=hex_size*0.2, 
                                    facecolor='red', edgecolor='black', zorder=3))
    # Add octopus tentacles
    tentacle_start_y = marker_y - hex_size * 0.1
    for i in range(8):
        angle = np.pi + (i * np.pi / 8)  # Angles from pi to 2pi (lower half)
        end_x = marker_x + hex_size * 0.3 * np.cos(angle)
        end_y = marker_y + hex_size * 0.3 * np.sin(angle)
        ax.plot([marker_x, end_x], [tentacle_start_y, end_y], color='red', linewidth=2, zorder=2)

    # Add Hydra eyes
    eye_offset = hex_size * 0.08
    left_eye = ax.add_patch(plt.Circle((marker_x - eye_offset, marker_y + eye_offset), 
                                       radius=hex_size*0.03, facecolor='white', edgecolor='black', zorder=4))
    right_eye = ax.add_patch(plt.Circle((marker_x + eye_offset, marker_y + eye_offset), 
                                        radius=hex_size*0.03, facecolor='white', edgecolor='black', zorder=4))

# Note: To install matplotlib with poetry, run the following command in your terminal:
# poetry add matplotlib

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
       


def generate_structure_color_combinations():
    structures, colors = generate_all_structures()
    return [f"{s}_{c}" for s in structures for c in colors]

def select_random_structures(generator, all_structures, min_structures, max_structures):
    num_structures = generator.integers(min_structures, max_structures + 1)
    return generator.choice(all_structures, size=num_structures, replace=False).tolist()

def try_location(generator, G, rows, cols, all_structures):
    row = generator.integers(0, rows)
    col = generator.integers(0, cols)
    
    if not any(G.nodes[(row, col)].get(s, False) for s in all_structures):
        return row, col
    return None

def find_empty_location(generator, G, rows, cols, all_structures):
    result = try_location(generator, G, rows, cols, all_structures)
    if result:
        return result
    else:
        return find_empty_location(generator, G, rows, cols, all_structures)

def add_structure_to_graph(G, structure, location):
    row, col = location
    parts = structure.split('_')
    color = parts.pop()
    structure_type = '_'.join(parts)
    G.nodes[(row, col)][structure] = True
    G.nodes[(row, col)][structure_type] = True
    G.nodes[(row, col)][color] = True

def add_random_structures(generator, G, rows, cols, min_structures=4, max_structures=6):
    """
    Add random structures to the hexagonal grid.
    
    Args:
    generator (numpy.random.Generator): The random number generator.
    G (networkx.Graph): The hexagonal grid graph.
    rows (int): Number of rows in the grid.
    cols (int): Number of columns in the grid.
    min_structures (int): Minimum number of structures to add.
    max_structures (int): Maximum number of structures to add.
    """
    all_structures = generate_structure_color_combinations()
    # Initialize all structures to False for all nodes
    for node in G.nodes:
        for structure in all_structures:
            G.nodes[node][structure] = False
    selected_structures = select_random_structures(generator, all_structures, min_structures, max_structures)
    

    for structure in selected_structures:
        location = find_empty_location(generator, G, rows, cols, all_structures)
        add_structure_to_graph(G, structure, location)


def generate_all_structures():
    structures = ['standing_stone', 'abandoned_shack']
    colors = ['blue', 'green', 'white', 'black']
    return structures, colors
def get_all_animals():
    return ['bear', 'cougar']
def get_terrain_types():
    return ['forest', 'desert', 'water', 'mountain', 'swamp']

def generate_game_map(generator, rows, cols):
    G = generate_hexagonal_grid_graph(rows, cols)
    # Add animal areas
    for animal in get_all_animals():
        add_connected_area_attribute(G, f'is_{animal.lower()}', 2)
        add_connected_area_attribute(G, f'is_{animal.lower()}', 3)

    # Add random structures to the board
    add_random_structures(generator, G, rows, cols)

    # Get all structure attributes
    all_structures = generate_structure_color_combinations()
    
    
    all_attrs = [f'is_{animal}' for animal in get_all_animals()] + all_structures

    # Enrich node attributes for all structures
    
    G = enrich_node_attributes(G)

    return G
