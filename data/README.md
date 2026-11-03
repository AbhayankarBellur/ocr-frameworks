# Benchmark Data

The benchmark uses five selected pages from *Attention Is All You Need*.

The original PDF is available from the paper's arXiv record: <https://arxiv.org/abs/1706.03762>. The arXiv record links to a non-exclusive distribution license; that is not treated here as blanket permission for this repository to redistribute the PDF, rendered pages, or extracted paper text. Those artifacts remain local and excluded from Git pending a rights review. Download and use the document in accordance with its source and hosting terms, and place a local copy at:

```text
data/native/attention_is_all_you_need.pdf
```

The image-based runners expect the rasterized five-page PDF at `data/rasterized/attention_is_all_you_need_rasterized.pdf`. Rasterization used 300 DPI and produced 2550 × 3300 pixel pages. Check source and derived-image permissions before distributing either file.

The repository's `ground-truth/native_pdf_baseline/` is a PyMuPDF extraction of the source PDF text layer. It is a reference transcript, not manually verified ground truth for OCR accuracy.