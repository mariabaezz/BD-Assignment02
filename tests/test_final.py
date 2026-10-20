
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DENSE = ROOT / "src/c/run_matrix_validate"
SPARSE = ROOT / "src/c/run_sparse"

SIZES = [50, 100, 150, 200, 250, 500, 750, 1000]
SPARSITIES = [0, 50, 80, 90, 95, 99]


def run_program(command):
    result = subprocess.run(
        [str(x) for x in command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout


print("=== DENSE VALIDATION ===")

for n in SIZES:
    checksums = []

    for method in ["basic", "reordered", "blocked"]:
        block_size = 32 if n <= 250 else 128

        output = run_program([
            DENSE, method, n, block_size
        ])

        _, checksum = output.strip().split(",")
        checksums.append(int(checksum))

    if len(set(checksums)) != 1:
        raise AssertionError(f"Dense mismatch: n={n}")

    print(f"PASS Dense n={n}")


print("\n=== SPARSE VALIDATION ===")

for n in [100, 250, 500]:
    for sparsity in SPARSITIES:

        output = run_program([
            SPARSE, n, sparsity
        ])

        if "Dense and Sparse results match." not in output:
            raise AssertionError(
                f"Sparse mismatch: n={n}, sparsity={sparsity}"
            )

        print(f"PASS Sparse n={n}, sparsity={sparsity}%")


print("\nALL FINAL TESTS PASSED")
