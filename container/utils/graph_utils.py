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


def _enrich_node_attributes_level(graph: nx.Graph, attr: str, prefix: str) -> dict:
    """
    Helper function to enrich node attributes for a single level.
    
    Parameters:
    - graph: A networkx graph (nx.Graph)
    - attr: The attribute to check for
    - prefix: The prefix for the new attribute
    
    Returns:
    - A dictionary of updates for the graph nodes
    """
    updates = {}
    new_attr = f"{prefix}_{attr}"
    for node in graph.nodes:
        updates[node] = {new_attr: any(
            graph.nodes[neighbor].get(attr, False) for neighbor in graph.neighbors(node)
        )}
    return updates

def enrich_node_attributes(graph: nx.Graph) -> nx.Graph:
    """
    Enriches the graph by adding attributes to each node indicating whether
    any neighbors or neighbors of neighbors have a certain boolean attribute set to True.
    
    Parameters:
    - graph: A networkx graph (nx.Graph) with boolean attributes on nodes (one-hot encoded).
    
    Returns:
    - The enriched networkx graph with additional attributes.
    """
    # Identify boolean attributes
    boolean_attributes = set()
    for node, attrs in graph.nodes(data=True):
        boolean_attributes.update(attr for attr, value in attrs.items() if isinstance(value, bool))
    
    # First level: neighbors
    for attr in boolean_attributes:
        nx.set_node_attributes(graph, _enrich_node_attributes_level(graph, attr, "neighbor"))

    # Second level: neighbors of neighbors
    for attr in boolean_attributes:
        nx.set_node_attributes(graph, _enrich_node_attributes_level(graph, f"neighbor_{attr}", "neighbor"))

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
        ('a', {"attr1": True, "attr2": False}),
        ('b', {"attr1": False, "attr2": True}),
        ('c', {"attr1": True, "attr2": True})
    ])
    graph.add_edges_from([('a', 'b'), ('b', 'c')])
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
