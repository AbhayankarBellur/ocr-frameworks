# Limitations and Open Issues

## Experimental limits

- The benchmark covers five pages of one scientific paper, not a representative document corpus.
- Input modes vary. Marker and Docling receive the original PDF; the image-based systems receive rendered pages. Embedded text can materially change the task.
- Pipeline stages are not uniform. Some systems perform only OCR; others include layout, table extraction, and document assembly.
- Initialization timing is recorded only for Surya and PP-StructureV3 in a standardized metric file.
- Framework-reported runtime and monitored process elapsed time have different boundaries. They must be reported in separate columns.
- RAM is sampled once per second and may miss peaks. Disk delta is printed by the monitor but not included in its CSV schema.
- NVML reports GPU 0 globally. It is not process-specific. Some CPU runs record idle global readings; other runs have no GPU reading.
- No annotated truth set supports WER/CER, exact table cell accuracy, equation fidelity, or figure relation scores.
- Table 2 in Docling has missing values and damaged scientific notation. Docling's attention and positional-encoding regions use `formula-not-decoded` placeholders.
- Marker equation OCR is disabled because its attempted equation-processing backend required Docker in the initial setup.
- OpenOCR's Windows CUDA provider failed to load with DLL error 126; the final result uses CPU.

## Reproducibility and publication gaps

- There is no single lockfile or version manifest for the separate framework environments.
- Marker and Docling exact package versions are not recorded in project evidence.
- The source PDF and rendered page images are not included in the public Git set pending a redistribution-rights review.
- No project code license has been chosen. The repository should not be advertised as open source until the owner selects a license.
- Model download storage sizes were not recorded and are not estimated here.
- For a repeatable comparison, hardware/driver details, OS build, cold/warm cache policy, model checkpoint hashes, and exact package locks should be recorded with each run.