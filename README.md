# BD Assignment 02 — Optimised Matrix Multiplication and Sparse Matrices

**Course:** Big Data  
**Academic year:** 2026–2027  
**Author:** María Báez Marrero  
**Implementation:** C, with Python for input generation, benchmarking and data analysis.

## 1. Project Overview

This project investigates the performance of different matrix multiplication approaches, focusing on execution time, memory consumption and the influence of matrix sparsity.

The assignment is divided into two parts:

**Part A — Dense Matrix Multiplication**

Three sequential matrix multiplication algorithms are implemented and compared:

- **Basic:** conventional matrix multiplication using the i-j-k loop order.
- **Reordered:** multiplication using the i-k-j loop order to improve memory access patterns.
- **Blocked:** tiled multiplication using different block sizes.

**Part B — Sparse Matrix Multiplication**

A custom Compressed Sparse Row (CSR) representation is implemented to investigate how matrix sparsity affects multiplication performance.

The sparse implementation converts two dense input matrices into CSR, performs CSR-based multiplication and produces a dense output matrix.

Both the multiplication-only time and the cost of converting the input matrices to CSR are evaluated.

## 2. Implementation

The matrix multiplication algorithms are implemented in C using sequential execution and 64-bit integer values (`long long`).

The dense implementations use flat, row-major arrays.

The CSR implementation stores nonzero elements using three arrays:

- `values`: nonzero matrix values.
- `col_index`: column indices of those values.
- `row_ptr`: starting positions of each row.

CSR multiplication processes nonzero entries of the input matrices while accumulating the result in a dense output matrix.

Python is used to generate reproducible input datasets, automate experiments, validate results and produce statistical summaries and figures.

## 3. Experimental Environment

| Component | Specification |
|---|---|
| Processor | Apple M4 |
| Physical cores | 10 |
| Logical CPUs | 10 |
| RAM | 16 GiB |
| Architecture | ARM64 |
| Operating system | macOS 26.3.1 |
| Compiler | Apple Clang 21.0.0 |
| Compiler optimisation | `-O2` |
| Execution model | Sequential |

Runtime measurements use `CLOCK_MONOTONIC` in C.

Peak resident memory is measured using macOS `/usr/bin/time -l`.

Each main benchmark configuration is executed five times. Results are summarised using the median and interquartile range (IQR), with inclusive quartiles.

## 4. Requirements

The project requires:

- A C compiler compatible with the source code, such as Apple Clang.
- Python 3.
- Matplotlib for generating figures.
- macOS for the provided Peak RSS measurement scripts.

Install the plotting dependency with:

`python3 -m pip install matplotlib`

The C multiplication implementations do not depend on external numerical libraries.

All commands below assume that they are executed from the repository root.

## 5. Compilation

### Dense benchmark

```bash
clang -O2 -DMATRIX_LIBRARY \
src/c/run_matrix.c \
src/c/dense_basic.c \
src/c/dense_reordered.c \
src/c/dense_blocked.c \
-o src/c/run_matrix
```

### Dense validation executable

```bash
clang -O2 -DMATRIX_LIBRARY -DVALIDATE_RESULTS \
src/c/run_matrix.c \
src/c/dense_basic.c \
src/c/dense_reordered.c \
src/c/dense_blocked.c \
-o src/c/run_matrix_validate
```

### Sparse benchmark

```bash
clang -O2 -DMATRIX_LIBRARY \
src/c/run_sparse.c \
src/c/sparse_csr.c \
src/c/dense_reordered.c \
-o src/c/run_sparse
```

### Sparse memory benchmark

```bash
clang -O2 -DMATRIX_LIBRARY \
src/c/run_sparse_memory.c \
src/c/sparse_csr.c \
src/c/dense_reordered.c \
-o src/c/run_sparse_memory
```

The `MATRIX_LIBRARY` definition prevents demonstration `main()` functions from conflicting when the C files are linked together.

The `VALIDATE_RESULTS` definition enables additional correctness checks and must not be used for the reported memory benchmarks.

## 6. Input Generation

Input matrices contain integer values and use fixed random seeds for reproducibility.

### Dense matrices

The dense experiments use matrix sizes:

50, 100, 150, 200, 250, 500, 750 and 1000.

The original small inputs can be regenerated with:

`python3 -m benchmark.generate_dense_small_inputs`

Larger dense inputs can be regenerated with:

`python3 -m benchmark.generate_dense_inputs`

**Important:** Generators write matrix CSV files. Preserve the existing input files when reproducing the original recorded results.

### Sparse matrices

The sparse experiments use matrix sizes:

100, 250 and 500.

The tested input sparsity levels are:

0%, 50%, 80%, 90%, 95% and 99%.

Matrices are generated with controlled numbers of nonzero elements and reproducible random positions.

To regenerate the sparse datasets:

`python3 -m benchmark.generate_sparse_inputs`

The datasets are stored in `inputs/sparse/`.

### Additional scaling inputs

An additional generator is provided for larger scaling experiments:

`python3 -m benchmark.generate_scaling_input 1500`

`python3 -m benchmark.generate_scaling_input 2000`

These inputs are excluded from Git because they can be regenerated.

## 7. Running the Experiments

### Part A — Dense multiplication

Run the dense benchmarks:

`python3 -m benchmark.benchmark_dense`

Run the block-size experiment for n = 250:

`python3 -m benchmark.benchmark_blocks`

Run the additional block-size experiment for n = 500 and 1000:

`python3 -m benchmark.benchmark_blocks_large`

Run the dense memory benchmark:

`python3 -m benchmark.memory_benchmark`

The original experiments include five repetitions for each configuration.

### Part B — Sparse multiplication

Run the sparse performance benchmark:

`python3 -m benchmark.benchmark_sparse`

Run the sparse memory benchmark:

`python3 -m benchmark.benchmark_sparse_memory`

The sparse benchmarks measure:

- Dense reordered multiplication time.
- Conversion time from dense matrices to CSR.
- CSR multiplication time.
- Conversion time plus CSR multiplication time.
- Number of nonzero elements in A, B and C.
- Peak RSS for dense and sparse execution paths.

Sparse memory measurements execute the dense and sparse methods in separate processes.

## 8. Correctness Validation

The project includes automated correctness checks.

Compile the dense validation executable as described in Section 5 and run:

`python3 -m tests.test_final`

The final validation checks eight dense configurations and eighteen sparse configurations.

All 26 final configurations passed.

The dense validation executable compares full multiplication results against the basic implementation. The sparse validation compares dense and CSR multiplication outputs element by element.

Checksums are also used to detect inconsistencies during benchmarking.

## 9. Statistical Analysis

The analysis scripts read the raw benchmark CSV files and generate summary tables and plots.

To analyse the dense experiments:

`python3 -m analysis.analyse_dense`

To analyse the sparse experiments:

`python3 -m analysis.analyse_sparse`

The analysis includes:

- Median execution time.
- Inclusive interquartile range.
- Speedup relative to the relevant dense baseline.
- Peak RSS statistics.
- CSR conversion cost.
- Input and output sparsity.
- Block-size sensitivity.

The raw measurements and generated summaries are stored in `results/`.

The figures are stored in `results/figures/`.

**Note:** Re-running a benchmark may overwrite the corresponding raw results file. The included datasets and experimental results are preserved in the repository.

## 10. Main Experimental Findings

### Dense multiplication

Reordering the loops generally improves execution time for larger matrices compared with the basic implementation.

Blocked multiplication is competitive with reordered multiplication, but does not consistently outperform it on the tested hardware.

Additional block-size experiments show that block size 128 performs well for larger matrices, although the best measured size varies with matrix dimensions.

The three dense implementations show very similar memory consumption because they store the same three dense matrices.

### Sparse multiplication

CSR-based multiplication provides substantial execution-time improvements when the input matrices contain many zeros.

When conversion is included, CSR is slower for fully dense inputs but faster at the tested sparsity levels of 50% and above.

The output matrix can become substantially denser than the input matrices. Therefore, input sparsity alone does not determine the storage requirements of the product.

## 11. Memory Interpretation

Two different memory concepts are considered.

**Theoretical matrix storage**

For an n × n matrix of 64-bit integers:

- Dense storage: `8 × n²` bytes.
- CSR storage: `12 × nnz + 4 × (n + 1)` bytes, using 32-bit indices.

This calculation describes the matrix representation itself.

**Peak resident memory**

Peak RSS measures the memory consumption of the complete running program.

The sparse pipeline first loads dense matrices, converts them to CSR and uses a dense output matrix. Consequently, its measured Peak RSS can exceed that of the dense implementation, even when the CSR input representation requires substantially less storage.

The theoretical storage comparison and measured process memory must not be interpreted as equivalent metrics.

## 12. Additional Scaling Experiment

Additional Dense Reordered tests were performed for n = 1500 and n = 2000.

A provisional experimental budget of 60 seconds total process runtime and 2 GiB Peak RSS was used for these additional checks.

Both tests completed within this budget.

The largest successfully tested size was n = 2000. This is not a claim that n = 2000 is the maximum feasible matrix size on the hardware.

Detailed environment and scaling measurements are recorded in `results/system.txt`.

## 13. Limitations

The experimental results are specific to the tested Apple M4 environment, compiler and input datasets.

The main limitations include:

- Sparse input positions are generated randomly rather than using structured sparsity patterns.
- CSR multiplication uses a dense output matrix.
- Sparse conversion and multiplication are measured separately, and their combined cost represents a particular input-processing scenario.
- The memory measurements include process overhead and temporary allocations.
- Five repetitions provide a limited estimate of runtime variability.
- Block-size tuning is experimental and does not establish a universally optimal block size.
- The additional scaling experiment does not establish a hardware-wide maximum feasible size.

## 14. Use of AI Tools

AI assistance, including ChatGPT and Claude, was used during development for explanations of algorithms, code suggestions, debugging support, experiment planning, technical review and documentation.

The implementations, experiments, datasets and reported results were developed and tested within the project workflow. The use of AI assistance is disclosed for transparency.

## 15. Repository

GitHub repository:

https://github.com/mariabaezz/BD-Assignment02
