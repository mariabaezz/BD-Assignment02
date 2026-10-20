
import csv
from pathlib import Path
from statistics import median, quantiles

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

SIZES = [100, 250, 500]
SPARSITIES = [0, 50, 80, 90, 95, 99]


def read_csv(filename):
    with open(RESULTS / filename, newline="") as file:
        return list(csv.DictReader(file))


def stats(values):
    if len(values) != 5:
        raise ValueError(
            f"Expected 5 repetitions, received {len(values)}"
        )

    q1, _, q3 = quantiles(
        values, n=4, method="inclusive"
    )

    return median(values), q3 - q1


time_rows = read_csv("sparse_results.csv")
memory_rows = read_csv("sparse_memory_results.csv")

time_summary = {}
memory_summary = {}


with open(
    RESULTS / "sparse_summary.csv", "w", newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "matrix_size",
        "sparsity",
        "nnz_A",
        "nnz_B",
        "nnz_C",
        "output_density_percent",
        "median_dense_seconds",
        "iqr_dense_seconds",
        "median_conversion_seconds",
        "iqr_conversion_seconds",
        "median_sparse_seconds",
        "iqr_sparse_seconds",
        "median_total_sparse_seconds",
        "iqr_total_sparse_seconds",
        "speedup_mult_only",
        "speedup_total"
    ])

    for n in SIZES:
        for sparsity in SPARSITIES:

            rows = [
                row for row in time_rows
                if int(row["matrix_size"]) == n
                and int(row["sparsity"]) == sparsity
            ]

            if len(rows) != 5:
                raise ValueError(
                    f"Missing data for n={n}, s={sparsity}"
                )

            dense, dense_iqr = stats([
                float(r["dense_time_seconds"]) for r in rows
            ])

            conversion, conversion_iqr = stats([
                float(r["conversion_time_seconds"]) for r in rows
            ])

            sparse, sparse_iqr = stats([
                float(r["sparse_time_seconds"]) for r in rows
            ])

            total, total_iqr = stats([
                float(r["conversion_plus_sparse_seconds"])
                for r in rows
            ])

            nnz_a = int(rows[0]["nnz_A"])
            nnz_b = int(rows[0]["nnz_B"])
            nnz_c = int(rows[0]["nnz_C"])

            for row in rows:
                if (
                    int(row["nnz_A"]) != nnz_a
                    or int(row["nnz_B"]) != nnz_b
                    or int(row["nnz_C"]) != nnz_c
                ):
                    raise ValueError("Inconsistent nonzero counts")

            output_density = 100 * nnz_c / (n * n)
            speedup_mult_only = dense / sparse
            speedup = dense / total

            time_summary[n, sparsity] = {
                "dense": dense,
                "conversion": conversion,
                "sparse": sparse,
                "total": total,
                "speedup_mult_only": speedup_mult_only,
                "speedup": speedup,
                "density": output_density
            }

            writer.writerow([
                n, sparsity, nnz_a, nnz_b, nnz_c,
                output_density,
                dense, dense_iqr,
                conversion, conversion_iqr,
                sparse, sparse_iqr,
                total, total_iqr,
                speedup_mult_only,
                speedup
            ])

            print(
                f"n={n}, sparsity={sparsity}% | "
                f"Speedup={speedup:.2f}x"
            )


with open(
    RESULTS / "sparse_memory_summary.csv",
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "matrix_size",
        "sparsity",
        "method",
        "median_peak_rss_mib",
        "iqr_peak_rss_mib"
    ])

    for n in SIZES:
        for sparsity in SPARSITIES:
            for method in ["dense", "sparse"]:

                rows = [
                    r for r in memory_rows
                    if int(r["matrix_size"]) == n
                    and int(r["sparsity"]) == sparsity
                    and r["method"] == method
                ]

                checksums = {
                    int(r["checksum"]) for r in rows
                }

                if len(checksums) != 1:
                    raise ValueError("Inconsistent checksums")

                values = [
                    int(r["peak_rss_bytes"]) / (1024 * 1024)
                    for r in rows
                ]

                med, iqr = stats(values)

                memory_summary[n, sparsity, method] = med

                writer.writerow([
                    n, sparsity, method, med, iqr
                ])

            dense_checksums = {
                int(r["checksum"]) for r in memory_rows
                if int(r["matrix_size"]) == n
                and int(r["sparsity"]) == sparsity
                and r["method"] == "dense"
            }

            sparse_checksums = {
                int(r["checksum"]) for r in memory_rows
                if int(r["matrix_size"]) == n
                and int(r["sparsity"]) == sparsity
                and r["method"] == "sparse"
            }

            if dense_checksums != sparse_checksums:
                raise ValueError("Dense/Sparse checksum mismatch")


for n in SIZES:

    plt.figure(figsize=(8, 5))

    for key, label in [
        ("dense", "Dense reordered"),
        ("sparse", "CSR multiplication"),
        ("total", "CSR conversion + multiplication")
    ]:

        values = [
            time_summary[n, s][key] * 1000
            for s in SPARSITIES
        ]

        plt.plot(
            SPARSITIES, values, marker="o", label=label
        )

    plt.yscale("log")
    plt.xlabel("Input sparsity (%)")
    plt.ylabel("Median time (ms, log scale)")
    plt.title(f"Dense vs CSR Runtime - n={n}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        FIGURES / f"sparse_runtime_{n}.png",
        dpi=300
    )
    plt.close()



for n in SIZES:

    plt.figure(figsize=(8, 5))

    for method in ["dense", "sparse"]:

        values = [
            memory_summary[n, s, method]
            for s in SPARSITIES
        ]

        plt.plot(
            SPARSITIES, values,
            marker="o", label=method.capitalize()
        )

    plt.xlabel("Input sparsity (%)")
    plt.ylabel("Median Peak RSS (MiB)")
    plt.title(f"Dense vs Dense-to-CSR Pipeline - n={n}")
    plt.ylim(bottom=0)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        FIGURES / f"sparse_memory_{n}.png",
        dpi=300
    )
    plt.close()



plt.figure(figsize=(8, 5))

for n in SIZES:

    values = [
        time_summary[n, s]["density"]
        for s in SPARSITIES
    ]

    plt.plot(
        SPARSITIES, values,
        marker="o", label=f"n={n}"
    )

plt.xlabel("Input sparsity (%)")
plt.ylabel("Output density (%)")
plt.title("Output Matrix Density")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    FIGURES / "sparse_output_density.png",
    dpi=300
)
plt.close()


plt.figure(figsize=(8, 5))

for n in SIZES:

    total_speedups = [
        time_summary[n, s]["speedup"]
        for s in SPARSITIES
    ]

    plt.plot(
        SPARSITIES,
        total_speedups,
        marker="o",
        label=f"n={n}"
    )

plt.axhline(
    y=1,
    color="gray",
    linestyle="--",
    label="Break-even (1x)"
)

plt.xlabel("Input sparsity (%)")
plt.ylabel("Speedup (Dense / CSR total)")
plt.title("CSR Speedup Including Conversion")
plt.yscale("log")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    FIGURES / "sparse_speedup_total.png",
    dpi=300
)
plt.close()



n = 500

dense_storage = []
csr_storage = []

for sparsity in SPARSITIES:

    rows = [
        row for row in time_rows
        if int(row["matrix_size"]) == n
        and int(row["sparsity"]) == sparsity
    ]

    nnz_a = int(rows[0]["nnz_A"])
    nnz_b = int(rows[0]["nnz_B"])

    # Storage of both input matrices
    dense_bytes = 2 * 8 * n * n

    csr_bytes = (
        12 * nnz_a + 4 * (n + 1)
        + 12 * nnz_b + 4 * (n + 1)
    )

    dense_storage.append(dense_bytes / (1024 * 1024))
    csr_storage.append(csr_bytes / (1024 * 1024))


plt.figure(figsize=(8, 5))

plt.plot(
    SPARSITIES,
    dense_storage,
    marker="o",
    label="Dense inputs (A + B)"
)

plt.plot(
    SPARSITIES,
    csr_storage,
    marker="o",
    label="CSR inputs (A + B)"
)

plt.xlabel("Input sparsity (%)")
plt.ylabel("Theoretical storage (MiB)")
plt.title("Theoretical Input Storage - n=500")
plt.ylim(bottom=0)
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    FIGURES / "sparse_theoretical_storage.png",
    dpi=300
)
plt.close()


print("\nSparse analysis completed.")
print("Summary tables saved in results/")
print("Figures saved in results/figures/")
