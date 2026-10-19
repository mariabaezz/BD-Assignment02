def multiply_basic(A, B):
    n = len(A)

    C = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]

    return C


if __name__ == "__main__":
    A = [[1, 2],
        [3, 4]]

    B = [[5, 6],
        [7, 8]]

    C = multiply_basic(A, B)

    print("Result:")
    for row in C:
        print(row)
