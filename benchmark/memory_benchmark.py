
import subprocess
import csv
from pathlib import Path

sizes = [50, 100, 150, 200, 250, 500, 750, 1000]
methods = ["basic", "reordered", "blocked"]
repetitions = 5
block_size = 128

project_root = Path(__file__).resolve().parents[1]
executable = project_root / "src" / "c" / "run_matrix"
results_file = project_root / "results" / "dense_memory_results.csv"

with open(results_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "method",
        "matrix_size",
        "repetition",
        "peak_rss_bytes"
    ])

    for n in sizes:
        for method in methods:
            for repetition in range(1, repetitions + 1):

                result = subprocess.run(
                    [
                        "/usr/bin/time",
                        "-l",
                        str(executable),
                        method,
                        str(n),
                        str(block_size)
                    ],
                    cwd=project_root,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    print("ERROR:")
                    print(result.stderr)
                    raise RuntimeError("Memory benchmark failed")

                memory = None

                for line in result.stderr.splitlines():
                    if "maximum resident set size" in line:
                        memory = int(line.split()[0])
                        break

                if memory is None:
                    raise ValueError("Peak RSS not found")

                writer.writerow([
                    method,
                    n,
                    repetition,
                    memory
                ])

                print(
                    "Method:", method,
                    "| Size:", n,
                    "| Repetition:", repetition,
                    "| Peak RSS:", memory, "bytes"
                )

print("Results saved to:", results_file)
