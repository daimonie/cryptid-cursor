import unittest
from  utils.graph_generate_random_area import add_connected_area_attribute

class TestGenerateRandomArea(unittest.TestCase):

    def test_add_connected_area_attribute_output_shape(self):
        width, height = 10, 10
        area = add_connected_area_attribute(width, height)
        self.assertEqual(len(area), height)
        self.assertEqual(len(area[0]), width)

    def test_add_connected_area_attribute_values(self):
        width, height = 5, 5
        area = add_connected_area_attribute(width, height)
        for row in area:
            for cell in row:
                self.assertIn(cell, [0, 1])

    def test_add_connected_area_attribute_different_outputs(self):
        width, height = 8, 8
        area1 = add_connected_area_attribute(width, height)
        area2 = add_connected_area_attribute(width, height)
        self.assertNotEqual(area1, area2)

    def test_add_connected_area_attribute_edge_cases(self):
        # Test with small dimensions
        area_small = add_connected_area_attribute(1, 1)
        self.assertEqual(len(area_small), 1)
        self.assertEqual(len(area_small[0]), 1)

        # Test with large dimensions
        width, height = 100, 100
        area_large = add_connected_area_attribute(width, height)
        self.assertEqual(len(area_large), height)
        self.assertEqual(len(area_large[0]), width)

if __name__ == '__main__':
    unittest.main()
