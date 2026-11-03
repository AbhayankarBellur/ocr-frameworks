# Findings

## What the runs show

- OCR engines produce recognized text and locations. A bounding box or confidence score is not a reading-order tree, a table, or an equation representation.
- Image-based OCR is the more appropriate category when the input is a scan or rendered page. Tesseract and OpenOCR had lower observed process-tree RAM in the selected runs than the longer CPU document pipelines, though the runs used different implementations and timing boundaries.
- Layout/document systems provide richer outputs (blocks, headings, tables, figures, Markdown, or structured JSON) at additional computation and memory cost. PP-StructureV3 and Surya were especially slow in their selected CPU runs; resource numbers are host- and configuration-specific.
- PDF-native extraction can avoid OCR for text already embedded in a PDF. Marker metadata says `text_extraction_method: pdftext`. Such a result must not be interpreted as image OCR quality.
- Detection of a table, equation, or figure is only one stage. Table values, row/column semantics, mathematical notation, and figure relationships require independent quality verification.
- Docling's table output demonstrates this distinction: Table 2 is represented structurally but has missing values and corrupted scientific notation. Formula placeholders show that successful document assembly does not mean equation decoding.

## Workload-oriented choices

| Workload need | Candidate fit from this benchmark | Qualification |
|---|---|---|
| Fast text transcription with boxes/confidence | Tesseract, PaddleOCR, OpenOCR | OCR outputs do not automatically reconstruct hierarchy, tables, or math. PaddleOCR was GPU-run; OpenOCR's final run was CPU. |
| Line OCR with explicit detector/recognizer stages | Surya | The selected CPU run was slow and memory intensive; use only when its output behavior fits the workload. |
| Page layout and richer structured page export | PP-StructureV3 | Highest observed CPU time and peak RAM in this sample; output quality still needs validation. |
| OCR-mode document parsing from rendered pages | MinerU basic tier | Extracts Markdown, structured blocks, and images; no VLM was used. Exact package environment is not fully locked. |
| PDF with a usable embedded text layer | Marker | Its `pdftext` mode is hybrid/native extraction, not comparable to image-only OCR. Equation OCR was disabled. |
| Multi-stage PDF conversion and Markdown assembly | Docling | Standard CPU pipeline includes OCR, tables, layout, reading order, and assembly; observed equations were not decoded and Table 2 had value errors. |

There is no single winner independent of input, fidelity requirements, available hardware, and acceptable cost. For table or equation workloads, evaluate exact cell/formula output rather than relying on a system's advertised stage list.