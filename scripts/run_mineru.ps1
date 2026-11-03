param(
    [string]$MineruExe = 'mineru-kit'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$renderDir = Join-Path $repoRoot 'outputs\tesseract\rendered_pages'
$outputDir = Join-Path $repoRoot 'outputs\mineru'

Push-Location $repoRoot
try {
    $pages = 1..5 | ForEach-Object {
        $path = Join-Path $renderDir ('page_{0:D2}.png' -f $_)
        if (-not (Test-Path $path)) { throw "Missing rendered page: $path. Run the Tesseract renderer first." }
        (Resolve-Path $path).Path
    }

    if (-not (Test-Path $MineruExe)) {
        $command = Get-Command $MineruExe -ErrorAction Stop
        $MineruExe = $command.Source
    }

    $env:MINERU_MODEL_SMALL_BACKEND = 'onnx'
    $env:MINERU_MODEL_ONNX_DEVICE = 'cpu'
    $env:MINERU_MODEL_SOURCE = 'huggingface'
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

    $monitorArgs = @(
        '--name', 'mineru_basic_cpu',
        '--output-dir', 'benchmarks/resource_logs',
        '--', $MineruExe, 'parse'
    ) + $pages + @(
        '--output', $outputDir,
        '--tier', 'basic',
        '--format', 'zip',
        '--ocr-mode', 'ocr'
    )

    & python .\scripts\monitor.py @monitorArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}