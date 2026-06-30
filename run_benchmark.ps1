$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$Events = if ($env:BHSM_BENCHMARK_EVENTS) { $env:BHSM_BENCHMARK_EVENTS } else { "1000000" }
$Repeats = if ($env:BHSM_BENCHMARK_REPEATS) { $env:BHSM_BENCHMARK_REPEATS } else { "3" }

Set-Location $Root
& $Python -c "import numpy, matplotlib" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $Python -m pip install -e ".[benchmark]"
}

& $Python -m bhsm.interface.benchmarks.coordinate_benchmark `
    --events $Events `
    --boundary-fraction 0.35 `
    --repeats $Repeats `
    --output tmp/coordinate_benchmark/results.json `
    --markdown tmp/coordinate_benchmark/results.md `
    --plot tmp/coordinate_benchmark/latency.png `
    --summary
exit $LASTEXITCODE
