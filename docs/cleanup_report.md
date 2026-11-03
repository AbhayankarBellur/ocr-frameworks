# Cleanup and Publication Preparation Report

No irreversible deletion was performed. The source PDF, rendered benchmark images, native baseline, raw benchmark outputs, resource logs, and virtual environments remain in the local working directory.

| Directory or file group | Recommended action | Reason | Safe to delete now? |
|---|---|---|---|
| `.venv/`, `.venv-docling/`, `.venv-marker/`, `.venv-mineru/`, `.venv-ppstructure/` | Keep locally until a verified remote clone and clean reproduction check | Expensive, framework-specific dependencies | No |
| Framework/model caches and downloaded weights | Keep until the repository is published and a fresh setup is verified | Re-downloadable but often large; exact model hashes/storage sizes are not recorded | No |
| `outputs/<framework>/` full local output trees | Exclude from Git; retain locally as source evidence until curated-copy verification | Contains duplicate page data, images, crops, and ZIP assets | No |
| `outputs/examples/` | Preserve | Curated representative results for eight systems | No |
| `benchmarks/*_resources.csv` selected final source runs | Preserve locally and in curated `benchmarks/resource_logs/` copies | Evidence for monitor elapsed time and sampled resources | No |
| Other resource CSV runs | Exclude from public repo unless needed for a specific comparison; keep local until audit confirms they are redundant | Earlier, failed, smoke, and duplicate runs | No |
| `benchmarks/metrics/` | Preserve | Curated copied final metric/timing evidence | No |
| `data/native/` original PDF | Keep local; exclude from Git pending rights review | Source provenance and redistribution concerns | No |
| `data/rasterized/` page PDF/images | Keep local; exclude from Git pending derived-image rights review | Unique benchmark inputs | No |
| `ground-truth/native_pdf_baseline/` | Preserve locally; exclude from Git pending rights review | Extracted paper text is derived from the source work and is not manually verified truth data | No |
| `__pycache__/`, `.pyc`, disposable temp files | Ignore; remove only after checking they are generated and unused | No publication value | Yes, after inspection |
| Extracted ZIP archives and duplicated image crops | Exclude; delete locally only after verifying unique evidence has a retained copy | Large intermediate data | No |
| `.git/` and project root | Preserve | Repository history/root; do not remove | Never |

The `.gitignore` excludes environments, model files/caches, source PDFs, rendered inputs, raw output trees, and root-level raw resource CSVs while allowing selected examples and copied final resource logs. `git check-ignore` should be rerun before the first commit. This report does not authorize deletion or publication of any excluded local data.