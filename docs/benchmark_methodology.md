# Benchmark Methodology

## Corpus and page representation

The sample is five selected pages from *Attention Is All You Need*. The source is the original research PDF. Image-oriented runs use pages rasterized at 300 DPI, producing 2550 × 3300 pixel images. The original source PDF and rendered page files remain local pending redistribution-rights review; see [../data/README.md](../data/README.md).

## Input-mode matrix

| Processing category | Frameworks | Input used |
|---|---|---|
| Image-based OCR | Tesseract, PaddleOCR, OpenOCR, Surya | Rendered page PNGs |
| Layout-aware image parsing | PP-StructureV3 | Rendered page PNGs |
| Document parsing with OCR | MinerU | Rendered page PNGs; basic tier, OCR mode, ONNX backend on CPU |
| PDF-native / hybrid parsing | Marker | Original PDF; metadata confirms `pdftext` extraction |
| Document parsing with OCR | Docling | Original PDF; standard pipeline, Tesseract OCR, tables enabled |
| Native text reference | PyMuPDF baseline | Original PDF embedded text layer |

The category names describe these specific benchmark configurations, not every possible mode each product supports.

## Timing boundaries

- **Framework-reported inference/pipeline/CLI time** comes from each framework's metrics or command output. The semantics vary: summing Tesseract's five stored per-page OCR timings gives 11.1193 seconds, and its own whole-run wall timer is 12.5842 seconds including rendering and writes. Marker CLI reported 5.6135 seconds. Docling's timing artifact reports 21.407 seconds of pipeline work.
- **Initialization** is separately present for Surya and PP-StructureV3. It is not recorded uniformly for the other systems.
- **Monitored elapsed time** is the monitor process duration around the command, including setup and output overhead. It is not interchangeable with model inference time.
- MinerU has a monitored elapsed value but no standardized framework-reported inference metric in the repository.

## Resource monitor

`scripts/monitor.py` samples a process and its descendants once per second by default. It records process-tree CPU, resident memory, read/write I/O, system CPU, and optional NVML GPU utilization/memory. It reports total elapsed time, peak sampled RSS, and working-drive used-space delta to the terminal. Disk delta is not a CSV column, so the final comparison records it as N/R. Sampling can miss short-lived peaks.

NVML values are for GPU 0 globally. The 142 MB readings during CPU runs are global idle readings; they are not allocations by the OCR process. PaddleOCR's 4770.5 MB reading is also global, not an isolated process allocation. Missing values are N/R rather than inferred.

## Comparability limits

- PDF-native Marker and Docling have access to embedded text and PDF structure; image-only OCR frameworks do not.
- MinerU's run is OCR mode, while Marker explicitly uses PDF text extraction. Docling runs a multi-stage pipeline with OCR and tables.
- Initialization, preprocessing, output writing, pipeline stages, and timing boundaries differ.
- GPU metrics are incomplete or global, and RAM is a sampled Windows process-tree maximum.
- The five-page sample is small and not a representative corpus of scanned documents, multiple languages, or degraded images.
- There is no annotation set for word error rate, table cell accuracy, equation fidelity, or figure relation accuracy.

For all selected values and source filenames, see [../benchmarks/final_comparison.csv](../benchmarks/final_comparison.csv).