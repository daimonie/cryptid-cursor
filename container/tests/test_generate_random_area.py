import pytest
import networkx as nx
from utils.graph_generate_random_area import (
    initialize_node_attributes,
    select_random_start_node,
    expand_connected_area,
    assign_attribute_to_nodes,
)

def test_initialize_node_attributes():
    G = nx.Graph()
    G.add_nodes_from([1, 2, 3])
    initialize_node_attributes(G, 'test_attr')
    
    for node in G.nodes:
        assert 'test_attr' in G.nodes[node]
        assert G.nodes[node]['test_attr'] == False

def test_select_random_start_node():
    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4, 5])
    
    selected_node = select_random_start_node(G)
    assert selected_node in G.nodes

def test_expand_connected_area():
    G = nx.grid_2d_graph(5, 5)  # 5x5 grid graph
    start_node = (2, 2)  # Center node
    N = 7
    
    connected_area = expand_connected_area(G, start_node, N)
    
    assert len(connected_area) == N
    assert start_node in connected_area
    assert all(nx.has_path(G.subgraph(connected_area), start_node, node) for node in connected_area)

def test_assign_attribute_to_nodes():
    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4, 5])
    nodes_to_assign = {2, 4}
    attribute = 'test_attr'
    
    assign_attribute_to_nodes(G, nodes_to_assign, attribute)
    
    for node in G.nodes:
        if node in nodes_to_assign:
            assert G.nodes[node][attribute] == True
        else:
            assert G.nodes[node][attribute] == False

def test_integration():
    G = nx.grid_2d_graph(10, 10)
    attribute = 'test_attr'
    N = 15
    
    initialize_node_attributes(G, attribute)
    start_node = select_random_start_node(G)
    connected_area = expand_connected_area(G, start_node, N)
    assign_attribute_to_nodes(G, connected_area, attribute)
    
    assert sum(1 for node in G.nodes if G.nodes[node][attribute]) == N
    assert all(nx.has_path(G.subgraph(connected_area), start_node, node) for node in connected_area)
