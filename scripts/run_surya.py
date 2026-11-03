import json
import time
import importlib.metadata
from pathlib import Path

import torch
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "outputs" / "tesseract" / "rendered_pages"
OUTPUT_DIR = ROOT / "outputs" / "surya"
PAGES_DIR = OUTPUT_DIR / "pages"

PAGES_DIR.mkdir(parents=True, exist_ok=True)

images = sorted(INPUT_DIR.glob("page_*.png"))
if len(images) != 5:
    raise RuntimeError(f"Expected 5 images, found {len(images)}")

device = "CUDA" if torch.cuda.is_available() else "CPU"
print(f"Surya {importlib.metadata.version('surya-ocr')} | Device: {device}")
print("Loading Surya predictors...", flush=True)

init_start = time.perf_counter()
foundation = FoundationPredictor()
recognition = RecognitionPredictor(foundation)
detection = DetectionPredictor()
initialization_time = time.perf_counter() - init_start

print(f"Models loaded in {initialization_time:.2f}s", flush=True)

all_text = []
page_metrics = []
total_inference = 0.0
total_lines = 0

for index, image_path in enumerate(images, 1):
    print(f"\nProcessing page {index}/5: {image_path.name}", flush=True)

    image = Image.open(image_path).convert("RGB")

    start = time.perf_counter()
    prediction = recognition([image], det_predictor=detection)
    elapsed = time.perf_counter() - start

    page = prediction[0]
    text_lines = getattr(page, "text_lines", [])

    records = []
    extracted = []

    for line in text_lines:
        text = getattr(line, "text", "")
        polygon = getattr(line, "polygon", None)
        confidence = getattr(line, "confidence", None)

        extracted.append(text)
        records.append({
            "text": text,
            "polygon": polygon,
            "confidence": confidence,
        })

    page_text = "\n".join(extracted)
    all_text.append(f"--- PAGE {index} ---\n{page_text}")

    page_data = {
        "page": index,
        "image": image_path.name,
        "dimensions": list(image.size),
        "inference_time_seconds": round(elapsed, 4),
        "recognized_lines": len(records),
        "text_lines": records,
    }

    (PAGES_DIR / f"page_{index:02d}.json").write_text(
        json.dumps(page_data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (PAGES_DIR / f"page_{index:02d}.txt").write_text(
        page_text, encoding="utf-8"
    )

    total_inference += elapsed
    total_lines += len(records)

    page_metrics.append({
        "page": index,
        "inference_time_seconds": round(elapsed, 4),
        "recognized_lines": len(records),
    })

    print(f"  Time: {elapsed:.3f}s | Lines: {len(records)}", flush=True)

(OUTPUT_DIR / "combined.txt").write_text(
    "\n\n".join(all_text), encoding="utf-8"
)

metrics = {
    "framework": "Surya",
    "version": importlib.metadata.version("surya-ocr"),
    "torch_version": torch.__version__,
    "device": device,
    "initialization_time_seconds": round(initialization_time, 4),
    "pages_processed": len(images),
    "total_inference_time_seconds": round(total_inference, 4),
    "total_recognized_lines": total_lines,
    "pages": page_metrics,
}

(OUTPUT_DIR / "metrics.json").write_text(
    json.dumps(metrics, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("\n========== SURYA BASELINE COMPLETE ==========")
print(json.dumps(metrics, indent=2, ensure_ascii=False))
