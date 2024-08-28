import pytest
import networkx as nx
from utils.graph_generate_random_area import (
    initialize_node_attributes,
    select_random_start_node,
    expand_connected_area,
    assign_attribute_to_nodes,
    add_connected_area_attribute
)

@pytest.fixture
def sample_graph():
    return nx.hexagonal_lattice_graph(3, 3)

def test_initialize_node_attributes(sample_graph):
    initialize_node_attributes(sample_graph, 'test_attr')
    assert all(sample_graph.nodes[node]['test_attr'] == False for node in sample_graph.nodes)

def test_select_random_start_node(sample_graph):
    start_node = select_random_start_node(sample_graph)
    assert start_node in sample_graph.nodes

def test_expand_connected_area(sample_graph):
    start_node = (0, 0)
    connected_area = expand_connected_area(sample_graph, start_node, 5)
    assert len(connected_area) == 5
    assert start_node in connected_area
    assert all(nx.has_path(sample_graph.subgraph(connected_area), start_node, node) for node in connected_area)

def test_assign_attribute_to_nodes(sample_graph):
    nodes_to_assign = {(0, 0), (0, 1), (1, 0)}
    assign_attribute_to_nodes(sample_graph, nodes_to_assign, 'test_attr')
    assert all(sample_graph.nodes[node]['test_attr'] == True for node in nodes_to_assign)
    assert all(sample_graph.nodes[node]['test_attr'] == False for node in sample_graph.nodes if node not in nodes_to_assign)

def test_add_connected_area_attribute(sample_graph):
    add_connected_area_attribute(sample_graph, 'is_Forest', 5)
    forest_nodes = [node for node, attr in sample_graph.nodes(data=True) if attr['is_Forest']]
    assert len(forest_nodes) == 5
    assert nx.is_connected(sample_graph.subgraph(forest_nodes))

def test_add_connected_area_attribute_error(sample_graph):
    with pytest.raises(ValueError):
        add_connected_area_attribute(sample_graph, 'is_Mountain', 100)

def test_expand_connected_area_full_graph(sample_graph):
    start_node = (0, 0)
    connected_area = expand_connected_area(sample_graph, start_node, len(sample_graph.nodes))
    assert len(connected_area) == len(sample_graph.nodes)
    assert all(node in connected_area for node in sample_graph.nodes)

def test_add_connected_area_attribute_single_node():
    G = nx.Graph()
    G.add_node(0)
    add_connected_area_attribute(G, 'is_Lake', 1)
    assert G.nodes[0]['is_Lake'] == True

def test_add_connected_area_attribute_multiple_calls(sample_graph):
    add_connected_area_attribute(sample_graph, 'is_Forest', 3)
    add_connected_area_attribute(sample_graph, 'is_Lake', 4)
    forest_nodes = [node for node, attr in sample_graph.nodes(data=True) if attr['is_Forest']]
    lake_nodes = [node for node, attr in sample_graph.nodes(data=True) if attr['is_Lake']]
    assert len(forest_nodes) == 3
    assert len(lake_nodes) == 4
    assert nx.is_connected(sample_graph.subgraph(forest_nodes))
    assert nx.is_connected(sample_graph.subgraph(lake_nodes))