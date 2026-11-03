import json
import time
import importlib.metadata
from pathlib import Path

import numpy as np
from PIL import Image
from openocr import OpenOCR

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "outputs" / "tesseract" / "rendered_pages"
OUTPUT_DIR = ROOT / "outputs" / "openocr"
PAGES_DIR = OUTPUT_DIR / "pages"

PAGES_DIR.mkdir(parents=True, exist_ok=True)

images = sorted(INPUT_DIR.glob("page_*.png"))
if len(images) != 5:
    raise RuntimeError(f"Expected 5 pages, found {len(images)}")

print("Initialising OpenOCR on CPU...", flush=True)
ocr = OpenOCR(backend="onnx", use_gpu="false")

all_text = []
page_metrics = []
total_time = 0.0
total_lines = 0

for page_num, image_path in enumerate(images, 1):
    print(f"Processing page {page_num}/5: {image_path.name}", flush=True)

    image = np.array(Image.open(image_path).convert("RGB"))

    start = time.perf_counter()
    output = ocr.model(str(image_path))
    elapsed = time.perf_counter() - start

    if isinstance(output, tuple):
        page_results, timing = output
    else:
        page_results, timing = output, {}

    result = page_results[0] if isinstance(page_results, list) and page_results else {}

    if isinstance(result, dict):
        transcriptions = result.get("transcription", [])
        if isinstance(transcriptions, str):
            transcriptions = [transcriptions]

        text = "\n".join(str(x) for x in transcriptions)
        line_count = len(transcriptions)
    else:
        text = str(result)
        line_count = 1 if text else 0

    all_text.append(f"--- PAGE {page_num} ---\n{text}")

    page_data = {
        "page": page_num,
        "image": image_path.name,
        "dimensions": list(image.shape[:2]),
        "wall_time_seconds": round(elapsed, 4),
        "timing": timing,
        "result": result,
    }

    (PAGES_DIR / f"page_{page_num:02d}.json").write_text(
        json.dumps(page_data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (PAGES_DIR / f"page_{page_num:02d}.txt").write_text(
        text, encoding="utf-8"
    )

    total_time += elapsed
    total_lines += line_count

    page_metrics.append({
        "page": page_num,
        "wall_time_seconds": round(elapsed, 4),
        "recognized_lines": line_count,
        "timing": timing,
    })

    print(f"  {elapsed:.3f}s | {line_count} lines", flush=True)

(OUTPUT_DIR / "combined.txt").write_text(
    "\n\n".join(all_text), encoding="utf-8"
)

metrics = {
    "framework": "OpenOCR",
    "openocr_version": importlib.metadata.version("openocr-python"),
    "onnxruntime_version": importlib.metadata.version("onnxruntime-gpu"),
    "backend": "ONNX Runtime",
    "device": "CPU",
    "pages_processed": len(images),
    "total_inference_wall_time_seconds": round(total_time, 4),
    "total_recognized_lines": total_lines,
    "pages": page_metrics,
}

(OUTPUT_DIR / "metrics.json").write_text(
    json.dumps(metrics, indent=2, ensure_ascii=False, default=str),
    encoding="utf-8",
)

print("\nOPENOCR BASELINE COMPLETE")
print(json.dumps(metrics, indent=2, ensure_ascii=False, default=str))

