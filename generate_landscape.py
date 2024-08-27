import networkx as nx
import random 

def mark_connected_area(G: nx.Graph, attribute: str, N: int) -> None:
    """
    Adds an attribute to the graph's nodes to represent a connected area of N nodes
    with the given attribute set to True, and all other nodes set to False.
    
    Parameters:
    - G: The networkx graph (nx.Graph) to which the attribute will be added.
    - attribute: The name of the attribute to be set.
    - N: The size of the connected area to be marked.
    """
    # Initialize all nodes with the attribute set to False
    nx.set_node_attributes(G, {node: False for node in G.nodes}, name=attribute)
    
    # Find all connected components
    connected_components = list(nx.connected_components(G))
    
    # Iterate through each connected component
    for component in connected_components:
        if len(component) == N:
            # Set the attribute to True for nodes in the component of size N
            nx.set_node_attributes(G, {node: True for node in component}, name=attribute)

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

def add_edges_for_node(G, node, rows, cols):
    """
    Add hexagonal grid edges for a single node.
    
    Parameters:
    - G: The networkx graph to which edges will be added.
    - node: The current node (row, col).
    - rows: Number of rows in the grid.
    - cols: Number of columns in the grid.
    """
    row, col = node
    neighbors = get_hexagonal_neighbors(row, col, rows, cols)
    for neighbor in neighbors:
        if neighbor in G.nodes:
            G.add_edge(node, neighbor)

def get_hexagonal_neighbors(row, col, rows, cols):
    """
    Get the list of hexagonal neighbors for a given node.
    
    Parameters:
    - row: Row index of the node.
    - col: Column index of the node.
    - rows: Number of rows in the grid.
    - cols: Number of columns in the grid.
    
    Returns:
    - List of neighbor coordinates.
    """
    neighbors = []
    
    # Define neighbor offsets for hexagonal grid
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1 if col % 2 == 0 else 0, -1), (-1 if col % 2 == 0 else 0, 1)]
    
    for dr, dc in offsets:
        r, c = row + dr, col + dc
        if 0 <= r < rows and 0 <= c < cols:
            neighbors.append((r, c))
    
    return neighbors

def add_hexagonal_edges(G, rows, cols):
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
    attributes = ['is_Swamp', 'is_Forest', 'is_Water', 'is_Mountain', 'is_Desert']
    
    # Add nodes with random attributes
    for row in range(rows):
        for col in range(cols):
            node = (row, col)
            node_attr = assign_random_attribute(attributes)
            G.add_node(node, **node_attr)
    
    # Add edges for hexagonal connectivity
    add_hexagonal_edges(G, rows, cols)
    
    return G

# Example Usage
G = generate_hexagonal_grid_graph(8, 11)

# Print node attributes
for node, data in G.nodes(data=True):
    print(f"Node {node}: {data}")
