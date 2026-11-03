import json
import time
from pathlib import Path

import paddle
import paddleocr
from paddleocr import PPStructureV3

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "outputs" / "tesseract" / "rendered_pages"
OUT = ROOT / "outputs" / "ppstructurev3"
OUT.mkdir(parents=True, exist_ok=True)

print("Framework: PP-StructureV3")
print("Paddle:", paddle.__version__)
print("PaddleOCR:", paddleocr.__version__)
print("Device: CPU")

print("\nLoading document parsing pipeline...")
t0 = time.perf_counter()

pipeline = PPStructureV3(
    lang="en",
    device="cpu",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

init_time = time.perf_counter() - t0
print(f"Initialization: {init_time:.2f}s")

pages = []
total_time = 0

for i in range(1, 6):
    image_path = INPUT / f"page_{i:02d}.png"

    if not image_path.exists():
        raise FileNotFoundError(image_path)

    print(f"\nProcessing page {i}/5: {image_path}")

    start = time.perf_counter()
    results = list(pipeline.predict(input=str(image_path)))
    elapsed = time.perf_counter() - start
    total_time += elapsed

    page_dir = OUT / "pages" / f"page_{i:02d}"
    page_dir.mkdir(parents=True, exist_ok=True)

    serialized = []
    markdown_parts = []

    for index, result in enumerate(results):
        data = getattr(result, "json", None)

        if callable(data):
            data = data()

        if data is None and isinstance(result, dict):
            data = result

        if hasattr(data, "get"):
            serialized.append(data)

        # Save native framework outputs when available.
        try:
            result.save_to_json(save_path=str(page_dir))
        except Exception as e:
            print("Native JSON export:", str(e)[:200])

        try:
            result.save_to_markdown(save_path=str(page_dir))
        except Exception as e:
            print("Native Markdown export:", str(e)[:200])

        markdown = getattr(result, "markdown", None)

        if isinstance(markdown, dict):
            texts = markdown.get("markdown_texts", "")
            if isinstance(texts, list):
                markdown_parts.extend(map(str, texts))
            elif texts:
                markdown_parts.append(str(texts))
        elif isinstance(markdown, str):
            markdown_parts.append(markdown)

    with open(page_dir / "combined.json", "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2, default=str)

    with open(page_dir / "combined.md", "w", encoding="utf-8") as f:
        f.write("\n\n".join(markdown_parts))

    pages.append({
        "page": i,
        "inference_time_seconds": round(elapsed, 4),
        "result_objects": len(results),
        "json_records": len(serialized),
        "markdown_characters": sum(map(len, markdown_parts)),
    })

    print(f"Completed: {elapsed:.2f}s | Results: {len(results)}")

metrics = {
    "framework": "PP-StructureV3",
    "paddle_version": paddle.__version__,
    "paddleocr_version": paddleocr.__version__,
    "device": "CPU",
    "initialization_time_seconds": round(init_time, 4),
    "pages_processed": len(pages),
    "total_inference_time_seconds": round(total_time, 4),
    "pages": pages,
}

with open(OUT / "metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print("\n========== PP-STRUCTUREV3 BASELINE COMPLETE ==========")
print(json.dumps(metrics, indent=2))
