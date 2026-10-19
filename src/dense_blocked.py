
def multiply_blocked(A, B, block_size=32):
    n = len(A)

    C = [[0 for _ in range(n)] for _ in range(n)]


    for ii in range(0, n, block_size):
        for kk in range(0, n, block_size):
            for jj in range(0, n, block_size):

                # Process elements inside each block
                for i in range(ii, min(ii + block_size, n)):
                    for k in range(kk, min(kk + block_size, n)):
                        for j in range(jj, min(jj + block_size, n)):
                            C[i][j] += A[i][k] * B[k][j]

    return C


if __name__ == "__main__":
    A = [[1, 2],
        [3, 4]]

    B = [[5, 6],
        [7, 8]]

    C = multiply_blocked(A, B, block_size=2)

    print("Blocked result:")
    for row in C:
        print(row)
