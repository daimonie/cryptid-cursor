import unittest
from container.utils.graph_utils import (
    create_graph,
    add_edge,
    get_neighbors,
    has_path,
    shortest_path
)

class TestGraphUtils(unittest.TestCase):

    def setUp(self):
        self.graph = create_graph()

    def test_create_graph(self):
        self.assertIsInstance(self.graph, dict)
        self.assertEqual(len(self.graph), 0)

    def test_add_edge(self):
        add_edge(self.graph, 'A', 'B')
        add_edge(self.graph, 'A', 'C')
        add_edge(self.graph, 'B', 'D')

        self.assertIn('A', self.graph)
        self.assertIn('B', self.graph)
        self.assertIn('C', self.graph)
        self.assertIn('D', self.graph)
        self.assertIn('B', self.graph['A'])
        self.assertIn('C', self.graph['A'])
        self.assertIn('D', self.graph['B'])

    def test_get_neighbors(self):
        add_edge(self.graph, 'A', 'B')
        add_edge(self.graph, 'A', 'C')
        add_edge(self.graph, 'B', 'D')

        neighbors = get_neighbors(self.graph, 'A')
        self.assertIn('B', neighbors)
        self.assertIn('C', neighbors)
        self.assertNotIn('D', neighbors)

    def test_has_path(self):
        add_edge(self.graph, 'A', 'B')
        add_edge(self.graph, 'B', 'C')
        add_edge(self.graph, 'C', 'D')

        self.assertTrue(has_path(self.graph, 'A', 'D'))
        self.assertTrue(has_path(self.graph, 'A', 'C'))
        self.assertFalse(has_path(self.graph, 'B', 'A'))
        self.assertFalse(has_path(self.graph, 'A', 'E'))

    def test_shortest_path(self):
        add_edge(self.graph, 'A', 'B')
        add_edge(self.graph, 'A', 'C')
        add_edge(self.graph, 'B', 'D')
        add_edge(self.graph, 'C', 'D')
        add_edge(self.graph, 'D', 'E')

        path = shortest_path(self.graph, 'A', 'E')
        self.assertIn(path, [['A', 'B', 'D', 'E'], ['A', 'C', 'D', 'E']])

        path = shortest_path(self.graph, 'A', 'D')
        self.assertIn(path, [['A', 'B', 'D'], ['A', 'C', 'D']])

        path = shortest_path(self.graph, 'A', 'F')
        self.assertIsNone(path)

if __name__ == '__main__':
    unittest.main()
