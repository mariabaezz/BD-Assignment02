import random
import csv

random.seed(42)

sizes = [50, 100, 150, 200, 250]

for n in sizes:

    A = [
        [random.randint(0, 9) for j in range(n)]
        for i in range(n)
    ]

    B = [
        [random.randint(0, 9) for j in range(n)]
        for i in range(n)
    ]

    with open(f"inputs/A_{n}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(A)

    with open(f"inputs/B_{n}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(B)

print("Input matrices generated.")