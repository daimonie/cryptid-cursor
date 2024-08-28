import unittest
import numpy as np
from utils.graph_generate_landscape import generate_landscape

class TestGenerateLandscape(unittest.TestCase):
    def test_generate_landscape_shape(self):
        # Test if the generated landscape has the correct shape
        size = 100
        landscape = generate_landscape(size)
        self.assertEqual(landscape.shape, (size, size))

    def test_generate_landscape_range(self):
        # Test if the generated landscape values are within the expected range
        size = 100
        landscape = generate_landscape(size)
        self.assertTrue(np.all(landscape >= 0))
        self.assertTrue(np.all(landscape <= 1))

    def test_generate_landscape_randomness(self):
        # Test if two generated landscapes are different (randomness)
        size = 100
        landscape1 = generate_landscape(size)
        landscape2 = generate_landscape(size)
        self.assertFalse(np.array_equal(landscape1, landscape2))

    def test_generate_landscape_seed(self):
        # Test if using the same seed produces the same landscape
        size = 100
        seed = 42
        landscape1 = generate_landscape(size, seed=seed)
        landscape2 = generate_landscape(size, seed=seed)
        self.assertTrue(np.array_equal(landscape1, landscape2))

    def test_generate_landscape_different_sizes(self):
        # Test if the function works with different sizes
        sizes = [50, 100, 200]
        for size in sizes:
            landscape = generate_landscape(size)
            self.assertEqual(landscape.shape, (size, size))

if __name__ == '__main__':
    unittest.main()
