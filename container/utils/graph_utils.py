import networkx as nx
import hashlib
import json
from utils.graph_generate_landscape import node_id_to_row_col, row_col_to_node_id
from typing import List, Dict

def serialize_graph(graph: nx.Graph, hints: Dict[str, List[str]] = None) -> str:
    """
    Serialize the graph to a JSON string.
    
    Parameters:
    - graph: A networkx graph (nx.Graph) whose nodes have attributes and edges.
    - hints: Optional list of hint tuples to be serialized.
    
    Returns:
    - A JSON string representing the graph structure and hints.
    """
    graph_data = {
        "nodes": {row_col_to_node_id(*node, "AB"): dict(data) for node, data in graph.nodes(data=True)},
        "edges": [(row_col_to_node_id(*u, "AB"), row_col_to_node_id(*v, "AB")) for u, v in graph.edges()]
    }
    
    if hints:
        hints_json = {
            f"player{i+1}": hints[i].tolist() for i in range(3)
        }
        
        graph_data["hints"] = hints_json
    
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

def parse_code_to_graph(graph_hash: str) -> nx.Graph:
    """
    Reconstruct a graph from a hash using the serialized data stored in a JSON file.
    
    Parameters:
    - graph_hash: The hash of the graph, used to lookup the serialized data.
    
    Returns:
    - A networkx graph reconstructed from the stored serialized data.
    
    Raises:
    - FileNotFoundError if the JSON file is not found.
    - KeyError if the hash is not found in the JSON file.
    """
    try:
        with open(f'/opt/container/output/{graph_hash}', 'r') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("'/opt/container/output/{graph_hash} file not found in /opt/container/output/")
 

    graph = nx.Graph()
    graph.add_nodes_from((node_id_to_row_col(node), attrs) for node, attrs in graph_data["nodes"].items())
    graph.add_edges_from((node_id_to_row_col(u), node_id_to_row_col(v)) for u, v in graph_data["edges"])
    # Check and correct player keys in hints
    if "hints" in graph_data and "player0" in graph_data["hints"]:
        corrected_hints = {}
        for key, value in graph_data["hints"].items():
            if key.startswith("player"):
                player_num = int(key[6:])  # Extract the number after "player"
                corrected_key = f"player{player_num + 1}"  # Increment by 1
                corrected_hints[corrected_key] = value
            else:
                corrected_hints[key] = value
        graph_data["hints"] = corrected_hints

    return graph, graph_data.get("hints", [])
def update_neighbors_with_prefix(graph: nx.Graph, attr: str, prefix: str, levels: int = 3) -> None:
    """
    Update nodes with prefixed attributes based on the presence of the attribute in neighboring nodes.
    
    Parameters:
    - graph: A networkx graph (nx.Graph)
    - attr: The attribute to check for
    - prefix: The prefix for the new attribute
    - levels: The number of levels to check (default is 3)
    """
    for level in range(1, levels + 1):
        current_neighbor = '_'.join([prefix] * (level - 1))
        current_attr = f"{current_neighbor}_{attr}" if level > 1 else attr
        new_attr = f"{'_'.join([prefix] * level)}_{attr}"
        updates = {}
        for node in graph.nodes:
            # Check if the current node or any of its neighbors have the attribute set to True
            has_attr = graph.nodes[node].get(current_attr, False) or any(
                graph.nodes[neighbor].get(current_attr, False)
                for neighbor in graph.neighbors(node)
            )
            updates[node] = {new_attr: has_attr}
        
        nx.set_node_attributes(graph, updates)

def enrich_node_attributes(graph: nx.Graph) -> nx.Graph:
    """
    Enriches the graph by adding attributes to each node indicating whether
    the node or its neighbors (up to 3 levels) have a certain boolean attribute set to True.
    
    Parameters:
    - graph: A networkx graph (nx.Graph) with boolean attributes on nodes (one-hot encoded).
    
    Returns:
    - The enriched networkx graph with additional attributes.
    """
    # Identify boolean attributes
    boolean_attributes = set()
    for node, attrs in graph.nodes(data=True):
        boolean_attributes.update(attr for attr, value in attrs.items() if isinstance(value, bool))
    
    # Update attributes for all levels
    for attr in boolean_attributes:
        update_neighbors_with_prefix(graph, attr, "neighbor", levels=3)

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
