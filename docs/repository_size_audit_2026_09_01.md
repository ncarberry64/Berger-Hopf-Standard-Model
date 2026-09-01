# Repository size audit — 2026-09-01

## Executive result

The checkout contains **10,685 tracked files totaling 1,817.40 MiB**. Of that,
**1,773.65 MiB (97.6%)** is under `artifacts/`. There are 38 tracked files at
or above 10 MiB and 9 at or above 50 MiB. The largest tracked file is the
97.1 MiB correlated-descriptor Jacobian NPZ.

No tracked `node_modules`, `dist`, `.next`, cache, `__pycache__`, coverage, or
`.pyc` output was found. No duplicate hashes were found within the museum's
source asset directory. Therefore this presentation milestone deletes no
tracked file: the large objects are scientific evidence or unique historical
records, and their removal would be scientifically destructive without a
separate retention decision.

## Tracked working-tree distribution

| Path | Files | Bytes | Approx. MiB |
| --- | ---: | ---: | ---: |
| `artifacts/` | 3,477 | 1,859,806,838 | 1,773.65 |
| `src/` | 1,505 | 15,058,160 | 14.36 |
| `docs/` | 1,033 | 11,695,221 | 11.15 |
| `scripts/` | 1,354 | 6,500,798 | 6.20 |
| `tests/` | 1,947 | 4,731,203 | 4.51 |
| `theory/` | 942 | 3,934,684 | 3.75 |

The shared object database reported 676.57 MiB in packs and 656.62 MiB in
loose objects at audit time. That local figure is shared across worktrees and
is not a clean measure of clone transfer size.

## Largest current tracked files

| MiB | File | Classification |
| ---: | --- | --- |
| 93.53 | `artifacts/flagship_integration/BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.npz` | Scientific numerical evidence |
| 68.86 | `artifacts/flagship_integration/BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.npz` | Scientific numerical evidence |
| 53.74 | `artifacts/flagship_integration/BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_NODES_00_23.npz` | Scientific numerical evidence |
| 53.72 | `artifacts/flagship_integration/BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_NODES_24_47.npz` | Scientific numerical evidence |
| 53.10 | `artifacts/flagship_integration/BHSM_N12_GATE7_SECOND_HS_NEWTON_LINE_SEARCH_PREDICTOR.npz` | Scientific numerical evidence |

## Safe actions taken

- Kept generated build and cache paths ignored.
- Kept the museum exporter deterministic so `museum/dist/` is never tracked.
- Copied only provenance-declared museum display assets into the build at
  build time.
- Added a public-surface audit that rejects tracked build/cache output.
- Preserved every unique scientific artifact and historical status snapshot.

## Recommended repository-operations follow-up

Treat artifact storage as a separate, reviewer-visible engineering milestone.
Before changing history or moving evidence, inventory which files are required
for offline reproduction, assign content hashes and retention classes, then
consider Git LFS or a DOI-backed artifact release. Do not delete or rewrite
large evidence objects merely to reduce the displayed repository size.

Reproduce the working-tree counts in PowerShell:

```powershell
$files = git ls-files
$sizes = foreach ($path in $files) {
  if (Test-Path -LiteralPath $path -PathType Leaf) {
    $item = Get-Item -LiteralPath $path
    [pscustomobject]@{ Path = $path; Bytes = $item.Length }
  }
}
$sizes | Measure-Object Bytes -Sum
$sizes | Sort-Object Bytes -Descending | Select-Object -First 30
```

This audit is descriptive, not a scientific artifact-retention authorization.
