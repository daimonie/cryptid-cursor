import unittest
import networkx as nx
import json
import builtins
from unittest import mock
from utils.graph_utils import serialize_graph, generate_unique_code, parse_code_to_graph, enrich_node_attributes, filter_nodes_by_attributes
from utils.graph_generate_landscape import generate_hexagonal_grid_graph

class TestGraphUtils(unittest.TestCase):

    def setUp(self):
        self.graph = generate_hexagonal_grid_graph(8, 11)

    def test_serialize_graph(self):
        serialized = serialize_graph(self.graph)
        self.assertIsInstance(serialized, str)
        data = json.loads(serialized)
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertEqual(len(data["nodes"]), 88)  # 8 * 11 = 88 nodes
        self.assertGreater(len(data["edges"]), 0)  # There should be edges

    def test_generate_unique_code(self):
        serialized = serialize_graph(self.graph)
        code = generate_unique_code(serialized)
        self.assertIsInstance(code, str)
        self.assertEqual(len(code), 64)  # SHA-256 hash is 64 characters long

    def test_parse_code_to_graph(self):
        serialized = serialize_graph(self.graph)
        code = generate_unique_code(serialized)
        
        # Mocking the file read operation
        original_open = builtins.open
        builtins.open = lambda *args, **kwargs: mock.mock_open(read_data=serialized)(*args, **kwargs)
        
        try:
            parsed_graph, _ = parse_code_to_graph(code)
            
            self.assertIsInstance(parsed_graph, nx.Graph)
            self.assertEqual(len(parsed_graph.nodes), 88)
            self.assertGreater(len(parsed_graph.edges), 0)
            # Check if nodes have the expected attributes
            for node in parsed_graph.nodes:
                attrs = parsed_graph.nodes[node]
                self.assertTrue(any(attrs[f'is_{terrain}'] for terrain in ['swamp', 'forest', 'water', 'mountain', 'desert']))
        finally:
            builtins.open = original_open

    def test_enrich_node_attributes(self):
        enriched_graph = enrich_node_attributes(self.graph)
        for node in enriched_graph.nodes:
            attrs = enriched_graph.nodes[node]
            self.assertTrue(any(attrs[f'neighbor_is_{terrain}'] for terrain in ['swamp', 'forest', 'water', 'mountain', 'desert']))

    def test_filter_nodes_by_attributes(self):
        for terrain in ['swamp', 'forest', 'water', 'mountain', 'desert']:
            filtered_nodes = filter_nodes_by_attributes(self.graph, f'is_{terrain}', True)
            self.assertGreater(len(filtered_nodes), 0)
            for node in filtered_nodes:
                self.assertTrue(self.graph.nodes[node][f'is_{terrain}'])

if __name__ == '__main__':
    unittest.main()
