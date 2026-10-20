
import subprocess
import csv
from pathlib import Path
from statistics import median

n = 250
block_sizes = [8, 16, 32, 64, 128]
repetitions = 5

project_root = Path(__file__).resolve().parents[1]
executable = project_root / "src" / "c" / "run_matrix"
results_file = project_root / "results" / "block_sizes_c.csv"

reference = subprocess.run(
    [
        str(executable),
        "basic",
        str(n),
        "32"
    ],
    cwd=project_root,
    capture_output=True,
    text=True,
    check=True
)

_, expected_checksum = reference.stdout.strip().split(",")
expected_checksum = int(expected_checksum)

with open(results_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "matrix_size",
        "block_size",
        "repetition",
        "execution_time_seconds",
        "checksum"
    ])

    for block_size in block_sizes:
        times = []

        for repetition in range(1, repetitions + 1):

            result = subprocess.run(
                [
                    str(executable),
                    "blocked",
                    str(n),
                    str(block_size)
                ],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )

            elapsed_time, checksum = result.stdout.strip().split(",")

            if int(checksum) != expected_checksum:
                raise ValueError(
                    f"Incorrect result for block size {block_size}"
                )

            times.append(float(elapsed_time))

            writer.writerow([
                n,
                block_size,
                repetition,
                elapsed_time,
                checksum
            ])

        print(
            "Block size:", block_size,
            "| Median:", median(times), "seconds"
        )

print("Results saved to:", results_file)
