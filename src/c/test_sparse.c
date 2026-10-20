
#include <stdio.h>
#include <stdlib.h>

// CSR representation
typedef struct {
    int n;
    int nnz;
    long long *values;
    int *col_index;
    int *row_ptr;
} CSRMatrix;

// Functions from sparse_csr.c
CSRMatrix dense_to_csr(const long long *A, int n);

void multiply_csr(const CSRMatrix *A,
                  const CSRMatrix *B,
                  long long *C);

void free_csr(CSRMatrix *csr);

// Basic multiplication from dense_basic.c
void multiply_basic(const long long *A,
                    const long long *B,
                    long long *C,
                    int n);


void test_multiplication(const long long *A,
                         const long long *B,
                         int n) {

    long long *C_basic = calloc((size_t)n * n, sizeof(long long));
    long long *C_sparse = calloc((size_t)n * n, sizeof(long long));

    if (C_basic == NULL || C_sparse == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        free(C_basic);
        free(C_sparse);
        exit(1);
    }

    CSRMatrix csr_A = dense_to_csr(A, n);
    CSRMatrix csr_B = dense_to_csr(B, n);

    multiply_basic(A, B, C_basic, n);
    multiply_csr(&csr_A, &csr_B, C_sparse);

    for (int i = 0; i < n * n; i++) {
        if (C_basic[i] != C_sparse[i]) {
            fprintf(stderr,
                    "FAILED: n=%d, index=%d\n", n, i);

            free(C_basic);
            free(C_sparse);
            free_csr(&csr_A);
            free_csr(&csr_B);
            exit(1);
        }
    }

    printf("PASSED: n=%d\n", n);

    free(C_basic);
    free(C_sparse);
    free_csr(&csr_A);
    free_csr(&csr_B);
}


int main(void) {

    // Test 1: Known multiplication
    long long A1[] = {
        1, 0, 2,
        0, 3, 0,
        4, 0, 5
    };

    long long B1[] = {
        2, 0, 0,
        0, 3, 0,
        1, 0, 4
    };

    test_multiplication(A1, B1, 3);

    // Test 2: Identity matrix
    long long A2[] = {
        1, 2,
        3, 4
    };

    long long I[] = {
        1, 0,
        0, 1
    };

    test_multiplication(A2, I, 2);

    // Test 3: Zero matrix
    long long Z[] = {
        0, 0,
        0, 0
    };

    test_multiplication(A2, Z, 2);

    // Test 4: Matrix of size 1
    long long A3[] = {7};
    long long B3[] = {3};

    test_multiplication(A3, B3, 1);

    printf("All sparse tests passed.\n");

    return 0;
}
