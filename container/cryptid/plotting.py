import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import RegularPolygon
 

def create_inner_hex_patch(x, y, hex_size, is_bear):
    """Create an inner hexagon patch for bear or cougar areas."""
    inner_hex_size = hex_size * 0.9
    edge_color = 'black' if is_bear else 'red'
    return RegularPolygon((x, y), numVertices=6, radius=inner_hex_size,
                          orientation=2*np.pi/12, facecolor='none', 
                          edgecolor=edge_color, linestyle='--', linewidth=3)

# Draw connections for all nodes
def get_node_center(row, col, hex_size):
    x = col * 1.5 * hex_size
    y = row * np.sqrt(3) * hex_size
    if col % 2 == 1:
        y += np.sqrt(3) * hex_size / 2
    return x, y
def plot_hexagonal_test(G, rows, cols, hex_size=1, cryptid_markers=None, hints=None, prefix=""):
    return plot_hexagonal_grid(
        G,
        rows,
        cols,
        hex_size=1,
        cryptid_markers=cryptid_markers,
        hints=hints,
        prefix=prefix,
        mark_edges=True,
        mark_standing_stone=True
    )

def plot_hexagonal_grid(G, rows, cols, hex_size=1, cryptid_markers=None, hints=None, prefix="", mark_edges=False, mark_standing_stone=False):
    fig, ax = plt.subplots(figsize=(cols * 1.5, rows * 1.5))
    ax.set_aspect('equal')

    for row in range(rows):
        for col in range(cols):
            x = col * 1.5 * hex_size
            y = row * np.sqrt(3) * hex_size
            if col % 2 == 1:
                y += np.sqrt(3) * hex_size / 2

            data = G.nodes[(row, col)]
            hex_color = get_terrain_color(data)
            hex = RegularPolygon((x, y), numVertices=6, radius=hex_size,
                                 orientation=np.pi/6, facecolor=hex_color, edgecolor='k')
            ax.add_patch(hex)
            ax.text(x, y, f'({row},{col})', ha='center', va='center', fontsize=8)
            # add animals
                
            if data.get('is_bear') or data.get('is_cougar'):
                inner_hex = create_inner_hex_patch(x, y, hex_size, data.get('is_bear'))
                ax.add_patch(inner_hex)
                
            # add structures
            add_structures_to_plot(ax, data, x, y, hex_size)

            if cryptid_markers and (row, col) in cryptid_markers:
                add_hydra_marker(ax, x, y, hex_size)
            
            if mark_standing_stone:
            # Check for near structure and add red square if True
                if data.get('neighbor_neighbor_neighbor_standing_stone', False):
                    add_bottom_marker(ax, x, y, hex_size, shape='square', alignment='right', color='black')
                if data.get('neighbor_neighbor_standing_stone', False):
                    add_bottom_marker(ax, x, y, hex_size, shape='circle', alignment='center', color='#00FF00')
                if data.get('neighbor_standing_stone', False):
                    add_bottom_marker(ax, x, y, hex_size, shape='square', alignment='left', color='red')

    if mark_edges:
        for node in G.nodes():
            # Add a 90% random chance to continue and skip drawing edges
            if np.random.random() > 0.1:
                continue
            for neighbor in G.neighbors(node):
                start_x, start_y = get_node_center(node[0], node[1], hex_size)
                end_x, end_y = get_node_center(neighbor[0], neighbor[1], hex_size)
                ax.annotate("", xy=(end_x, end_y), xytext=(start_x, start_y),
                            arrowprops=dict(arrowstyle="-", color="purple", lw=1, alpha=0.5),
                            zorder=1)


    if hints:
        hint_text = "\n".join([f"Hint {i+1}: {', '.join(hint)}" for i, hint in enumerate(hints)])
        plt.figtext(
            0.02, 
            0.98, 
            hint_text, 
            ha="left", 
            va="top", 
            fontsize=10, 
            bbox={
                "facecolor":"white", 
                "alpha":0.5, 
                "pad":5
            }
        )

    ax.set_xlim(-1, cols * 1.5 * hex_size + 1)
    ax.set_ylim(-1, rows * np.sqrt(3) * hex_size + 1)
    ax.axis('off')
    plt.tight_layout()
    
    plt.savefig(f'{prefix}.png', dpi=300, bbox_inches='tight')
    plt.close()

def get_terrain_color(node_data):
    color_map = {
        'is_desert': 'yellow',
        'is_water': 'blue',
        'is_forest': 'green',
        'is_mountain': 'gray',
        'is_swamp': 'brown'
    }
    for key, val in color_map.items(): 
        if node_data.get(key, False):
            return val
        
    filtered_data = {k: v for k, v in node_data.items() if 'neighbor' not in k}
    raise ValueError(f"No terrain type found. Node attributes: {filtered_data}")

def add_hydra_marker(ax, hex_x, hex_y, hex_size):
    marker_x = hex_x
    marker_y = hex_y + 0.5 * hex_size
    # Add Hydra body
    body = ax.add_patch(plt.Circle((marker_x, marker_y), radius=hex_size*0.2, 
                                   facecolor='red', edgecolor='black', zorder=3))
    
    # Add Hydra tentacles
    num_tentacles = 5
    tentacle_length = hex_size * 0.3
    tentacle_start_y = marker_y - hex_size * 0.1
    
    for i in range(num_tentacles):
        angle = np.pi * (0.6 + 0.8 * i / (num_tentacles - 1))
        end_x = marker_x + hex_size * 0.3 * np.cos(angle)
        end_y = marker_y + hex_size * 0.3 * np.sin(angle)
        ax.plot([marker_x, end_x], [tentacle_start_y, end_y], color='red', linewidth=2, zorder=2)

    # Add Hydra eyes
    eye_offset = hex_size * 0.08
    left_eye = ax.add_patch(plt.Circle((marker_x - eye_offset, marker_y + eye_offset), 
                                       radius=hex_size*0.03, facecolor='white', edgecolor='black', zorder=4))
    right_eye = ax.add_patch(plt.Circle((marker_x + eye_offset, marker_y + eye_offset), 
                                        radius=hex_size*0.03, facecolor='white', edgecolor='black', zorder=4))

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
def add_bottom_marker(ax, x, y, hex_size, shape='square', alignment='center', color='red'):
    """
    Add a square or circle marker at the bottom of the hexagon.
    
    Parameters:
    - ax: matplotlib axis
    - x, y: coordinates of the hexagon center
    - hex_size: size of the hexagon
    - shape: 'square' or 'circle'
    - alignment: 'left', 'center', or 'right'
    - color: color of the marker
    """
    marker_size = hex_size * 0.2
    y_offset = -hex_size * 0.5  # Move to bottom of hexagon
    
    if alignment == 'left':
        x_offset = -hex_size * 0.4
    elif alignment == 'right':
        x_offset = hex_size * 0.4
    else:  # center
        x_offset = 0
    
    marker_x = x + x_offset
    marker_y = y + y_offset
    
    if shape == 'square':
        marker = plt.Rectangle((marker_x - marker_size/2, marker_y - marker_size/2), 
                               marker_size, marker_size, 
                               facecolor=color, edgecolor='black', zorder=3)
    else:  # circle
        marker = plt.Circle((marker_x, marker_y), radius=marker_size/2, 
                            facecolor=color, edgecolor='black', zorder=3)
    
    ax.add_patch(marker)

