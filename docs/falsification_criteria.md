# Falsification Criteria

These criteria are copied and summarized from the frozen v1.0 falsification
ledger.

| ID | Criterion | Status |
| --- | --- | --- |
| `F1` | Alpha-anchored geometry cannot be derived from the internal action. | `OPEN_PROOF_OBLIGATION` |
| `F2` | `Omega_f` cannot be derived from the twisted Dirac/bundle action. | `OPEN_PROOF_OBLIGATION` |
| `F3` | Scheme-consistent quark ratios disagree beyond fixed tolerance bands. | `FALSIFIABLE_NUMERICAL_BRANCH` |
| `F4` | CKM outputs fail outside fixed tolerances. | `FALSIFIABLE_NUMERICAL_BRANCH` |
| `F5` | PMNS effective-extension outputs are decisively contradicted. | `EFFECTIVE_EXTENSION_BRANCH` |
| `F6` | Full twisted Dirac/H_T spectrum produces extra light states below `4*pi^2 v`. | `OPEN_SPECTRAL_THEOREM` |
| `F7` | Unscreened light scalar/topographic modes remain. | `OPEN_ACTION_LEVEL_PROOF` |
| `F8` | Higher-loop/threshold RG matching breaks coupling agreement. | `OPEN_RG_MATCHING` |
| `F9` | Any post-freeze adjustment of `a`, `S`, modes, or `Z_virt` based on residuals. | `FREEZE_CONSTRAINT` |

This release is falsifiable because it freezes constants, modes, tolerances,
and outputs before comparison.

## BHSM v1 Comparison Gates

The internal profile-scale identities and no-empirical-derivation gate are internal gates. Charged-sector, CKM/PMNS/CP, and DESI checks are comparison-only gates and are `NOT_EVALUATED_DATA_ABSENT` until target data are supplied.

## BHSM v1.0.0 Falsification And Comparison Layer

The v1.0.0 release keeps falsification outside the derivation pipeline. The
machine-readable gate artifact is:

```text
artifacts/BHSM_falsification_gates_v1.json
```

Internal gates verify package integrity and no empirical derivation inputs.
External gates require target data, scheme metadata, and comparison metadata.
If target data are absent, those gates are reported as
`NOT_EVALUATED_DATA_ABSENT`, not as internal failures.

The release remains falsifiable because the internal constants and outputs are
frozen before external comparison.
