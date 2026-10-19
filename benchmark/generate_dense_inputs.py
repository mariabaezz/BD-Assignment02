
import csv
import random
from pathlib import Path

sizes = [500, 750, 1000]

project_root = Path(__file__).resolve().parents[1]
inputs_folder = project_root / "inputs"

inputs_folder.mkdir(exist_ok=True)

for n in sizes:

    rng = random.Random(42 + n)

    for name in ["A", "B"]:

        filename = inputs_folder / f"{name}_{n}.csv"

        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)

            for i in range(n):
                row = [rng.randint(0, 9) for _ in range(n)]
                writer.writerow(row)

        print("Created:", filename.name)