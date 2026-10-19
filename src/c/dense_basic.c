
#include <stdio.h>

void multiply_basic(const long long *A, const long long *B,
                    long long *C, int n) {

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {

            C[i * n + j] = 0;

            for (int k = 0; k < n; k++) {
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

    multiply_basic(A, B, C, n);

    printf("Basic result:\n");

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%lld ", C[i * n + j]);
        }
        printf("\n");
    }

    return 0;
}
