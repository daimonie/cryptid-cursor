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

    def test_create_graph(self):
        graph = create_graph()
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)
        self.assertTrue(graph.nodes['a']['attr1'])
        self.assertFalse(graph.nodes['a']['attr2'])
        self.assertFalse(graph.nodes['b']['attr1'])
        self.assertTrue(graph.nodes['b']['attr2'])
        self.assertTrue(graph.nodes['c']['attr1'])
        self.assertTrue(graph.nodes['c']['attr2'])

    def test_serialize_graph(self):
        serialized = serialize_graph(self.test_graph)
        self.assertIsInstance(serialized, str)
        self.assertIn('"nodes":', serialized)
        self.assertIn('"edges":', serialized)

    def test_generate_unique_code(self):
        serialized = serialize_graph(self.test_graph)
        code1 = generate_unique_code(serialized)
        code2 = generate_unique_code(serialized)
        self.assertEqual(code1, code2)
        self.assertEqual(len(code1), 64)  # SHA-256 hash length

    def test_parse_code_to_graph(self):
        serialized = serialize_graph(self.test_graph)
        code = generate_unique_code(serialized)
        reconstructed = parse_code_to_graph(code, {code: serialized})
            
        # Raise an exception with node and edge counts
        raise Exception(f"Serialized graph: {len(self.test_graph.nodes)} nodes, {len(self.test_graph.edges)} edges. "
                        f"Reconstructed graph: {len(reconstructed.nodes)} nodes, {len(reconstructed.edges)} edges.")

        self.assertEqual(len(self.test_graph.nodes), len(reconstructed.nodes))
        self.assertEqual(len(self.test_graph.edges), len(reconstructed.edges))
        self.assertEqual(dict(self.test_graph.nodes(data=True)), dict(reconstructed.nodes(data=True)))

    def test_parse_code_to_graph_key_error(self):
        with self.assertRaises(KeyError):
            parse_code_to_graph("nonexistent_hash", {})

    def test_enrich_node_attributes(self):
        enriched = enrich_node_attributes(self.test_graph)
        self.assertTrue(enriched.nodes['a']['neighbors_attr2'])
        self.assertFalse(enriched.nodes['a']['neighbors_attr1'])
        self.assertTrue(enriched.nodes['a']['neighbors_of_neighbors_attr1'])
        self.assertTrue(enriched.nodes['a']['neighbors_of_neighbors_attr2'])
        self.assertTrue(enriched.nodes['a']['neighbors_of_neighbors_of_neighbors_attr1'])
        self.assertTrue(enriched.nodes['a']['neighbors_of_neighbors_of_neighbors_attr2'])

    def test_filter_nodes_by_attributes(self):
        filtered = filter_nodes_by_attributes(self.test_graph, 'attr1', True)
        self.assertEqual(set(filtered), {'a', 'c'})

        filtered = filter_nodes_by_attributes(self.test_graph, 'attr1', True, 'attr2', True)
        self.assertEqual(filtered, ['c'])

    def test_filter_nodes_by_attributes_invalid_args(self):
        with self.assertRaises(ValueError):
            filter_nodes_by_attributes(self.test_graph, 'attr1')

if __name__ == '__main__':
    unittest.main()