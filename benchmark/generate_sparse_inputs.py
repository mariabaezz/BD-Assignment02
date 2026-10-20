
import csv
import random
from pathlib import Path

sizes = [100, 250, 500]
sparsities = [0, 50, 80, 90, 95, 99]
seed = 42

project_root = Path(__file__).resolve().parents[1]
output_folder = project_root / "inputs" / "sparse"

output_folder.mkdir(parents=True, exist_ok=True)


def generate_matrix(n, sparsity, rng):
    total = n * n
    nnz = round(total * (100 - sparsity) / 100)

    matrix = [[0] * n for _ in range(n)]

    # Select exactly nnz different positions
    positions = rng.sample(range(total), nnz)

    for position in positions:
        i = position // n
        j = position % n

        matrix[i][j] = rng.randint(1, 9)

    return matrix


for n in sizes:
    for sparsity in sparsities:

        for name, offset in [("A", 0), ("B", 1)]:
            rng = random.Random(seed + n * 1000 + sparsity * 10 + offset)

            matrix = generate_matrix(n, sparsity, rng)

            filename = (
                output_folder /
                f"{name}_{n}_s{sparsity}.csv"
            )

            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(matrix)

            nnz = sum(value != 0 for row in matrix for value in row)

            print(
                filename.name,
                "| Nonzeros:", nnz,
                "| Density:", round(100 * nnz / (n * n), 2), "%"
            )
