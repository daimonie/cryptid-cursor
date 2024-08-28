import networkx as nx
import hashlib
import json

def serialize_graph(graph: nx.Graph) -> str:
    """
    Serialize the graph to a JSON string.
    
    Parameters:
    - graph: A networkx graph (nx.Graph) whose nodes have attributes and edges.
    
    Returns:
    - A JSON string representing the graph structure.
    """
    graph_data = {
        "nodes": {node: dict(data) for node, data in graph.nodes(data=True)},
        "edges": list(graph.edges())
    }
    return json.dumps(graph_data, sort_keys=True)


def generate_unique_code(serialized_graph: str) -> str:
    """
    Generate a unique SHA-256 hash for the serialized graph string.
    
    Parameters:
    - serialized_graph: A JSON string representing the graph structure.
    
    Returns:
    - A SHA-256 hash of the serialized graph string.
    """
    return hashlib.sha256(serialized_graph.encode()).hexdigest()


def parse_code_to_graph(graph_hash: str, serialized_data_store: dict) -> nx.Graph:
    """
    Reconstruct a graph from a hash using the serialized data stored with the hash.
    
    Parameters:
    - graph_hash: The hash of the graph, used to lookup the serialized data.
    - serialized_data_store: A dictionary storing serialized graph data keyed by hash.
    
    Returns:
    - A networkx graph reconstructed from the stored serialized data.
    
    Raises:
    - KeyError if the hash is not found in the serialized_data_store.
    """
    if graph_hash not in serialized_data_store:
        raise KeyError("Graph data for the given hash not found.")
    
    serialized_data = serialized_data_store[graph_hash]
    graph_data = json.loads(serialized_data)

    graph = nx.Graph()
    graph.add_nodes_from((node, attrs) for node, attrs in graph_data["nodes"].items())
    graph.add_edges_from(graph_data["edges"])

    return graph


def enrich_node_attributes(graph: nx.Graph) -> nx.Graph:
    """
    Enriches the graph by adding attributes to each node indicating whether
    any neighbors or neighbors of neighbors have a certain boolean attribute set to True.
    
    Parameters:
    - graph: A networkx graph (nx.Graph) with boolean attributes on nodes (one-hot encoded).
    
    Returns:
    - The enriched networkx graph with additional attributes.
    """
    # Create a dictionary to track neighbor and neighbor-of-neighbor attributes
    attr_summary = {node: {'neighbors': set(), 'neighbors_of_neighbors': set()} for node in graph.nodes}

    # Populate the dictionary
    for node in graph.nodes:
        neighbors = set(graph.neighbors(node))
        attr_summary[node]['neighbors'] = neighbors
        for neighbor in neighbors:
            attr_summary[node]['neighbors_of_neighbors'].update(graph.neighbors(neighbor))
        attr_summary[node]['neighbors_of_neighbors'].discard(node)
    
    # Cache for new attributes
    new_attributes = {node: {} for node in graph.nodes}
    
    # Enrich the attributes
    for node in graph.nodes:
        node_attrs = graph.nodes[node]
        neighbors = attr_summary[node]['neighbors']
        neighbors_of_neighbors = attr_summary[node]['neighbors_of_neighbors']

        for attr, value in node_attrs.items():
            if isinstance(value, bool) and value:
                new_attributes[node][f"neighbor_has_{attr}"] = any(graph.nodes[neighbor].get(attr, False) for neighbor in neighbors)
                new_attributes[node][f"neighbor_of_neighbor_has_{attr}"] = any(graph.nodes[neighbor_of_neighbor].get(attr, False) for neighbor_of_neighbor in neighbors_of_neighbors)
    
    # Update node attributes after the loop
    for node, attrs in new_attributes.items():
        graph.nodes[node].update(attrs)
    
    return graph


def filter_nodes_by_attributes(graph: nx.Graph, *args) -> list:
    """
    Filter nodes based on attributes provided as key-value pairs in *args.
    
    Parameters:
    - graph: A networkx graph (nx.Graph) with attributes on nodes.
    - *args: A variable number of key-value pairs representing attributes and their desired values.
    
    Returns:
    - A list of node IDs that satisfy the attributes represented in the arguments.
    """
    if len(args) % 2 != 0:
        raise ValueError("Arguments must be provided in key-value pairs.")

    attr_conditions = dict(zip(args[::2], args[1::2]))
    
    def node_matches_conditions(node_attrs):
        return all(node_attrs.get(attr) == value for attr, value in attr_conditions.items())
    
    return [node for node, attrs in graph.nodes(data=True) if node_matches_conditions(attrs)]

def create_graph():
    graph = nx.Graph()
    graph.add_nodes_from([
        (1, {"attr1": True, "attr2": False}),
        (2, {"attr1": False, "attr2": True}),
        (3, {"attr1": True, "attr2": True})
    ])
    graph.add_edges_from([(1, 2), (2, 3)])
    return graph
if __name__ == "__main__":
    # Example usage or test code
    test_graph = create_graph()

    print("Original graph:", test_graph.nodes(data=True))
    
    enriched_graph = enrich_node_attributes(test_graph)
    print("Enriched graph:", enriched_graph.nodes(data=True))
    
    filtered_nodes = filter_nodes_by_attributes(enriched_graph, "attr1", True)
    print("Nodes with attr1=True:", filtered_nodes)

    serialized = serialize_graph(enriched_graph)
    print("Serialized graph:", serialized)

    unique_code = generate_unique_code(serialized)
    print("Unique code:", unique_code)

    reconstructed_graph = parse_code_to_graph(unique_code, {unique_code: serialized})
    print("Reconstructed graph:", reconstructed_graph.nodes(data=True))
