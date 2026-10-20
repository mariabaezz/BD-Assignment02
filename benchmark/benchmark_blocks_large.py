
import csv
import subprocess
from pathlib import Path
from statistics import median

sizes = [500, 1000]
block_sizes = [16, 32, 64, 128, 256, 512]
repetitions = 5

project_root = Path(__file__).resolve().parents[1]
executable = project_root / "src" / "c" / "run_matrix"
results_file = project_root / "results" / "block_sizes_large.csv"

# Store the raw results
with open(results_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "matrix_size",
        "block_size",
        "repetition",
        "execution_time_seconds",
        "checksum"
    ])

    for n in sizes:

        # Calculate the reference checksum once per size
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

        _, expected_checksum = (
            reference.stdout.strip().split(",")
        )

        expected_checksum = int(expected_checksum)

        print(f"\nMatrix size: {n}")
        print(f"Expected checksum: {expected_checksum}")

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

                elapsed_time, checksum = (
                    result.stdout.strip().split(",")
                )

                if int(checksum) != expected_checksum:
                    raise ValueError(
                        f"Incorrect result: n={n}, "
                        f"block={block_size}"
                    )

                elapsed_time = float(elapsed_time)
                times.append(elapsed_time)

                writer.writerow([
                    n,
                    block_size,
                    repetition,
                    elapsed_time,
                    checksum
                ])

            print(
                f"Block: {block_size:3d} | "
                f"Median: {median(times):.6f} seconds"
            )

print("\nResults saved to:", results_file)
