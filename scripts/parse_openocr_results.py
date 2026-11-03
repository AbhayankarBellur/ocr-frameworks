import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "outputs" / "openocr" / "pages"
OUTPUT_DIR = ROOT / "outputs" / "openocr"

all_text = []
page_metrics = []
total_lines = 0
all_scores = []

for page_num in range(1, 6):
    path = PAGES_DIR / f"page_{page_num:02d}.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    raw = data["result"]

    if isinstance(raw, str):
        # OpenOCR format: filename<TAB>JSON array
        _, payload = raw.split("\t", 1)
        records = json.loads(payload)
    elif isinstance(raw, list):
        records = raw
    else:
        raise TypeError(f"Unexpected result format on page {page_num}: {type(raw)}")

    lines = []
    for record in records:
        text = record.get("transcription", "")
        score = record.get("score")
        points = record.get("points")

        if text:
            lines.append(text)

        if score is not None:
            all_scores.append(float(score))

    page_text = "\n".join(lines)
    all_text.append(f"--- PAGE {page_num} ---\n{page_text}")

    corrected = {
        "page": page_num,
        "recognized_lines": len(records),
        "average_confidence": (
            sum(float(r["score"]) for r in records if r.get("score") is not None)
            / max(1, sum(1 for r in records if r.get("score") is not None))
        ),
        "records": records,
    }

    (PAGES_DIR / f"page_{page_num:02d}_parsed.json").write_text(
        json.dumps(corrected, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (PAGES_DIR / f"page_{page_num:02d}.txt").write_text(
        page_text, encoding="utf-8"
    )

    total_lines += len(records)
    page_metrics.append({
        "page": page_num,
        "recognized_lines": len(records),
        "average_confidence": round(corrected["average_confidence"], 4),
    })

(OUTPUT_DIR / "combined.txt").write_text(
    "\n\n".join(all_text), encoding="utf-8"
)

metrics_path = OUTPUT_DIR / "metrics.json"
metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
metrics["total_recognized_lines"] = total_lines
metrics["pages"] = [
    {**old, **new}
    for old, new in zip(metrics["pages"], page_metrics)
]
metrics["average_detection_confidence"] = round(
    sum(all_scores) / len(all_scores), 4
) if all_scores else None
metrics["result_parser"] = "OpenOCR filename-tab-JSON-array parser"

metrics_path.write_text(
    json.dumps(metrics, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("Corrected OpenOCR output parsing complete.")
print("Total detected text regions:", total_lines)
print("Average detection/recognition score:", metrics["average_detection_confidence"])
print("\nPage breakdown:")
for page in page_metrics:
    print(page)
