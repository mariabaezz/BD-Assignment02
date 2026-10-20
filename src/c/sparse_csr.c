
#include <stdio.h>
#include <stdlib.h>

// CSR matrix representation
typedef struct {
    int n;
    int nnz;
    long long *values;
    int *col_index;
    int *row_ptr;
} CSRMatrix;


// Convert dense matrix to CSR
CSRMatrix dense_to_csr(const long long *A, int n) {

    CSRMatrix csr;
    csr.n = n;
    csr.nnz = 0;

    // Count nonzero elements
    for (int i = 0; i < n * n; i++) {
        if (A[i] != 0) {
            csr.nnz++;
        }
    }

    // Allocate memory
    csr.values = malloc((size_t)csr.nnz * sizeof(long long));
    csr.col_index = malloc((size_t)csr.nnz * sizeof(int));
    csr.row_ptr = malloc((size_t)(n + 1) * sizeof(int));

    if (csr.row_ptr == NULL ||
        (csr.nnz > 0 &&
        (csr.values == NULL || csr.col_index == NULL))) {
        fprintf(stderr, "CSR allocation failed\n");
        exit(1);
    }

    int index = 0;

    for (int i = 0; i < n; i++) {

        csr.row_ptr[i] = index;

        for (int j = 0; j < n; j++) {

            long long value = A[i * n + j];

            if (value != 0) {
                csr.values[index] = value;
                csr.col_index[index] = j;
                index++;
            }
        }
    }

    csr.row_ptr[n] = index;

    return csr;
}


void free_csr(CSRMatrix *csr) {
    free(csr->values);
    free(csr->col_index);
    free(csr->row_ptr);
}

void multiply_csr(const CSRMatrix *A, const CSRMatrix *B,
                  long long *C) {

    int n = A->n;

    // Initialize dense result with zeros
    for (int i = 0; i < n * n; i++) {
        C[i] = 0;
    }

    // Process each row of A
    for (int i = 0; i < n; i++) {

        // Nonzero elements of row i in A
        for (int p = A->row_ptr[i];
            p < A->row_ptr[i + 1]; p++) {

            int k = A->col_index[p];
            long long value_A = A->values[p];

            // Nonzero elements of row k in B
            for (int q = B->row_ptr[k];
                q < B->row_ptr[k + 1]; q++) {

                int j = B->col_index[q];
                long long value_B = B->values[q];

                C[i * n + j] += value_A * value_B;
            }
        }
    }
}

#ifndef MATRIX_LIBRARY

int main(void) {

    int n = 3;

    long long A[] = {
        1, 0, 2,
        0, 3, 0,
        4, 0, 5
    };

    long long B[] = {
        2, 0, 0,
        0, 3, 0,
        1, 0, 4
    };

    long long C[9];

    CSRMatrix csr_A = dense_to_csr(A, n);
    CSRMatrix csr_B = dense_to_csr(B, n);

    multiply_csr(&csr_A, &csr_B, C);

    printf("Sparse multiplication result:\n");

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%lld ", C[i * n + j]);
        }
        printf("\n");
    }

    free_csr(&csr_A);
    free_csr(&csr_B);

    return 0;
}
#endif