# BHSM v1.4 QCD/RG Matching Note

BHSM v1.4 adds a comparison-scheme scaffold for quark mass ratios. It does not
change BHSM predictions, canonical geometry, overlap width, mode ledger, or
frozen branch outputs.

Reference sets:

| Set | Role |
| --- | --- |
| `MIXED_DEFAULT` | current repository baseline; scheme-sensitive |
| `COMMON_SCALE_APPROX` | fixed-`n_f` one-loop-inspired common-scale scaffold |
| `THRESHOLD_AWARE_APPROX` | piecewise-`n_f` approximate scaffold |
| `PRECISION_QCD_PLACEHOLDER` | future two-/three-loop threshold-matched target; no numerical values supplied |

The scaffold recomputes comparison rows for:

- `c/t`
- `u/t`
- `s/b`
- `d/b`
- dressed-candidate `c/t`

The precision-QCD row is intentionally a placeholder. No final scheme-consistent
failure is declared in this phase because no final precision-QCD reference set
is available. If a future precision reference set is supplied and a frozen BHSM
ratio fails its declared tolerance, that must be reported as a real BHSM
tension rather than tuned away.

Limitations:

- approximate running is not precision QCD;
- uncertainty propagation remains open;
- top/charm reference consistency remains an important comparison issue;
- frozen BHSM v1.0/v1.1 predictions remain unchanged.
