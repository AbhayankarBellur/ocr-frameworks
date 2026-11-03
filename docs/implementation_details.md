# Implementation Details

## Source runners

| System | Source | Actual operation and output |
|---|---|---|
| Tesseract | [`scripts/run_tesseract.py`](../scripts/run_tesseract.py) | Opens the rasterized PDF, renders each page at 300 DPI, calls `image_to_data` with OEM 1 / PSM 3, writes page TXT/TSV, combined text, and metrics. |
| PaddleOCR | [`scripts/run_paddleocr.py`](../scripts/run_paddleocr.py) | Renders PDF pages at 300 DPI, initializes English PaddleOCR on `gpu:0`, calls `predict`, and writes recognized text, scores, polygons, and timing metrics. |
| OpenOCR | [`scripts/run_openocr.py`](../scripts/run_openocr.py) | Reads Tesseract's rendered PNGs; ONNX backend on CPU; writes per-page raw JSON, text, and aggregate metrics. |
| OpenOCR parser | [`scripts/parse_openocr_results.py`](../scripts/parse_openocr_results.py) | Parses the ONNX result representation into records, text, counts, and confidence summary. |
| Surya | [`scripts/run_surya.py`](../scripts/run_surya.py) | Loads foundation, detection, and recognition predictors, processes rendered PNGs, and stores line polygons/confidence and aggregate timings. |
| PP-StructureV3 | [`scripts/run_ppstructure.py`](../scripts/run_ppstructure.py) | Runs its CPU pipeline over rendered PNGs, saving framework JSON and Markdown exports plus timing metrics. |
| Native baseline | [`scripts/extract_native_baseline.py`](../scripts/extract_native_baseline.py) | Reads the original PDF text layer with sorted PyMuPDF text; this is not OCR. |
| Resource monitor | [`scripts/monitor.py`](../scripts/monitor.py) | Launches a child process, samples process-tree metrics, optionally samples NVML GPU 0, and writes time-series CSV. |

## Recorded package/runtime versions

| Framework | Version evidence |
|---|---|
| Tesseract | `tesseract v5.5.3.20260724`; Python wrapper version not in the metrics file |
| PaddleOCR | PaddleOCR 3.7.0, PaddlePaddle 3.2.0, PaddleX 3.7.2 |
| OpenOCR | OpenOCR 0.1.5, ONNX Runtime GPU package 1.20.2; final run CPU |
| Surya | Surya OCR 0.17.1, PyTorch 2.15.0+cpu |
| PP-StructureV3 | PaddleOCR 3.7.0, Paddle 3.2.0 |
| MinerU | MinerU 4.1.4 in exported metadata |
| Marker | Exact installed version not recorded in project evidence |
| Docling | Exact installed version not recorded in project evidence |

## Special configurations

- Tesseract uses English, 300 DPI, `--oem 1 --psm 3`.
- PaddleOCR uses `lang="en"`, `device="gpu:0"`, with orientation classification, unwarping, and textline orientation disabled.
- OpenOCR final configuration is `OpenOCR(backend="onnx", use_gpu="false")`; Windows CUDA provider initialization failed with DLL error 126.
- Surya's final run selected CPU as reported by PyTorch.
- PP-StructureV3 runs CPU; its orientation classification, unwarping, and textline orientation are disabled.
- MinerU selected basic tier, ONNX small-model backend, CPU device, and OCR parse mode. Its run is not VLM-based.
- Marker uses original PDF, page range 0-4, fast mode, Markdown, disabled multiprocessing, disabled progress bar, and [`configs/marker_cpu_config.json`](../configs/marker_cpu_config.json). Equation OCR is disabled.
- Docling uses original PDF, standard pipeline, CPU, OCR on, tables on, Tesseract OCR engine, English OCR language, pages 1-5, four threads, and profiling.

## Output provenance

The curated examples under `outputs/examples/` are copies of original generated artifacts. Docling's output contains base64-embedded figure images; the curated Markdown substitutes a short placeholder for those embedded binary payloads to avoid committing bulky data URLs. Text content and timing evidence are otherwise retained. The complete local outputs remain in the ignored original `outputs/<framework>/` directories.