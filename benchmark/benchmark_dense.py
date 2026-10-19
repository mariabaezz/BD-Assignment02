import time
import csv
from pathlib import Path

from src.dense_basic import multiply_basic
from src.dense_reordered import multiply_reordered
from src.dense_blocked import multiply_blocked


def read_matrix(filename):
    matrix = []

    with open(filename, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            matrix.append([int(value) for value in row])

    return matrix


sizes = [50, 100, 150, 200, 250]
repetitions = 5
warmups = 1

project_root = Path(__file__).resolve().parents[1]

results_file = project_root / "results" / "dense_results.csv"

methods = {
    "basic": multiply_basic,
    "reordered": multiply_reordered,
    "blocked": multiply_blocked
}


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

        A = read_matrix(project_root / "inputs" / f"A_{n}.csv")
        B = read_matrix(project_root / "inputs" / f"B_{n}.csv")

        expected = multiply_basic(A, B)

        for name, method in methods.items():

            for _ in range(warmups):
                C = method(A, B)

                if C != expected:
                    raise ValueError("Incorrect result during warm-up")

            for repetition in range(1, repetitions + 1):

                start = time.perf_counter()

                C = method(A, B)

                end = time.perf_counter()

                if C != expected:
                    raise ValueError("Incorrect multiplication result")

                elapsed_time = end - start
                checksum = sum(sum(row) for row in C)

                writer.writerow([
                    name,
                    n,
                    repetition,
                    elapsed_time,
                    checksum
                ])

                print(
                    "Method:", name,
                    "| Size:", n,
                    "| Repetition:", repetition,
                    "| Time:", elapsed_time,
                    "| Checksum:", checksum
                )
