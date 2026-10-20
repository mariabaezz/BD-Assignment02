
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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

// Function from dense_reordered.c
void multiply_reordered(const long long *A,
                        const long long *B,
                        long long *C, int n);


// Read a matrix from CSV
void read_matrix(const char *filename, long long *A, int n) {

    FILE *file = fopen(filename, "r");

    if (file == NULL) {
        fprintf(stderr, "Cannot open %s\n", filename);
        exit(1);
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {

            if (fscanf(file, " %lld", &A[i * n + j]) != 1) {
                fprintf(stderr, "Invalid CSV data\n");
                fclose(file);
                exit(1);
            }

            if (j < n - 1 && fgetc(file) != ',') {
                fprintf(stderr, "Invalid CSV separator\n");
                fclose(file);
                exit(1);
            }
        }
    }

    fclose(file);
}


int main(int argc, char *argv[]) {

    if (argc != 3) {
        fprintf(stderr, "Usage: ./run_sparse size sparsity\n");
        return 1;
    }

    int n = atoi(argv[1]);
    int sparsity = atoi(argv[2]);

    if (n <= 0 || n > 10000 || sparsity < 0 || sparsity > 100) {
        fprintf(stderr, "Invalid size or sparsity\n");
        return 1;
    }

    size_t total = (size_t)n * n;

    long long *A = malloc(total * sizeof(long long));
    long long *B = malloc(total * sizeof(long long));
    long long *C_dense = malloc(total * sizeof(long long));
    long long *C_sparse = malloc(total * sizeof(long long));

    if (!A || !B || !C_dense || !C_sparse) {
        fprintf(stderr, "Memory allocation failed\n");
        free(A);
        free(B);
        free(C_dense);
        free(C_sparse);
        return 1;
    }

    char filename[256];

    snprintf(filename, sizeof(filename),
            "inputs/sparse/A_%d_s%d.csv", n, sparsity);
    read_matrix(filename, A, n);

    snprintf(filename, sizeof(filename),
            "inputs/sparse/B_%d_s%d.csv", n, sparsity);
    read_matrix(filename, B, n);


    struct timespec start, end;

    double dense_time;
    double conversion_time;
    double sparse_time;

    // Dense warm-up (not measured)
    multiply_reordered(A, B, C_dense, n);

    // Measure dense multiplication
    clock_gettime(CLOCK_MONOTONIC, &start);

    multiply_reordered(A, B, C_dense, n);

    clock_gettime(CLOCK_MONOTONIC, &end);

    dense_time = (end.tv_sec - start.tv_sec)
               + (end.tv_nsec - start.tv_nsec) / 1e9;


    // Measure conversion of A and B to CSR
    clock_gettime(CLOCK_MONOTONIC, &start);

    CSRMatrix csr_A = dense_to_csr(A, n);
    CSRMatrix csr_B = dense_to_csr(B, n);

    clock_gettime(CLOCK_MONOTONIC, &end);

    conversion_time = (end.tv_sec - start.tv_sec)
                    + (end.tv_nsec - start.tv_nsec) / 1e9;


    // Sparse warm-up (not measured)
    multiply_csr(&csr_A, &csr_B, C_sparse);

    // Measure sparse multiplication
    clock_gettime(CLOCK_MONOTONIC, &start);

    multiply_csr(&csr_A, &csr_B, C_sparse);

    clock_gettime(CLOCK_MONOTONIC, &end);

    sparse_time = (end.tv_sec - start.tv_sec)
                + (end.tv_nsec - start.tv_nsec) / 1e9;


    // Compare all elements
    int nnz_C = 0;

    for (size_t i = 0; i < total; i++) {

        if (C_dense[i] != C_sparse[i]) {
            fprintf(stderr, "Mismatch at index %zu\n", i);

            free_csr(&csr_A);
            free_csr(&csr_B);
            free(A);
            free(B);
            free(C_dense);
            free(C_sparse);
            return 1;
        }

        if (C_sparse[i] != 0) {
            nnz_C++;
        }
    }


    printf("Size: %d | Sparsity: %d%%\n", n, sparsity);

    printf("nnz A: %d | nnz B: %d | nnz C: %d\n",
        csr_A.nnz, csr_B.nnz, nnz_C);

    printf("Dense runtime: %.9f seconds\n", dense_time);
    printf("CSR conversion: %.9f seconds\n", conversion_time);
    printf("Sparse runtime: %.9f seconds\n", sparse_time);

    printf("Conversion + Sparse: %.9f seconds\n",
        conversion_time + sparse_time);

    printf("Dense and Sparse results match.\n");


    free_csr(&csr_A);
    free_csr(&csr_B);

    free(A);
    free(B);
    free(C_dense);
    free(C_sparse);

    return 0;
}
