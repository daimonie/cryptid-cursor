import random

import networkx as nx


def initialize_node_attributes(G: nx.Graph, attribute: str) -> None:
    """
    Initialize all nodes in the graph with the given attribute set to False.

    Parameters:
    - G: The networkx graph (nx.Graph).
    - attribute: The name of the attribute to be initialized.
    """
    for node in G.nodes:
        G.nodes[node].setdefault(attribute, False)


def select_random_start_node(G: nx.Graph) -> int:
    """
    Select a random starting node from the graph.

    Parameters:
    - G: The networkx graph (nx.Graph).

    Returns:
    - A randomly selected node.
    """
    return random.choice(list(G.nodes))


def expand_connected_area(G: nx.Graph, start_node: int, N: int) -> set:
    """
    Expand from the start node to create a connected area of N nodes.

    Parameters:
    - G: The networkx graph (nx.Graph).
    - start_node: The node from which to start the expansion.
    - N: The desired size of the connected area.

    Returns:
    - A set of nodes that form the connected area.
    """
    visited = set()
    queue = [start_node]

    while queue and len(visited) < N:
        current_node = queue.pop(0)  # BFS: FIFO
        if current_node not in visited:
            visited.add(current_node)
            neighbors = list(G.neighbors(current_node))
            random.shuffle(neighbors)  # Shuffle to ensure randomness
            queue.extend(neighbors)

    return visited


def assign_attribute_to_nodes(G: nx.Graph, nodes: set, attribute: str) -> None:
    """
    Assign the attribute to the specified nodes and set it to False for all others.

    Parameters:
    - G: The networkx graph (nx.Graph).
    - nodes: The set of nodes to which the attribute should be set to True.
    - attribute: The name of the attribute to be set.
    """
    # Set attribute to True for the nodes in the connected area
    nx.set_node_attributes(G, {node: True for node in nodes}, name=attribute)
    # Ensure all other nodes have the attribute set to False if not already set
    for node in G.nodes:
        if node not in nodes:
            G.nodes[node].setdefault(attribute, False)


def add_connected_area_attribute(G: nx.Graph, attribute: str, N: int) -> None:
    """
    Orchestrates the process of adding an attribute to a random hexagon node and generating
    a connected area of N nodes with the given attribute set to True.

    Parameters:
    - G: The networkx graph (nx.Graph) representing the hexagonal grid.
    - attribute: The name of the attribute to be added.
    - N: The size of the connected area to be created.
    """
    if N > len(G.nodes):
        raise ValueError(
            "N cannot be greater than the total number of nodes in the graph."
        )

    initialize_node_attributes(G, attribute)
    start_node = select_random_start_node(G)
    connected_area = expand_connected_area(G, start_node, N)
    assign_attribute_to_nodes(G, connected_area, attribute)


if __name__ == "__main__":
    # Example Usage
    G = nx.hexagonal_lattice_graph(5, 5)  # Create a 5x5 hexagonal grid graph

    # Mark a connected area of 10 nodes with 'is_Swamp' attribute
    add_connected_area_attribute(G, "is_Swamp", 10)

    # Print node attributes
    for node, data in G.nodes(data=True):
        print(f"Node {node}: {data}")
