
import csv
import re
import subprocess
from pathlib import Path

sizes = [100, 250, 500]
sparsities = [0, 50, 80, 90, 95, 99]
methods = ["dense", "sparse"]
repetitions = 5

project_root = Path(__file__).resolve().parents[1]
executable = project_root / "src" / "c" / "run_sparse_memory"
results_file = project_root / "results" / "sparse_memory_results.csv"

results_file.parent.mkdir(parents=True, exist_ok=True)

with open(results_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "matrix_size",
        "sparsity",
        "method",
        "repetition",
        "peak_rss_bytes",
        "checksum"
    ])

    for n in sizes:
        for sparsity in sparsities:

            expected_checksum = None

            for repetition in range(1, repetitions + 1):
                for method in methods:

                    result = subprocess.run(
                        [
                            "/usr/bin/time",
                            "-l",
                            str(executable),
                            method,
                            str(n),
                            str(sparsity)
                        ],
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                        check=True
                    )

                    memory_match = re.search(
                        r"(\d+)\s+maximum resident set size",
                        result.stderr
                    )

                    checksum_match = re.search(
                        r"Checksum:\s+(\d+)",
                        result.stdout
                    )

                    if memory_match is None:
                        raise ValueError("Peak RSS not found")

                    if checksum_match is None:
                        raise ValueError("Checksum not found")

                    peak_rss = int(memory_match.group(1))
                    checksum = int(checksum_match.group(1))

                    # Check that both methods agree
                    if expected_checksum is None:
                        expected_checksum = checksum
                    elif checksum != expected_checksum:
                        raise ValueError(
                            f"Checksum mismatch: n={n}, "
                            f"sparsity={sparsity}, method={method}"
                        )

                    writer.writerow([
                        n,
                        sparsity,
                        method,
                        repetition,
                        peak_rss,
                        checksum
                    ])

                    print(
                        f"Size: {n} | Sparsity: {sparsity}% "
                        f"| Method: {method} "
                        f"| Repetition: {repetition} "
                        f"| Peak RSS: {peak_rss} bytes"
                    )

print("\nResults saved to:", results_file)
