import networkx as nx
import random 
from typing import Any, List, Dict, Tuple, Union
 
def assign_random_attribute(attributes):
    """
    Randomly assign one of the attributes to True, others to False.
    
    Parameters:
    - attributes: List of attribute names.
    
    Returns:
    - Dictionary with one attribute set to True and others set to False.
    """
    node_attr = {attr: False for attr in attributes}
    chosen_attr = random.choice(attributes)
    node_attr[chosen_attr] = True
    return node_attr

def assign_random_attribute(attributes: List[str]) -> Dict[str, bool]:
    """
    Randomly assign one of the attributes to True, others to False.
    
    Parameters:
    - attributes: List of attribute names.
    
    Returns:
    - Dictionary with one attribute set to True and others set to False.
    """
    node_attr: Dict[str, bool] = {attr: False for attr in attributes}
    chosen_attr: str = random.choice(attributes)
    node_attr[chosen_attr] = True
    return node_attr


def node_id_to_row_col(node_id: Union[Tuple[int, int], Tuple[str, str], str]) -> Tuple[int, int]:
    """
    Convert a node ID to row and column indices.

    Parameters:
    - node_id: Can be a tuple of two integers, a tuple of two alphabetic characters, or a string with 2 alphabetic characters.

    Returns:
    - A tuple of (row, col) as integers.
    """
    if isinstance(node_id, tuple) and len(node_id) == 2:
        if all(isinstance(x, int) for x in node_id):
            return node_id
        elif all(isinstance(x, str) and x.isalpha() for x in node_id):
            return (ord(node_id[0].upper()) - ord('A'), ord(node_id[1].upper()) - ord('A'))
    elif isinstance(node_id, str) and len(node_id) == 2 and node_id.isalpha():
        return (ord(node_id[0].upper()) - ord('A'), ord(node_id[1].upper()) - ord('A'))
    
    raise ValueError("Invalid node ID format")


def row_col_to_node_id(row: int, col: int, node_format: Union[Tuple[int, int], Tuple[str, str], str]) -> Union[Tuple[int, int], Tuple[str, str], str]:
    """
    Convert row and column indices back to the original node ID format.

    Parameters:
    - row: Row index as integer.
    - col: Column index as integer.
    - node_format: The format of the original node ID to determine the return type.

    Returns:
    - Node ID in the same format as the input node.
    """
    if isinstance(node_format, tuple) and len(node_format) == 2:
        if all(isinstance(x, int) for x in node_format):
            return (row, col)
        elif all(isinstance(x, str) and x.isalpha() for x in node_format):
            return (chr(row + ord('A')), chr(col + ord('A')))
    elif isinstance(node_format, str) and len(node_format) == 2 and node_format.isalpha():
        return f"{chr(row + ord('A'))}{chr(col + ord('A'))}"
    
    raise ValueError("Invalid node format")

def add_edges_for_node(G: nx.Graph, node: Any, rows: int, cols: int) -> None:
    """
    Add hexagonal grid edges for a single node.
    
    Parameters:
    - G: The networkx graph to which edges will be added.
    - node: The current node (row, col).
    - rows: Number of rows in the grid.
    - cols: Number of columns in the grid.
    """
    # convert from generic node id to row, col  
    row, col = node_id_to_row_col(node)
    neighbors = get_hexagonal_neighbors(row, col, rows, cols)


    neighbors = [row_col_to_node_id(r, c, node) for r, c in neighbors]
    for neighbor in neighbors:
        if neighbor in G.nodes:
            G.add_edge(node, neighbor)

def get_hexagonal_neighbors(row: int, col: int, rows: int, cols: int) -> List[Tuple[int, int]]:
    """
    Get the list of hexagonal neighbors for a given node in a hexagonal grid where odd rows are indented.
    
    Parameters:
    - row: Row index of the node (0-based).
    - col: Column index of the node (0-based).
    - rows: Total number of rows in the grid.
    - cols: Total number of columns in the grid.
    
    Returns:
    - List of neighbor coordinates as tuples (row, col).
    """
    neighbors = []
    
    # Define neighbor offsets for hexagonal grid
    # For even rows: top-left, top-right, left, right, bottom-left, bottom-right
    # For odd rows: top-left, top-right, left, right, bottom-left, bottom-right (shifted right)
    offsets = [
        (-1, -1), (-1, 0),
        (0, -1), (0, 1),
        (1, -1), (1, 0)
    ] if row % 2 == 0 else [
        (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, 0), (1, 1)
    ]
    
    for dr, dc in offsets:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < rows and 0 <= new_col < cols:
            neighbors.append((new_row, new_col))
    # Ensure the current node is not included in the neighbors list
    neighbors = [neighbor for neighbor in neighbors if neighbor != (row, col)]
    return neighbors

def add_hexagonal_edges(G: nx.Graph, rows: int, cols: int) -> None:
    """
    Add hexagonal grid edges to the graph by iterating over all nodes.
    
    Parameters:
    - G: The networkx graph to which edges will be added.
    - rows: Number of rows in the grid.
    - cols: Number of columns in the grid.
    """
    for row in range(rows):
        for col in range(cols):
            node = (row, col)
            add_edges_for_node(G, node, rows, cols)

def get_terrain_types():
    return ['swamp', 'forest', 'water', 'mountain', 'desert']


def generate_hexagonal_grid_graph(rows, cols):
    """
    Generate a hexagonal grid graph where each node is assigned one of the boolean flags:
    is_Swamp, is_Forest, is_Water, is_Mountain, is_Desert (uniquely).
    
    Parameters:
    - rows: Number of rows in the grid.
    - cols: Number of columns in the grid.
    
    Returns:
    - A networkx graph (nx.Graph) representing the hexagonal grid with assigned boolean attributes.
    """
    G = nx.Graph()
    
    attributes = [f'is_{terrain}' for terrain in get_terrain_types()]
    
    # Add nodes with random attributes
    for row in range(rows):
        for col in range(cols):
            node = (row, col)
            node_attr = assign_random_attribute(attributes)
            G.add_node(node, **node_attr)
    
    # Add edges for hexagonal connectivity
    add_hexagonal_edges(G, rows, cols)
    
    return G

if __name__ == "__main__":
    # Example Usage
    G = generate_hexagonal_grid_graph(8, 11)

    # Print node attributes
    for node, data in G.nodes(data=True):
        print(f"Node {node}: {data}")
