
import subprocess
import csv
from pathlib import Path

sizes = [500, 750, 1000]
repetitions = 5
block_size = 128

project_root = Path(__file__).resolve().parents[1]
executable = project_root / "src" / "c" / "run_matrix"
results_file = project_root / "results" / "dense_c_large_results.csv"

methods = ["basic", "reordered", "blocked"]

with open(results_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "method",
        "matrix_size",
        "repetition",
        "execution_time_seconds",
        "checksum"
    ])

    for n in sizes:
        for method in methods:
            for repetition in range(1, repetitions + 1):

                result = subprocess.run(
                    [
                        str(executable),
                        method,
                        str(n),
                        str(block_size)
                    ],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    check=True
                )

                elapsed_time, checksum = result.stdout.strip().split(",")

                writer.writerow([
                    method,
                    n,
                    repetition,
                    elapsed_time,
                    checksum
                ])

                print(
                    "Method:", method,
                    "| Size:", n,
                    "| Repetition:", repetition,
                    "| Time:", elapsed_time,
                    "| Checksum:", checksum
                )
