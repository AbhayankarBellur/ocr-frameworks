"""
Native-PDF baseline: extract the existing PDF text layer.
This is NOT OCR. Run once to establish a reference baseline.
"""
import argparse
import json
import time
from pathlib import Path
import pymupdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default="ground-truth/native_pdf_baseline")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(args.pdf)
    start = time.perf_counter()
    pages = []
    combined = []

    for i, page in enumerate(doc, start=1):
        text = page.get_text("text", sort=True)
        (out / f"page_{i:02d}.txt").write_text(text, encoding="utf-8")
        pages.append({
            "page": i,
            "characters": len(text),
            "words": len(text.split()),
            "image_count": len(page.get_images(full=True)),
        })
        combined.append(f"===== PAGE {i} =====\n{text}")

    elapsed = time.perf_counter() - start
    (out / "combined.txt").write_text(
        "\n\n".join(combined), encoding="utf-8"
    )
    (out / "metrics.json").write_text(json.dumps({
        "input_pdf": str(Path(args.pdf).resolve()),
        "pages": len(doc),
        "elapsed_seconds": round(elapsed, 4),
        "page_results": pages,
    }, indent=2), encoding="utf-8")
    print(json.dumps({
        "pages": len(doc),
        "elapsed_seconds": round(elapsed, 4),
        "page_results": pages,
    }, indent=2))
    doc.close()


if __name__ == "__main__":
    main()
