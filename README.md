# BD Assignment 02 — Optimised Matrix Multiplication and Sparse Matrices

**Course:** Big Data (2026–2027)  
**Author:** María Báez Marrero  
**Languages:** C and Python  
**Repository:** https://github.com/mariabaezz/BD-Assignment02

## 1. Overview

This project evaluates the performance of dense and sparse matrix multiplication, focusing on execution time, memory usage and the influence of matrix sparsity.

**Part A — Dense Matrix Multiplication**

Three sequential algorithms are implemented in C:

- **Basic:** standard multiplication using the `i-j-k` loop order.
- **Reordered:** `i-k-j` loop order to improve memory access locality.
- **Blocked:** tiled multiplication with configurable block sizes.

**Part B — Sparse Matrix Multiplication**

A custom Compressed Sparse Row (CSR) representation is used to multiply sparse matrices. Dense inputs are converted to CSR, multiplied, and stored in a dense output matrix.

The experiments compare Dense Reordered against CSR multiplication, measuring both multiplication time and conversion overhead.

All implementations use sequential C, 64-bit integers and no external numerical libraries.

## 2. Repository Structure

```text
BD-Assignment02/
├── src/c/        # Dense and CSR implementations
├── benchmark/    # Input generators and benchmark scripts
├── analysis/     # Statistical analysis and figures
├── tests/        # Correctness tests
├── inputs/       # Dense and sparse input datasets
├── results/      # Raw CSVs, summaries, system.txt and figures/
└── README.md
```

The repository includes the main experimental datasets, measurements and analysis scripts. Additional scaling inputs are generated separately.

## 3. Experimental Environment

| Component | Specification |
|---|---|
| Processor | Apple M4 (10 physical / 10 logical cores) |
| Model | Mac16,1 |
| RAM | 16 GiB |
| Architecture | ARM64 |
| Operating system | macOS 26.3.1 (build 25D771280a) |
| Compiler | Apple Clang 21.0.0 |
| Python | 3.13.0 |
| Matplotlib | 3.10.8 |
| Compilation | `-O2 -DMATRIX_LIBRARY` |
| Execution | Sequential |

Matrix values use `long long` (64-bit); CSR indices and row pointers use `int` (32-bit).

### Measurement Methodology

- Runtime measured using `CLOCK_MONOTONIC`.
- Five repetitions per main benchmark configuration.
- One multiplication warm-up before timing.
- Results summarised using median and inclusive IQR.
- Peak RSS measured using macOS `/usr/bin/time -l`, specifically `maximum resident set size` in bytes.
- Input reading and correctness verification excluded from multiplication timers.
- Output initialisation included in multiplication time.

Peak RSS includes process overhead and temporary allocations, not just matrix storage.

The compiler flag `-DVALIDATE_RESULTS` is used only for correctness checks, never for memory measurements.

Additional environment information is available in `results/system.txt`.

## 4. Setup and Compilation

Clone the repository:

```bash
git clone https://github.com/mariabaezz/BD-Assignment02.git
cd BD-Assignment02
python3 -m pip install matplotlib
```

### Dense multiplication

```bash
clang -O2 -DMATRIX_LIBRARY \
src/c/run_matrix.c \
src/c/dense_basic.c \
src/c/dense_reordered.c \
src/c/dense_blocked.c \
-o src/c/run_matrix
```

### Dense validation

```bash
clang -O2 -DMATRIX_LIBRARY -DVALIDATE_RESULTS \
src/c/run_matrix.c \
src/c/dense_basic.c \
src/c/dense_reordered.c \
src/c/dense_blocked.c \
-o src/c/run_matrix_validate
```

### Sparse multiplication

```bash
clang -O2 -DMATRIX_LIBRARY \
src/c/run_sparse.c \
src/c/sparse_csr.c \
src/c/dense_reordered.c \
-o src/c/run_sparse
```

### Sparse memory measurement

```bash
clang -O2 -DMATRIX_LIBRARY \
src/c/run_sparse_memory.c \
src/c/sparse_csr.c \
src/c/dense_reordered.c \
-o src/c/run_sparse_memory
```

The `MATRIX_LIBRARY` flag prevents multiple demonstration `main()` functions from being linked.

## 5. Input Generation

The datasets use fixed random seeds for reproducibility.

| Experiment | Matrix sizes | Configuration |
|---|---|---|
| Dense | 50, 100, 150, 200, 250, 500, 750, 1000 | Integer values 0–9 |
| Sparse | 100, 250, 500 | Sparsity 0%, 50%, 80%, 90%, 95%, 99% |
| Additional scaling | 1500, 2000 | Dense Reordered |

Generate the datasets if needed:

```bash
python3 -m benchmark.generate_dense_small_inputs
python3 -m benchmark.generate_dense_inputs
python3 -m benchmark.generate_sparse_inputs
```

Small dense inputs use the original Assignment 1 generator with seed 42 and a continuous random sequence. Large dense inputs use a separate deterministic generator. Sparse inputs use controlled nonzero counts and random positions.

For additional scaling inputs:

```bash
python3 -m benchmark.generate_scaling_input 1500
python3 -m benchmark.generate_scaling_input 2000
```

**Note:** Most generators overwrite existing inputs. The scaling generator refuses to overwrite existing files. The original main datasets are already included in the repository.

## 6. Reproducing the Experiments

The recommended workflow is:

**Generate inputs → Compile C executables → Run tests → Run benchmarks → Analyse results**

### Part A — Dense

```bash
python3 -m benchmark.benchmark_dense
python3 -m benchmark.benchmark_blocks
python3 -m benchmark.benchmark_blocks_large
python3 -m benchmark.memory_benchmark
python3 -m analysis.analyse_dense
```

The original runtime experiments used two configurations:

| Sizes | Block size | Output |
|---|---|---|
| 50–250 | 32 | `dense_c_results.csv` |
| 500–1000 | 128 | `dense_c_large_results.csv` |

`benchmark_dense.py` is currently configured for the larger matrices. To reproduce the smaller experiment, change its `sizes`, `block_size` and `results_file` parameters accordingly.

### Part B — Sparse

```bash
python3 -m benchmark.benchmark_sparse
python3 -m benchmark.benchmark_sparse_memory
python3 -m analysis.analyse_sparse
```

The sparse benchmarks record conversion time, multiplication time, nonzero counts, checksums and Peak RSS. Dense and Sparse memory measurements use separate processes.

The analysis scripts generate medians, IQRs, speedups and figures from the raw CSV files.

**Warning:** Re-running benchmarks overwrites their configured results files. Back up the original measurements before repeating experiments.

## 7. Correctness Validation

The implementations are checked against reference multiplication results.

Dense validation compares full outputs against Basic. Sparse validation compares the CSR multiplication result against Dense Reordered element by element.

After compilation, run:

```bash
python3 -m tests.test_final
```

All **26 final configurations passed**:

- 8 Dense matrix-size configurations.
- 18 Sparse size/sparsity configurations.

Additional small tests include known products, identity and zero matrices. Exact integer comparisons are used rather than floating-point tolerances.

## 8. Main Results

### Dense Multiplication

For n = 1000:

| Method | Median runtime | Speedup |
|---|---:|---:|
| Basic | 0.741946 s | 1.00× |
| Reordered | 0.601308 s | 1.23× |
| Blocked (128) | 0.614269 s | 1.21× |

Reordered performed best in this comparison. Blocked improved on Basic for larger matrices but did not consistently outperform Reordered.

Additional tuning found block size 128 fastest among those tested at n = 500, while 512 was fastest at n = 1000. Block size 128 remained competitive in both cases.

### Sparse Multiplication

For n = 500, including conversion time:

| Input sparsity | Total CSR speedup |
|---|---:|
| 0% | 0.93× |
| 50% | 2.84× |
| 80% | 12.04× |
| 90% | 32.30× |
| 95% | 71.57× |
| 99% | 158.65× |

For the tested random matrices, CSR outperformed Dense Reordered at 50% sparsity and above, even including conversion. The exact break-even threshold between 0% and 50% was not measured.

Output density can be much higher than input density. At n = 500 and 90% input sparsity, C contained 248,334 nonzero values out of 250,000 positions (99.33% density).

## 9. Memory Interpretation

Theoretical storage for one n × n matrix is:

- **Dense:** `8 × n²` bytes.
- **CSR:** `12 × nnz + 4 × (n + 1)` bytes.

These expressions describe matrix storage, not total process memory.

Our sparse pipeline loads A and B as dense matrices, converts them into CSR and produces dense C. Therefore, the measured Sparse Peak RSS can exceed the Dense Peak RSS despite CSR requiring less storage for sparse inputs.

The project reports theoretical representation storage and measured process memory separately.

## 10. Additional Scaling Experiment

A complementary Dense Reordered experiment used a provisional budget of:

- **Time:** 60 seconds total process runtime.
- **Memory:** 2 GiB Peak RSS.

| Size | Timed multiplication | Total runtime | Peak RSS |
|---|---:|---:|---:|
| 1500 | 2.148865 s | 4.58 s | 52.80 MiB |
| 2000 | 4.856322 s | 10.31 s | 92.89 MiB |

Checksums were `68292811157` for n = 1500 and `162045984472` for n = 2000.

Both tests met the provisional budget. **n = 2000 was the largest successfully tested size, not the maximum feasible size of the system.** These were individual scaling runs rather than five-repetition benchmarks.

## 11. Limitations

The findings are specific to the tested Apple M4 hardware, compiler, input distributions and measurement conditions.

Important limitations include:

- Only sequential integer implementations were evaluated; no GPU, parallel execution or external BLAS libraries.
- Sparse inputs use randomly distributed nonzeros; structured sparsity was not tested.
- CSR multiplication has a dense output, so it is not a fully sparse-output implementation.
- Conversion overhead matters when input matrices are initially dense.
- Peak RSS includes process overhead, dense temporary inputs and additional CSR allocations.
- Five repetitions and fixed benchmark ordering do not eliminate timing variability.
- Very short CSR runtimes are particularly sensitive to measurement noise.
- Block-size results are specific to the tested configurations.
- The exact sparsity break-even point and maximum feasible matrix dimension were not determined.

These limitations are considered when interpreting the experimental results.

## 12. Use of AI Tools

Claude (Anthropic) was used for algorithm explanation, debugging, statistical analysis support and documentation review.


AI assistance is disclosed for academic transparency.

---

**Repository:** https://github.com/mariabaezz/BD-Assignment02

Raw measurements, summary CSV files, source code and figures are available in the repository. The final report presents selected figures and a more detailed discussion of the findings.