
import subprocess
import csv
import re
from pathlib import Path

sizes = [100, 250, 500]
sparsities = [0, 50, 80, 90, 95, 99]
repetitions = 5

project_root = Path(__file__).resolve().parents[1]
executable = project_root / "src" / "c" / "run_sparse"
results_file = project_root / "results" / "sparse_results.csv"

with open(results_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "matrix_size",
        "sparsity",
        "repetition",
        "nnz_A",
        "nnz_B",
        "nnz_C",
        "dense_time_seconds",
        "conversion_time_seconds",
        "sparse_time_seconds",
        "conversion_plus_sparse_seconds"
    ])

    for n in sizes:
        for sparsity in sparsities:
            for repetition in range(1, repetitions + 1):

                result = subprocess.run(
                    [
                        str(executable),
                        str(n),
                        str(sparsity)
                    ],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    check=True
                )

                output = result.stdout

                if "Dense and Sparse results match." not in output:
                    raise ValueError("Results not validated")

                def extract(pattern):
                    match = re.search(pattern, output)
                    if not match:
                        raise ValueError(
                            f"Missing measurement: {pattern}"
                        )
                    return match.group(1)

                nnz_a = extract(r"nnz A: (\d+)")
                nnz_b = extract(r"nnz B: (\d+)")
                nnz_c = extract(r"nnz C: (\d+)")

                dense_time = float(
                    extract(r"Dense runtime: ([\d.]+)")
                )
                conversion_time = float(
                    extract(r"CSR conversion: ([\d.]+)")
                )
                sparse_time = float(
                    extract(r"Sparse runtime: ([\d.]+)")
                )

                writer.writerow([
                    n,
                    sparsity,
                    repetition,
                    nnz_a,
                    nnz_b,
                    nnz_c,
                    dense_time,
                    conversion_time,
                    sparse_time,
                    conversion_time + sparse_time
                ])

                print(
                    "Size:", n,
                    "| Sparsity:", sparsity,
                    "| Repetition:", repetition,
                    "| Dense:", dense_time,
                    "| Sparse:", sparse_time
                )

print("Results saved to:", results_file)
