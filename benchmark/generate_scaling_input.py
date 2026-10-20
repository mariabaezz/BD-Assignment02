
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "inputs"

if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python3 -m benchmark.generate_scaling_input SIZE"
    )

n = int(sys.argv[1])

if n <= 0 or n > 2000:
    raise ValueError("Size must be between 1 and 2000")

INPUTS.mkdir(parents=True, exist_ok=True)

rng = random.Random(42 + n)

for name in ["A", "B"]:

    filename = INPUTS / f"{name}_{n}.csv"

    if filename.exists():
        raise FileExistsError(
            f"{filename} already exists. Refusing to overwrite."
        )

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        for _ in range(n):
            writer.writerow([
                rng.randint(0, 9) for _ in range(n)
            ])

    print("Created:", filename)
