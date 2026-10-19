def multiply_reordered(A, B):
    n = len(A)

    # Create the result matrix
    C = [[0 for _ in range(n)] for _ in range(n)]

    # Optimised matrix multiplication: i-k-j
    for i in range(n):
        for k in range(n):
            for j in range(n):
                C[i][j] += A[i][k] * B[k][j]

    return C


if __name__ == "__main__":
    A = [[1, 2],
        [3, 4]]

    B = [[5, 6],
        [7, 8]]

    C = multiply_reordered(A, B)

    print("Reordered result:")
    for row in C:
        print(row)
