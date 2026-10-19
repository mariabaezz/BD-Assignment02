
import unittest

from src.dense_basic import multiply_basic
from src.dense_reordered import multiply_reordered


class TestDenseMultiplication(unittest.TestCase):

    def test_known_result(self):
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]

        expected = [[19, 22], [43, 50]]

        self.assertEqual(multiply_basic(A, B), expected)
        self.assertEqual(multiply_reordered(A, B), expected)

    def test_identity(self):
        A = [[2, 5], [7, 3]]
        I = [[1, 0], [0, 1]]

        self.assertEqual(multiply_basic(A, I), A)
        self.assertEqual(multiply_reordered(A, I), A)

    def test_zero_matrix(self):
        A = [[1, 2], [3, 4]]
        Z = [[0, 0], [0, 0]]

        self.assertEqual(multiply_basic(A, Z), Z)
        self.assertEqual(multiply_reordered(A, Z), Z)


if __name__ == "__main__":
    unittest.main()
