# Output Artifacts

`examples/` contains a small, curated subset of the original generated outputs for format and qualitative inspection. The complete local `outputs/<framework>/` directories are excluded from Git because they contain repeated per-page data, crops, image assets, and ZIP bundles.

The curated Docling Markdown replaces large base64-embedded image payloads with an explanatory placeholder. This keeps the text and table output inspectable without committing embedded figure binaries. The original local Docling output remains unchanged.

Small figure assets referenced by Marker, MinerU, and PP-StructureV3 examples are retained where they demonstrate image extraction; unrelated page crops and repeated image products are omitted.