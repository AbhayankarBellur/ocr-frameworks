"""
Tiny Inference Lab — Tesseract OCR runner
Input: rasterized PDF (five-page OCR-only benchmark sample)
Outputs: per-page PNG, TXT, TSV, JSON metrics, combined TXT.
"""
import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path

import pymupdf
from PIL import Image
import pytesseract
import pandas as pd
from pytesseract import Output


def get_tesseract_version():
    return subprocess.check_output(
        ["tesseract", "--version"], text=True, stderr=subprocess.STDOUT
    ).splitlines()[0]


def line_text(data):
    lines = {}
    for i, token in enumerate(data["text"]):
        token = token.strip()
        if not token:
            continue
        key = (
            data["page_num"][i],
            data["block_num"][i],
            data["par_num"][i],
            data["line_num"][i],
        )
        lines.setdefault(key, []).append(token)
    return "\n".join(" ".join(words) for words in lines.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, help="Path to rasterized PDF")
    ap.add_argument("--out", default="outputs/tesseract")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--lang", default="eng")
    ap.add_argument("--psm", type=int, default=3)
    args = ap.parse_args()

    pdf_path = Path(args.pdf).resolve()
    out_dir = Path(args.out)
    image_dir = out_dir / "rendered_pages"
    image_dir.mkdir(parents=True, exist_ok=True)

    version = get_tesseract_version()
    doc = pymupdf.open(pdf_path)
    results = []
    all_text = []
    run_start = time.perf_counter()

    for page_index, page in enumerate(doc):
        page_number = page_index + 1
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(args.dpi / 72, args.dpi / 72),
            colorspace=pymupdf.csRGB,
            alpha=False,
        )
        image_path = image_dir / f"page_{page_number:02d}.png"
        pix.save(image_path)

        with Image.open(image_path) as im:
            image = im.copy()

        config = f"--oem 1 --psm {args.psm}"
        start = time.perf_counter()
        data = pytesseract.image_to_data(
            image,
            lang=args.lang,
            config=config,
            output_type=Output.DICT,
        )
        elapsed = time.perf_counter() - start

        text = line_text(data)
        (out_dir / f"page_{page_number:02d}.txt").write_text(
            text, encoding="utf-8"
        )
        pd.DataFrame(data).to_csv(
            out_dir / f"page_{page_number:02d}.tsv",
            sep="\t",
            index=False,
        )

        confidences = [
            float(c) for c, t in zip(data["conf"], data["text"])
            if t.strip() and float(c) >= 0
        ]
        word_count = sum(1 for t in data["text"] if t.strip())
        page_result = {
            "page": page_number,
            "width_px": pix.width,
            "height_px": pix.height,
            "dpi": args.dpi,
            "language": args.lang,
            "psm": args.psm,
            "elapsed_seconds": round(elapsed, 4),
            "recognized_words": word_count,
            "mean_word_confidence": round(statistics.mean(confidences), 2)
                if confidences else None,
            "rendered_image_bytes": image_path.stat().st_size,
            "text_characters": len(text),
        }
        results.append(page_result)
        all_text.append(f"===== PAGE {page_number} =====\n{text}")
        print(
            f"Page {page_number}: {elapsed:.2f}s | "
            f"{word_count} words | "
            f"mean confidence {page_result['mean_word_confidence']}"
        )

    total_elapsed = time.perf_counter() - run_start
    combined = "\n\n".join(all_text)
    (out_dir / "combined.txt").write_text(combined, encoding="utf-8")

    summary = {
        "input_pdf": str(pdf_path),
        "pages": len(doc),
        "tesseract_version": version,
        "language": args.lang,
        "oem": 1,
        "psm": args.psm,
        "dpi": args.dpi,
        "total_wall_seconds_including_render_and_writes": round(total_elapsed, 4),
        "total_recognized_words": sum(r["recognized_words"] for r in results),
        "mean_page_confidence": round(
            statistics.mean(
                [r["mean_word_confidence"] for r in results
                 if r["mean_word_confidence"] is not None]
            ), 2
        ) if any(r["mean_word_confidence"] is not None for r in results) else None,
        "page_results": results,
    }
    (out_dir / "metrics.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print("\nRun complete.")
    print(json.dumps(summary, indent=2))
    doc.close()


if __name__ == "__main__":
    main()
