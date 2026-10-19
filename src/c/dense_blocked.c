#include <stdio.h>

void multiply_blocked(const long long *A, const long long *B,
                      long long *C, int n, int block_size) {

    // Initialize result matrix with zeros
    for (int i = 0; i < n * n; i++) {
        C[i] = 0;
    }

    // Process matrices in blocks
    for (int ii = 0; ii < n; ii += block_size) {
        for (int kk = 0; kk < n; kk += block_size) {
            for (int jj = 0; jj < n; jj += block_size) {

                // Process elements inside each block
                for (int i = ii; i < ii + block_size && i < n; i++) {
                    for (int k = kk; k < kk + block_size && k < n; k++) {
                        for (int j = jj; j < jj + block_size && j < n; j++) {
                            C[i * n + j] +=
                                A[i * n + k] * B[k * n + j];
                        }
                    }
                }

            }
        }
    }
}
#ifndef MATRIX_LIBRARY

int main(void) {

    int n = 3;
    int block_size = 2;

long long A[] = {1, 2, 3,
                4, 5, 6,
                7, 8, 9};

long long B[] = {1, 0, 0,
                0, 1, 0,
                0, 0, 1};

long long C[9];

    multiply_blocked(A, B, C, n, block_size);

    printf("Blocked result:\n");

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%lld ", C[i * n + j]);
        }
        printf("\n");
    }

    return 0;
}
#endif