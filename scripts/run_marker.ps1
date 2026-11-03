param(
    [string]$PdfPath = '.\data\native\attention_is_all_you_need.pdf',
    [string]$OutputDir = '.\outputs\marker'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if (-not (Test-Path $PdfPath)) { throw "PDF not found: $PdfPath" }
    $resolvedPdf = (Resolve-Path $PdfPath).Path
    $config = (Resolve-Path '.\configs\marker_cpu_config.json').Path
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

    $monitorArgs = @(
        '--name', 'marker_fast_cpu',
        '--output-dir', 'benchmarks/resource_logs',
        '--', 'marker_single', $resolvedPdf,
        '--page_range', '0-4',
        '--mode', 'fast',
        '--config_json', $config,
        '--output_format', 'markdown',
        '--output_dir', $OutputDir,
        '--disable_multiprocessing',
        '--disable_tqdm'
    )
    & python .\scripts\monitor.py @monitorArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}