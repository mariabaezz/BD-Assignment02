
#include <stdio.h>

void multiply_reordered(const long long *A, const long long *B,
                        long long *C, int n) {

    // Initialize result matrix with zeros
    for (int i = 0; i < n * n; i++) {
        C[i] = 0;
    }

    // Optimised multiplication: i-k-j
    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            for (int j = 0; j < n; j++) {
                C[i * n + j] +=
                    A[i * n + k] * B[k * n + j];
            }
        }
    }
}

int main(void) {

    int n = 2;

    long long A[] = {1, 2,
                    3, 4};

    long long B[] = {5, 6,
                    7, 8};

    long long C[4];

    multiply_reordered(A, B, C, n);

    printf("Reordered result:\n");

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%lld ", C[i * n + j]);
        }
        printf("\n");
    }

    return 0;
}
