# Output Quality Assessment

This is a qualitative inspection of saved outputs, not a formal accuracy benchmark. No page-level truth annotation exists for character strings, bounding boxes, table cells, equations, or diagram relationships. No arbitrary numeric quality scores are assigned.

| Framework | Prose | Reading order and headings | Tables | Equations | Figures / spatial information | Output structure |
|---|---|---|---|---|---|---|
| Tesseract | Generally readable, with symbol errors | Line/token sequence; no semantic headings | Text/TSV only, no row/column reconstruction | Superscripts and mathematical layout are fragile | Word boxes only; no figure model | TXT and TSV |
| PaddleOCR | Readable line text | Ordered line output; polygons and confidence, no hierarchy | Polygons do not define cells | No math-specific representation verified | Text geometry only | Combined TXT and per-page JSON |
| OpenOCR | Readable line text; 396 lines total in recorded metrics | Parsed OCR regions, no hierarchy | No table reconstruction evidence | Plain recognition output | Region data, no figure extraction | TXT and parsed JSON |
| Surya | 406 detected/recognized lines in the run | Line sequence and polygon metadata | No table structure output | Math remains text lines | Bounding polygons, no diagram graph | TXT and JSON |
| PP-StructureV3 | Richer page Markdown than line-only OCR | Layout-aware blocks and headings | Table-capable output; cell correctness not verified | Formula-capable stages but inspected expression text is malformed in places | Image/caption regions in outputs | Markdown and structured JSON |
| MinerU | Coherent body text in Markdown | `paragraph_title` blocks and normalized bounding boxes | Structured extraction possible; exact row/column truth not assessed | LaTeX-like text present but characters can be split and spacing damaged | Image blocks, captions, and extracted assets | Markdown, structured JSON, middle JSON, ZIP output |
| Marker | Strong prose from embedded PDF text | Sections/page anchors and block hierarchy | Markdown table extraction; not cell-validated | Equation OCR disabled; equation content depends on PDF text path | Diagram JPEGs and captions retained | Markdown and metadata JSON |
| Docling | Readable document Markdown | Reading-order and document assembly stages | Table 2 grid is present, but several values are absent and scientific notation is corrupted | Formula areas contain `formula-not-decoded` placeholders | Figure images and captions are retained; relationships are not fully represented | Markdown and profiling timings |

## Table observations

### Table 1: Complexity comparison

Raw OCR can recognize many words and numbers but usually emits lines rather than cells. That representation does not reliably preserve columns, row associations, superscripts, or embedded math. Layout/document parsers provide more structure, but the repository has no gold cell boundaries or cell-value labels with which to certify the reconstruction.

### Table 2: BLEU scores and training costs

Docling detects and serializes the table structure, but the inspected Markdown is incomplete: multiple cell values are absent and scientific notation is corrupted. A detected table is not automatically an accurate table. Marker output is available as a comparison example but has not been validated against a cell-level truth set.

### Table 3: Model variations and hyperparameters

Multi-line headers and tightly packed hyperparameters challenge row and column alignment. Markdown can retain approximate rows while still mishandling merged cells or their association with values. No cell-level score is reported.

## Equation observations

- **Attention equation:** Marker has equation OCR disabled. MinerU produces LaTeX-like strings but may split variable names and digits. PP-StructureV3 may emit malformed formula text.
- **Positional encoding:** Docling's Markdown contains `formula-not-decoded` placeholders around the formula regions. The surrounding prose is not proof of equation extraction.
- **Greek symbols, superscripts, and subscripts:** line OCR can preserve visible glyphs as ordinary text but usually loses mathematical scope and two-dimensional relationships. UTF-8 output does not repair recognition errors.

## Diagram observations

Marker extracts diagram JPEGs and retains captions. MinerU emits image blocks, caption text, and image assets. Docling Markdown contains embedded figure images and captions. PP-StructureV3 emits image regions. These outputs demonstrate detection/extraction, not reconstruction of arrows, node labels, or a spatially linked diagram graph.

## Inspectable examples

- [Tesseract combined text](../outputs/examples/tesseract/combined.txt) and TSV.
- [PaddleOCR text and JSON](../outputs/examples/paddleocr/).
- [OpenOCR parsed output](../outputs/examples/openocr/).
- [Surya line JSON](../outputs/examples/surya/).
- [PP-StructureV3 Markdown and JSON](../outputs/examples/ppstructurev3/).
- [MinerU Markdown and structured JSON](../outputs/examples/mineru/).
- [Marker Markdown and metadata](../outputs/examples/marker/).
- [Docling Markdown and timings](../outputs/examples/docling/).