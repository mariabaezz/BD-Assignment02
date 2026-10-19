import unittest

from src.dense_basic import multiply_basic
from src.dense_reordered import multiply_reordered
from src.dense_blocked import multiply_blocked


class TestDenseMultiplication(unittest.TestCase):

    def check_all_methods(self, A, B, expected):
        self.assertEqual(multiply_basic(A, B), expected)
        self.assertEqual(multiply_reordered(A, B), expected)

        for block_size in [1, 2, 3, 4]:
            self.assertEqual(
                multiply_blocked(A, B, block_size),
                expected
            )

    def test_known_result(self):
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]

        expected = [[19, 22], [43, 50]]

        self.check_all_methods(A, B, expected)

    def test_identity(self):
        A = [[2, 5], [7, 3]]
        I = [[1, 0], [0, 1]]

        self.check_all_methods(A, I, A)

    def test_zero_matrix(self):
        A = [[1, 2], [3, 4]]
        Z = [[0, 0], [0, 0]]

        self.check_all_methods(A, Z, Z)

    def test_non_multiple_block_size(self):
        A = [[1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]]

        I = [[1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]]

        self.check_all_methods(A, I, A)


if __name__ == "__main__":
    unittest.main()
