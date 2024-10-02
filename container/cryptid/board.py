import networkx as nx
import numpy as np

from utils.graph_generate_landscape import generate_hexagonal_grid_graph
from utils.graph_generate_random_area import add_connected_area_attribute
from utils.graph_utils import enrich_node_attributes


def generate_structure_color_combinations():
    """
    Generate all possible combinations of structures and colors.

    Returns:
    list: A list of strings, each representing a unique structure-color combination.
    """
    structures, colors = generate_all_structures()
    return [f"{s}_{c}" for s in structures for c in colors]


def select_random_structures(generator, all_structures, min_structures, max_structures):
    """
    Select a random number of structures from the given list.

    Args:
    generator (numpy.random.Generator): The random number generator.
    all_structures (list): List of all possible structures.
    min_structures (int): Minimum number of structures to select.
    max_structures (int): Maximum number of structures to select.

    Returns:
    list: A list of randomly selected structures.
    """
    num_structures = generator.integers(min_structures, max_structures + 1)
    return generator.choice(all_structures, size=num_structures, replace=False).tolist()


def try_location(generator, G, rows, cols, all_structures):
    """
    Attempt to find an empty location on the graph for a structure.

    Args:
    generator (numpy.random.Generator): The random number generator.
    G (networkx.Graph): The graph representing the game board.
    rows (int): Number of rows in the grid.
    cols (int): Number of columns in the grid.
    all_structures (list): List of all possible structures.

    Returns:
    tuple or None: A tuple (row, col) if an empty location is found, None otherwise.
    """
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
    parts = structure.split("_")
    color = parts.pop()
    structure_type = "_".join(parts)
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
    selected_structures = select_random_structures(
        generator, all_structures, min_structures, max_structures
    )

    for structure in selected_structures:
        location = find_empty_location(generator, G, rows, cols, all_structures)
        add_structure_to_graph(G, structure, location)


def generate_all_structures():
    structures = ["standing_stone", "abandoned_shack"]
    colors = ["blue", "green", "white", "black"]
    return structures, colors


def get_all_animals():
    return ["bear", "cougar"]


def get_terrain_types():
    return ["forest", "desert", "water", "mountain", "swamp"]


def generate_game_map(generator, rows, cols):
    G = generate_hexagonal_grid_graph(rows, cols)

    # Add animal areas
    for animal in get_all_animals():
        add_connected_area_attribute(G, f"is_{animal.lower()}", 2)
        add_connected_area_attribute(G, f"is_{animal.lower()}", 3)

    # Add random structures to the board
    add_random_structures(generator, G, rows, cols)

    # Get all structure attributes
    all_structures = generate_structure_color_combinations()

    all_attrs = [f"is_{animal}" for animal in get_all_animals()] + all_structures

    # Enrich node attributes for all structures
    G = enrich_node_attributes(G)

    return G
