$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath 'C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model'
$bhsmActive = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'python.exe' -and $_.CommandLine -match 'reproduce_n12_gate7_interval14_entry.py'
})
if ($bhsmActive.Count -gt 0) { throw 'A BHSM reproduction driver is already running. Do not start a second writer.' }
$bhsmLog = 'tmp/gate7_vector_20260919/manual_resume_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log'
Write-Host "Continuing interval-14 reproduction. Log: $bhsmLog"
& 'C:\Python314\python.exe' 'scripts/reproduce_n12_gate7_interval14_entry.py' `
    --evidence-root '../BHSM-ae32-crossing-correction' `
    --work 'tmp/gate7_vector_20260919' `
    --workers 10 `
    --midpoint-repair 'tmp/gate7_vector_20260919/interval14_midpoint14_exact_raw_repair_v2' `
    *> $bhsmLog
$bhsmExit = $LASTEXITCODE
Get-Content -LiteralPath $bhsmLog -Tail 12
if ($bhsmExit -ne 0) { throw "Reproduction stopped with exit code $bhsmExit. Preserve the log and checkpoints; do not bypass the comparison." }
Write-Host 'Check interval14_entry_reproduction_first.json. Successful reproduction does not itself debit the ledger or close Gate 7.'
