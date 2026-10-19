
import subprocess
import unittest
from pathlib import Path


project_root = Path(__file__).resolve().parents[1]
executable = project_root / "src" / "c" / "run_matrix"

expected_checksums = {
    50: 2580329,
    100: 20043070,
    150: 68563585,
    200: 161354779,
    250: 315567802
}


class TestDenseC(unittest.TestCase):

    def test_all_methods(self):

        for n, expected in expected_checksums.items():

            for method in ["basic", "reordered", "blocked"]:

                result = subprocess.run(
                    [
                        str(executable),
                        method,
                        str(n),
                        "32"
                    ],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    check=True
                )

                elapsed, checksum = result.stdout.strip().split(",")

                self.assertEqual(int(checksum), expected)
                self.assertGreaterEqual(float(elapsed), 0)


if __name__ == "__main__":
    unittest.main()
