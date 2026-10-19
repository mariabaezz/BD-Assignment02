import csv
from pathlib import Path
from statistics import median, quantiles
import matplotlib.pyplot as plt


project_root = Path(__file__).resolve().parents[1]
results = project_root / "results"
figures = results / "figures"
figures.mkdir(exist_ok=True)


def read_csv(filename):
    with open(results / filename, newline="") as file:
        return list(csv.DictReader(file))


def summarize(values):
    values = sorted(values)
    q1, _, q3 = quantiles(values, n=4, method="inclusive")
    return median(values), q3 - q1


measurements = []

for filename, block_size in [
    ("dense_c_results.csv", 32),
    ("dense_c_large_results.csv", 128)
]:
    for row in read_csv(filename):
        row["block_size"] = block_size
        measurements.append(row)


sizes = sorted({
    int(row["matrix_size"]) for row in measurements
})

methods = ["basic", "reordered", "blocked"]

time_summary = {}



with open(results / "dense_summary.csv", "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "matrix_size",
        "method",
        "block_size",
        "repetitions",
        "median_seconds",
        "iqr_seconds",
        "speedup"
    ])

    for n in sizes:
        times = {}

        for method in methods:
            values = [
                float(row["execution_time_seconds"])
                for row in measurements
                if int(row["matrix_size"]) == n
                and row["method"] == method
            ]

            if len(values) != 5:
                raise ValueError(
                    f"Expected 5 measurements: {method}, n={n}"
                )

            times[method] = summarize(values)

        basic_time = times["basic"][0]

        for method in methods:
            med, iqr = times[method]
            block_size = 32 if n <= 250 else 128

            speedup = basic_time / med

            time_summary[n, method] = med

            writer.writerow([
                n,
                method,
                block_size if method == "blocked" else "",
                5,
                med,
                iqr,
                speedup
            ])

            print(
                "Size:", n,
                "| Method:", method,
                "| Median:", round(med, 6),
                "| IQR:", round(iqr, 6),
                "| Speedup:", round(speedup, 3)
            )


plt.figure()

for method in methods:
    times = [time_summary[n, method] for n in sizes]

    if method == "blocked":
        label = "Blocked (32 for n<=250, 128 for n>=500)"
    else:
        label = method.capitalize()

    plt.plot(sizes, times, marker="o", label=label)

plt.xlabel("Matrix size (n)")
plt.ylabel("Median execution time (seconds)")
plt.title("Dense Matrix Multiplication - Runtime")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(figures / "dense_runtime.png", dpi=300)
plt.close()


memory_rows = read_csv("dense_memory_results.csv")
memory_summary = {}

with open(results / "dense_memory_summary.csv", "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "matrix_size",
        "method",
        "repetitions",
        "median_peak_rss_mib",
        "iqr_peak_rss_mib"
    ])

    for n in sizes:
        for method in methods:

            values = [
                int(row["peak_rss_bytes"]) / (1024 * 1024)
                for row in memory_rows
                if int(row["matrix_size"]) == n
                and row["method"] == method
            ]

            if len(values) != 5:
                raise ValueError(
                    f"Expected 5 memory measurements: {method}, n={n}"
                )

            med, iqr = summarize(values)
            memory_summary[n, method] = med

            writer.writerow([n, method, len(values), med, iqr])


plt.figure()

for method in methods:
    memory = [memory_summary[n, method] for n in sizes]
    plt.plot(sizes, memory, marker="o", label=method)

plt.xlabel("Matrix size (n)")
plt.ylabel("Median Peak RSS (MiB)")
plt.title("Dense Matrix Multiplication - Memory")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(figures / "dense_memory.png", dpi=300)
plt.close()

block_rows = read_csv("block_sizes_c.csv")

block_sizes = sorted({
    int(row["block_size"]) for row in block_rows
})

block_medians = []

for block_size in block_sizes:
    values = [
        float(row["execution_time_seconds"])
        for row in block_rows
        if int(row["block_size"]) == block_size
    ]

    med, _ = summarize(values)
    block_medians.append(med)


plt.figure()
plt.plot(block_sizes, block_medians, marker="o")
plt.xlabel("Block size")
plt.ylabel("Median execution time (seconds)")
plt.title("Block Size Tuning - n=250")
plt.grid(True)
plt.tight_layout()

plt.savefig(figures / "block_sizes.png", dpi=300)
plt.close()


print("\nAnalysis completed.")
print("Tables saved in results/")
print("Figures saved in results/figures/")
