
import argparse
import json
import time
from pathlib import Path
from importlib.metadata import version

import fitz
from paddleocr import PaddleOCR


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--device", default="gpu:0")
    return parser.parse_args()


def main():
    args = parse_args()

    pdf_path = Path(args.pdf)
    output_dir = Path(args.out)
    pages_dir = output_dir / "pages"

    pages_dir.mkdir(parents=True, exist_ok=True)

    print("Initializing PaddleOCR...")
    print("PaddleOCR:", version("paddleocr"))
    print("PaddlePaddle:", version("paddlepaddle-gpu"))
    print("Device:", args.device)

    ocr = PaddleOCR(
        lang="en",
        device=args.device,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    document = fitz.open(pdf_path)

    all_text = []
    page_metrics = []
    total_inference_time = 0.0

    for page_index, page in enumerate(document):
        page_number = page_index + 1

        image_path = pages_dir / f"page_{page_number:02d}.png"
        text_path = pages_dir / f"page_{page_number:02d}.txt"
        json_path = pages_dir / f"page_{page_number:02d}.json"

        # Render the PDF page at the same DPI as the Tesseract benchmark.
        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(args.dpi / 72, args.dpi / 72),
            alpha=False,
        )
        pixmap.save(image_path)

        start = time.perf_counter()

        results = ocr.predict(str(image_path))

        inference_time = time.perf_counter() - start
        total_inference_time += inference_time

        page_lines = []
        structured_results = []

        for result in results:
            data = result.json

            # PaddleOCR 3.x may wrap prediction data in a result object.
            if callable(data):
                data = data()

            if isinstance(data, dict) and "res" in data:
                data = data["res"]

            if not isinstance(data, dict):
                continue

            texts = data.get("rec_texts", [])
            scores = data.get("rec_scores", [])
            boxes = data.get("rec_polys", data.get("dt_polys", []))

            for index, text in enumerate(texts):
                score = (
                    float(scores[index])
                    if index < len(scores)
                    else None
                )

                box = (
                    boxes[index].tolist()
                    if index < len(boxes)
                    and hasattr(boxes[index], "tolist")
                    else boxes[index] if index < len(boxes)
                    else None
                )

                page_lines.append(str(text))

                structured_results.append({
                    "text": str(text),
                    "confidence": score,
                    "bounding_box": box,
                })

        extracted_text = "\n".join(page_lines)

        text_path.write_text(
            extracted_text,
            encoding="utf-8",
        )

        json_path.write_text(
            json.dumps(
                structured_results,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        all_text.append(
            f"\n\n===== PAGE {page_number} =====\n\n"
            + extracted_text
        )

        page_metrics.append({
            "page": page_number,
            "inference_time_seconds": round(inference_time, 4),
            "recognized_lines": len(page_lines),
            "text_characters": len(extracted_text),
            "image_width": pixmap.width,
            "image_height": pixmap.height,
        })

        print(
            f"Page {page_number}: "
            f"{inference_time:.3f}s | "
            f"{len(page_lines)} lines | "
            f"{len(extracted_text)} characters"
        )

    combined_text = "".join(all_text)

    (output_dir / "combined.txt").write_text(
        combined_text,
        encoding="utf-8",
    )

    metrics = {
        "framework": "PaddleOCR",
        "paddleocr_version": version("paddleocr"),
        "paddlepaddle_version": version("paddlepaddle-gpu"),
        "paddlex_version": version("paddlex"),
        "device": args.device,
        "dpi": args.dpi,
        "input_pdf": str(pdf_path),
        "pages_processed": len(document),
        "total_inference_time_seconds": round(
            total_inference_time, 4
        ),
        "total_recognized_lines": sum(
            p["recognized_lines"] for p in page_metrics
        ),
        "total_text_characters": len(combined_text),
        "pages": page_metrics,
    }

    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print("\nPaddleOCR benchmark complete.")
    print("Pages:", len(document))
    print("Total inference:", round(total_inference_time, 4), "seconds")
    print("Recognized lines:", metrics["total_recognized_lines"])
    print("Output:", output_dir.resolve())


if __name__ == "__main__":
    main()
