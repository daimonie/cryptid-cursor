import unittest
import networkx as nx
from utils.graph_utils import serialize_graph, generate_unique_code, parse_code_to_graph
from utils.graph_utils import create_graph

class TestGraphUtils(unittest.TestCase):

    def setUp(self):
        self.graph = create_graph()

    def test_serialize_graph(self):
        serialized = serialize_graph(self.graph)
        self.assertIsInstance(serialized, str)
        self.assertIn("nodes", serialized)
        self.assertIn("edges", serialized)

    def test_generate_unique_code(self):
        serialized = serialize_graph(self.graph)
        code = generate_unique_code(serialized)
        self.assertIsInstance(code, str)
        self.assertEqual(len(code), 32)  # MD5 hash is 32 characters long

    def test_parse_code_to_graph(self):
        serialized = serialize_graph(self.graph)
        code = generate_unique_code(serialized)
        parsed_graph, _ = parse_code_to_graph(code)
        
        self.assertIsInstance(parsed_graph, nx.Graph)
        self.assertEqual(len(parsed_graph.nodes), 2)
        self.assertEqual(len(parsed_graph.edges), 1)
        self.assertTrue(parsed_graph.nodes[1]['is_forest'])
        self.assertFalse(parsed_graph.nodes[1]['is_water'])
        self.assertTrue(parsed_graph.nodes[2]['is_desert'])
        self.assertFalse(parsed_graph.nodes[2]['is_mountain'])

if __name__ == '__main__':
    unittest.main()
