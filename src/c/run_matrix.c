
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void multiply_basic(const long long *A, const long long *B,
                    long long *C, int n);

void multiply_reordered(const long long *A, const long long *B,
                        long long *C, int n);

void multiply_blocked(const long long *A, const long long *B,
                      long long *C, int n, int block_size);


void read_matrix(const char *filename, long long *matrix, int n) {
    FILE *file = fopen(filename, "r");

    if (file == NULL) {
        fprintf(stderr, "Cannot open %s\n", filename);
        exit(1);
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (fscanf(file, " %lld", &matrix[i * n + j]) != 1) {
                fprintf(stderr, "Invalid matrix: %s\n", filename);
                exit(1);
            }

            if (j < n - 1) {
                int separator = fgetc(file);
                if (separator != ',') {
                    fprintf(stderr, "Invalid CSV separator\n");
                    exit(1);
                }
            }
        }
    }

    fclose(file);
}


int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: ./run_matrix method size block_size\n");
        return 1;
    }

    char *method = argv[1];
    int n = atoi(argv[2]);
    int block_size = atoi(argv[3]);

    if (n <= 0 || n > 10000 || block_size <= 0) {
        fprintf(stderr, "Invalid size or block size\n");
        return 1;
    }

    size_t elements = (size_t)n * n;

    long long *A = malloc(elements * sizeof(long long));
    long long *B = malloc(elements * sizeof(long long));
    long long *C = malloc(elements * sizeof(long long));

    if (A == NULL || B == NULL || C == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        free(A);
        free(B);
        free(C);
        return 1;
    }

    char filename[256];

    snprintf(filename, sizeof(filename), "inputs/A_%d.csv", n);
    read_matrix(filename, A, n);

    snprintf(filename, sizeof(filename), "inputs/B_%d.csv", n);
    read_matrix(filename, B, n);

    if (strcmp(method, "basic") == 0) {
        multiply_basic(A, B, C, n);
    } else if (strcmp(method, "reordered") == 0) {
        multiply_reordered(A, B, C, n);
    } else if (strcmp(method, "blocked") == 0) {
        multiply_blocked(A, B, C, n, block_size);
    } else {
        fprintf(stderr, "Unknown method: %s\n", method);
        free(A);
        free(B);
        free(C);
        return 1;
    }

    long long checksum = 0;

    for (size_t i = 0; i < elements; i++) {
        checksum += C[i];
    }

    printf("Method: %s | Size: %d | Checksum: %lld\n", method, n, checksum);

    free(A);
    free(B);
    free(C);

    return 0;
}
