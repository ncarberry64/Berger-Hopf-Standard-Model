# Reproduction and reuse

The saved arrays are the default resume point. The following commands
document reproduction; they are not instructions to rerun production
on every continuation. A fresh output directory is required throughout.
The exact executed source files are retained under executed_source/.

From the publication checkout, reproduce the new tail from its saved
state/clock subset (no history/field campaign and no old element replay):

```powershell
$env:PYTHONPATH='src'
$env:OPENBLAS_NUM_THREADS='1'
& 'C:\Python314\python.exe' scripts/replay_muon_retained_tail_core.py `
  --retained-input artifacts/muon_retained_tail_core_20261005/run_1 `
  --shift 0 --output <new-tail-directory>
```

Reproduce only the accepted coupled solve from cached model coefficients:

```powershell
& 'C:\Python314\python.exe' scripts/solve_muon_tail_source_centered_core.py `
  --source artifacts/muon_retained_tail_core_20261005/run_1 `
  --digits 80 --output <new-solve-directory>
```

New targeted checks only:

```powershell
$env:PYTHONPATH='src'
& 'C:\Python314\python.exe' -m pytest --noconftest -q tests/test_muon_retained_tail_core.py
```

Seven checks passed in1.62 seconds on Python3.14. The old ten checks and
earlier producers were not replayed. Reproduction quantities are compared
mathematically, not by insisting on cross-platform ZIP/BLAS last bits.
Hashes identify the particular executed source/input bytes and saved
outputs. The native spectral length remains unset. The reference s=0
is a declared numerical-model resolvent parameter, not physical momentum.

The discarded diagnostic charts can be reproduced by
attempt_muon_tail_coupled_core.py and solve_muon_tail_hierarchical_core.py;
there is no reason to repeat them for continuation. Their saved receipts
explain the scientific reason for the source-centered repair.
