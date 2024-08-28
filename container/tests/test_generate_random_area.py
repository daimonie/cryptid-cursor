import unittest
from .utils.graph_generate_random_area import generate_random_area

class TestGenerateRandomArea(unittest.TestCase):

    def test_generate_random_area_output_shape(self):
        width, height = 10, 10
        area = generate_random_area(width, height)
        self.assertEqual(len(area), height)
        self.assertEqual(len(area[0]), width)

    def test_generate_random_area_values(self):
        width, height = 5, 5
        area = generate_random_area(width, height)
        for row in area:
            for cell in row:
                self.assertIn(cell, [0, 1])

    def test_generate_random_area_different_outputs(self):
        width, height = 8, 8
        area1 = generate_random_area(width, height)
        area2 = generate_random_area(width, height)
        self.assertNotEqual(area1, area2)

    def test_generate_random_area_edge_cases(self):
        # Test with small dimensions
        area_small = generate_random_area(1, 1)
        self.assertEqual(len(area_small), 1)
        self.assertEqual(len(area_small[0]), 1)

        # Test with large dimensions
        width, height = 100, 100
        area_large = generate_random_area(width, height)
        self.assertEqual(len(area_large), height)
        self.assertEqual(len(area_large[0]), width)

if __name__ == '__main__':
    unittest.main()
