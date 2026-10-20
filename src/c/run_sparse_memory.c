
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// CSR representation
typedef struct {
    int n;
    int nnz;
    long long *values;
    int *col_index;
    int *row_ptr;
} CSRMatrix;

CSRMatrix dense_to_csr(const long long *A, int n);
void multiply_csr(const CSRMatrix *A,
                  const CSRMatrix *B,
                  long long *C);
void free_csr(CSRMatrix *csr);

void multiply_reordered(const long long *A,
                        const long long *B,
                        long long *C, int n);


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

    if (argc != 4) {
        fprintf(stderr,
                "Usage: ./run_sparse_memory dense|sparse size sparsity\n");
        return 1;
    }

    const char *method = argv[1];
    int n = atoi(argv[2]);
    int sparsity = atoi(argv[3]);

    if ((strcmp(method, "dense") != 0 &&
        strcmp(method, "sparse") != 0) ||
        n <= 0 || n > 10000 ||
        sparsity < 0 || sparsity > 100) {
        fprintf(stderr, "Invalid arguments\n");
        return 1;
    }

    size_t total = (size_t)n * n;

    long long *A = malloc(total * sizeof(long long));
    long long *B = malloc(total * sizeof(long long));
    long long *C = malloc(total * sizeof(long long));

    if (!A || !B || !C) {
        fprintf(stderr, "Memory allocation failed\n");
        free(A);
        free(B);
        free(C);
        return 1;
    }

    char filename[256];

    snprintf(filename, sizeof(filename),
            "inputs/sparse/A_%d_s%d.csv", n, sparsity);
    read_matrix(filename, A, n);

    snprintf(filename, sizeof(filename),
            "inputs/sparse/B_%d_s%d.csv", n, sparsity);
    read_matrix(filename, B, n);

    if (strcmp(method, "dense") == 0) {

        multiply_reordered(A, B, C, n);

    } else {

        CSRMatrix csr_A = dense_to_csr(A, n);
        CSRMatrix csr_B = dense_to_csr(B, n);

        multiply_csr(&csr_A, &csr_B, C);

        free_csr(&csr_A);
        free_csr(&csr_B);
    }

    // Use the computed result
    long long checksum = 0;

    for (size_t i = 0; i < total; i++) {
        checksum += C[i];
    }

    printf("Method: %s | Size: %d | Sparsity: %d\n",
        method, n, sparsity);
    printf("Checksum: %lld\n", checksum);

    free(A);
    free(B);
    free(C);

    return 0;
}
