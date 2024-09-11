import unittest
import networkx as nx
from utils.graph_utils import (
    serialize_graph,
    generate_unique_code,
    parse_code_to_graph,
    enrich_node_attributes,
    filter_nodes_by_attributes,
    create_graph
)

class TestGraphUtils(unittest.TestCase):

    def setUp(self):
        self.test_graph = create_graph()

    def test_serialize_graph(self):
        serialized = serialize_graph(self.test_graph)
        self.assertIsInstance(serialized, str)
        self.assertIn('"nodes":', serialized)
        self.assertIn('"edges":', serialized)

    def test_generate_unique_code(self):
        serialized = serialize_graph(self.test_graph)
        code = generate_unique_code(serialized)
        self.assertEqual(len(code), 64)  # SHA-256 hash is 64 characters long

    def test_parse_code_to_graph(self):
        serialized = serialize_graph(self.test_graph)
        code = generate_unique_code(serialized)
        reconstructed = parse_code_to_graph(code, {code: serialized})
        self.assertEqual(list(self.test_graph.nodes()), list(reconstructed.nodes()))
        self.assertEqual(list(self.test_graph.edges()), list(reconstructed.edges()))
    def test_line_graph_attributes(self):
        G = nx.Graph()
        G.add_nodes_from([
            ('A', {"is_swamp": True}),
            ('B', {"is_forest": True}),
            ('C', {"is_mountain": True}),
            ('D', {"is_desert": True})
        ])
        G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D')])

        self.assertTrue(G.nodes['A']['is_swamp'])
        self.assertTrue(G.nodes['B']['is_forest'])
        self.assertTrue(G.nodes['C']['is_mountain'])
        self.assertTrue(G.nodes['D']['is_desert'])
        with self.assertRaises(KeyError):
            G.nodes['A']['is_forest']
        with self.assertRaises(KeyError):
            G.nodes['B']['is_swamp']
        with self.assertRaises(KeyError):
            G.nodes['C']['is_desert']
        with self.assertRaises(KeyError):
            G.nodes['D']['is_mountain']

        enriched = enrich_node_attributes(G)
        # Test direct attributes
        self.assertTrue(enriched.nodes['A']['is_swamp'])
        self.assertTrue(enriched.nodes['B']['is_forest'])
        self.assertTrue(enriched.nodes['C']['is_mountain'])
        self.assertTrue(enriched.nodes['D']['is_desert'])
        with self.assertRaises(KeyError):
            enriched.nodes['A']['is_forest']
        with self.assertRaises(KeyError):
            enriched.nodes['B']['is_swamp']
        with self.assertRaises(KeyError):
            enriched.nodes['C']['is_desert']
        with self.assertRaises(KeyError):
            enriched.nodes['D']['is_mountain']
        # Test neighbor attributes A
        self.assertTrue(enriched.nodes['A']['neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['A']['neighbor_is_swamp']) 
        self.assertFalse(enriched.nodes['A']['neighbor_is_desert']) 
        self.assertFalse(enriched.nodes['A']['neighbor_is_mountain']) 
        self.assertTrue(enriched.nodes['A']['neighbor_neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['A']['neighbor_neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['A']['neighbor_neighbor_is_mountain'])
        self.assertFalse(enriched.nodes['A']['neighbor_neighbor_is_desert']) 
        self.assertTrue(enriched.nodes['A']['neighbor_neighbor_neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['A']['neighbor_neighbor_neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['A']['neighbor_neighbor_neighbor_is_mountain'])
        self.assertTrue(enriched.nodes['A']['neighbor_neighbor_neighbor_is_desert']) 

        # Test neighbor attributes B
        self.assertTrue(enriched.nodes['B']['neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['B']['neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['B']['neighbor_is_mountain']) 
        self.assertFalse(enriched.nodes['B']['neighbor_is_desert']) 
        self.assertTrue(enriched.nodes['B']['neighbor_neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['B']['neighbor_neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['B']['neighbor_neighbor_is_mountain'])
        self.assertTrue(enriched.nodes['B']['neighbor_neighbor_is_desert']) 
        self.assertTrue(enriched.nodes['B']['neighbor_neighbor_neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['B']['neighbor_neighbor_neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['B']['neighbor_neighbor_neighbor_is_mountain'])
        self.assertTrue(enriched.nodes['B']['neighbor_neighbor_neighbor_is_desert']) 

        # Test neighbor attributes C
        self.assertTrue(enriched.nodes['C']['neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['C']['neighbor_is_mountain']) 
        self.assertTrue(enriched.nodes['C']['neighbor_is_desert']) 
        self.assertFalse(enriched.nodes['C']['neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['C']['neighbor_neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['C']['neighbor_neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['C']['neighbor_neighbor_is_mountain'])
        self.assertTrue(enriched.nodes['C']['neighbor_neighbor_is_desert']) 
        self.assertTrue(enriched.nodes['C']['neighbor_neighbor_neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['C']['neighbor_neighbor_neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['C']['neighbor_neighbor_neighbor_is_mountain'])
        self.assertTrue(enriched.nodes['C']['neighbor_neighbor_neighbor_is_desert']) 

        # Test neighbor attributes D
        self.assertTrue(enriched.nodes['D']['neighbor_is_mountain']) 
        self.assertTrue(enriched.nodes['D']['neighbor_is_desert']) 
        self.assertFalse(enriched.nodes['D']['neighbor_is_forest']) 
        self.assertFalse(enriched.nodes['D']['neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['D']['neighbor_neighbor_is_forest']) 
        self.assertFalse(enriched.nodes['D']['neighbor_neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['D']['neighbor_neighbor_is_mountain'])
        self.assertTrue(enriched.nodes['D']['neighbor_neighbor_is_desert']) 
        self.assertTrue(enriched.nodes['D']['neighbor_neighbor_neighbor_is_swamp']) 
        self.assertTrue(enriched.nodes['D']['neighbor_neighbor_neighbor_is_forest']) 
        self.assertTrue(enriched.nodes['D']['neighbor_neighbor_neighbor_is_mountain'])
        self.assertTrue(enriched.nodes['D']['neighbor_neighbor_neighbor_is_desert']) 
 

    def test_enrich_node_attributes(self):
        enriched = enrich_node_attributes(self.test_graph)

        # Check node 'a'
        self.assertTrue(enriched.nodes['a']['attr1'])
        self.assertFalse(enriched.nodes['a']['attr2'])
        self.assertTrue(enriched.nodes['a']['neighbor_attr2'])
        self.assertTrue(enriched.nodes['a']['neighbor_attr1'])
        self.assertTrue(enriched.nodes['a']['neighbor_neighbor_attr1'])
        self.assertTrue(enriched.nodes['a']['neighbor_neighbor_attr2'])
        self.assertTrue(enriched.nodes['a']['neighbor_neighbor_neighbor_attr1'])
        self.assertTrue(enriched.nodes['a']['neighbor_neighbor_neighbor_attr2'])
        
        # Check node 'b'
        self.assertFalse(enriched.nodes['b']['attr1'])
        self.assertTrue(enriched.nodes['b']['attr2'])
        self.assertTrue(enriched.nodes['b']['neighbor_attr1'])
        self.assertTrue(enriched.nodes['b']['neighbor_attr2'])
        self.assertTrue(enriched.nodes['b']['neighbor_neighbor_attr1'])
        self.assertTrue(enriched.nodes['b']['neighbor_neighbor_attr2'])
        self.assertTrue(enriched.nodes['b']['neighbor_neighbor_neighbor_attr1'])
        self.assertTrue(enriched.nodes['b']['neighbor_neighbor_neighbor_attr2'])
        
        # Check node 'c'
        self.assertTrue(enriched.nodes['c']['attr1'])
        self.assertTrue(enriched.nodes['c']['attr2'])
        self.assertTrue(enriched.nodes['c']['neighbor_attr1'])
        self.assertTrue(enriched.nodes['c']['neighbor_attr2'])
        self.assertTrue(enriched.nodes['c']['neighbor_neighbor_attr1'])
        self.assertTrue(enriched.nodes['c']['neighbor_neighbor_attr2'])
        self.assertTrue(enriched.nodes['c']['neighbor_neighbor_neighbor_attr1'])
        self.assertTrue(enriched.nodes['c']['neighbor_neighbor_neighbor_attr2'])

    def test_filter_nodes_by_attributes(self):
        filtered = filter_nodes_by_attributes(self.test_graph, "attr1", True)
        self.assertEqual(set(filtered), {'a', 'c'})

    def test_filter_nodes_by_attributes_multiple(self):
        filtered = filter_nodes_by_attributes(self.test_graph, "attr1", True, "attr2", True)
        self.assertEqual(set(filtered), {'c'})

    def test_filter_nodes_by_attributes_no_match(self):
        filtered = filter_nodes_by_attributes(self.test_graph, "attr1", False, "attr2", False)
        self.assertEqual(filtered, [])

    def test_filter_nodes_by_attributes_invalid_args(self):
        with self.assertRaises(ValueError):
            filter_nodes_by_attributes(self.test_graph, "attr1")

if __name__ == '__main__':
    unittest.main()