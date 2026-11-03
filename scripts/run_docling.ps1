param(
    [string]$PdfPath = '.\data\native\attention_is_all_you_need.pdf',
    [string]$OutputDir = '.\outputs\docling'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if (-not (Test-Path $PdfPath)) { throw "PDF not found: $PdfPath" }
    $resolvedPdf = (Resolve-Path $PdfPath).Path
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

    $monitorArgs = @(
        '--name', 'docling_standard_cpu',
        '--output-dir', 'benchmarks/resource_logs',
        '--', 'docling', 'convert', $resolvedPdf,
        '--to', 'md',
        '--pipeline', 'standard',
        '--device', 'cpu',
        '--ocr',
        '--tables',
        '--ocr-engine', 'tesseract',
        '--ocr-lang', 'eng',
        '--page-range', '1-5',
        '--output', $OutputDir,
        '--num-threads', '4',
        '--save-profiling'
    )
    & python .\scripts\monitor.py @monitorArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}