import unittest
import networkx as nx
from utils.graph_generate_landscape import ( 
    assign_random_attribute,
    add_edges_for_node,
    get_hexagonal_neighbors,
    add_hexagonal_edges,
    generate_hexagonal_grid_graph
)

class TestGraphGenerateLandscape(unittest.TestCase):
 
    def test_assign_random_attribute(self):
        attributes = ['is_Swamp', 'is_Forest', 'is_Water', 'is_Mountain', 'is_Desert']
        result = assign_random_attribute(attributes)
        self.assertEqual(sum(result.values()), 1)
        self.assertEqual(len(result), len(attributes))

    # Test if add_edges_for_node function adds correct number of edges for different positions
    def test_add_edges_for_node(self): 
        G = nx.Graph()
        
        # Check if all expected nodes exist
        expected_nodes = ['AA', 'AB', 'AC', 'BA', 'BB', 'BC', 'CA', 'CB', 'CC']
        G.add_nodes_from(expected_nodes)
        
        for node in G.nodes:
            add_edges_for_node(G, node, 3, 3)
        
        self.assertEqual(set(G.nodes()), set(expected_nodes))
        
        # Check connections for first row (not indented)
        self.assertEqual(set(G.neighbors('AA')), {'AB', 'BA'})
        self.assertEqual(set(G.neighbors('AB')), {'AA', 'AC', 'BA', 'BB'})
        self.assertEqual(set(G.neighbors('AC')), {'AB', 'BB', 'BC'})
        
        # Check connections for last row (not indented)
        self.assertEqual(set(G.neighbors('CA')), {'BA', 'CB'})
        self.assertEqual(set(G.neighbors('CC')), {'CB', 'BB', 'BC'})
        
        # Check connections for second row (indented)
        self.assertEqual(set(G.neighbors('BA')), {'AA', 'AB', 'BB', 'CA', 'CB'})
        self.assertEqual(set(G.neighbors('BB')), {'AB', 'AC', 'BA', 'BC', 'CB', 'CC'})
        self.assertEqual(set(G.neighbors('BC')), {'AC', 'BB', 'CC'})
        
        # Check connections for third row (not indented)
        self.assertEqual(set(G.neighbors('CA')), {'BA', 'CB'})
        self.assertEqual(set(G.neighbors('CB')), {'BA', 'BB', 'CA', 'CC'})
        self.assertEqual(set(G.neighbors('CC')), {'BB', 'BC', 'CB'})
        
        # Check total number of edges
        self.assertEqual(len(G.edges), 16)
        

    def test_generate_hexagonal_grid_graph(self):
        G = generate_hexagonal_grid_graph(3, 3)
        self.assertEqual(len(G.nodes), 9)
        self.assertEqual(len(G.edges), 16)