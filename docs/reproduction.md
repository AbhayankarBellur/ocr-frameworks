# Reproduction Guide

These commands reflect the benchmark configurations recorded in the source scripts, output metadata, and the saved PowerShell command history. They do not install dependencies automatically. Run from the repository root in a separately prepared environment for the selected framework.

## Prerequisites

- Windows PowerShell, Python 3.11 for the recorded setup, and Git.
- Obtain the source PDF separately and place it at `data/native/attention_is_all_you_need.pdf` only after checking rights. The repository excludes the PDF and rendered page images.
- Install Tesseract OCR and ensure `tesseract.exe` is on `PATH`. Docling's recorded run also used this executable.
- Python package versions are not fully locked. Versions observed in metrics are listed in [implementation_details.md](implementation_details.md). Marker and Docling exact versions were not recorded. Do not treat the current local virtual environments as a portable environment specification.
- Model weights may be downloaded by each framework. The repo does not record verified aggregate storage requirements.

## Create and activate framework environments

The recorded workflow used separate environments. Example activation for the already-present local environments:

```powershell
.\.venv\Scripts\Activate.ps1       # Tesseract / PaddleOCR / OpenOCR / Surya as locally installed
.\.venv-ppstructure\Scripts\Activate.ps1
.\.venv-mineru\Scripts\Activate.ps1
.\.venv-marker\Scripts\Activate.ps1
.\.venv-docling\Scripts\Activate.ps1
```

These are local examples, not checked-in dependencies. The initial MinerU, Marker, and Docling package installs in the recorded history were `python -m pip install mineru`, `python -m pip install marker-pdf psutil`, and `python -m pip install docling psutil`, respectively. Those commands do not pin versions and are not guaranteed to recreate the recorded run.

## Render pages and run the native baseline

The Tesseract runner performs rendering and OCR in one command; its rendered PNGs feed OpenOCR, Surya, PP-StructureV3, and MinerU.

```powershell
python .\scripts\run_tesseract.py `
  --pdf .\data\rasterized\attention_is_all_you_need_rasterized.pdf `
  --out .\outputs\tesseract `
  --dpi 300 --lang eng --psm 3

python .\scripts\extract_native_baseline.py `
  --pdf .\data\native\attention_is_all_you_need.pdf `
  --out .\ground-truth\native_pdf_baseline
```

For a monitored run, wrap a runner with `python .\scripts\monitor.py --name RUN_NAME --output-dir .\benchmarks\resource_logs -- COMMAND`. The resource monitor's GPU column is global GPU 0 telemetry.

## Image-based frameworks

### PaddleOCR

```powershell
python .\scripts\run_paddleocr.py `
  --pdf .\data\rasterized\attention_is_all_you_need_rasterized.pdf `
  --out .\outputs\paddleocr `
  --dpi 300 --device gpu:0
```

The recorded run used PaddleOCR 3.7.0, PaddlePaddle 3.2.0, and PaddleX 3.7.2. The GPU-enabled package was installed in a separate environment. CPU execution can be selected with the script's `--device` option, but would be a different benchmark configuration.

### OpenOCR

```powershell
python .\scripts\run_openocr.py
python .\scripts\parse_openocr_results.py
```

The runner reads the five images under `outputs/tesseract/rendered_pages/`; its recorded configuration is ONNX Runtime with `use_gpu="false"`. The parser consumes raw per-page output and updates aggregate JSON/text. The attempted CUDA provider failed on Windows with DLL load error 126; the final metrics are CPU-only.

### Surya

```powershell
python .\scripts\run_surya.py
```

The recorded run used Surya OCR 0.17.1 and PyTorch 2.15.0+cpu. The script chooses the device based on PyTorch CUDA availability; the saved run was CPU.

### PP-StructureV3

```powershell
python .\scripts\run_ppstructure.py
```

The script expects the same five Tesseract-rendered page images and explicitly initializes PP-StructureV3 on CPU. The observed environment used Paddle 3.2.0 and PaddleOCR 3.7.0.

### MinerU

The original model setup selected the basic tier and ONNX backend on CPU:

```powershell
$env:MINERU_MODEL_SMALL_BACKEND = 'onnx'
$env:MINERU_MODEL_ONNX_DEVICE = 'cpu'
$env:MINERU_MODEL_SOURCE = 'huggingface'
mineru-kit models download --tier basic --small-backend onnx --source huggingface
mineru-kit models verify --tier basic --small-backend onnx
```

After rendering the five pages, invoke the local wrapper:

```powershell
.\scripts\run_mineru.ps1
```

It passes the five PNG paths to `mineru-kit parse` with `--tier basic --format zip --ocr-mode ocr`, matching the recorded command. Export metadata reports MinerU 4.1.4 and confirms no VLM tier was used. This requires model downloads; storage size was not measured in the repository.

## Original-PDF frameworks

### Marker

Activate the Marker environment and run:

```powershell
.\scripts\run_marker.ps1
```

This wraps `marker_single` on the original PDF with page range `0-4`, `--mode fast`, Markdown output, the saved CPU equation configuration, disabled multiprocessing, and disabled progress display. The wrapper writes resource samples under `benchmarks/resource_logs/`. Marker equation OCR remains disabled in [`configs/marker_cpu_config.json`](../configs/marker_cpu_config.json).

### Docling

Ensure `docling` and Tesseract are available in the active environment and on `PATH`, then run:

```powershell
.\scripts\run_docling.ps1
```

The wrapper preserves the recorded standard CPU pipeline, OCR and tables enabled, Tesseract engine, `eng` OCR language, pages 1-5, four threads, and profiling. This configuration yields Markdown and a profiling timing JSON. The exact Docling package version was not saved.

## Reproduction status

The repository now has runnable command wrappers for all eight named frameworks plus the native baseline. However, **a clean clone is not yet a fully reproducible benchmark environment**: package versions are not locked across systems, Marker/Docling versions are unknown, model hashes and storage sizes are absent, source PDF redistribution is unresolved, and successful end-to-end reruns have not been performed from a clean machine. The wrappers preserve recorded parameters but are not a substitute for dependency lockfiles.