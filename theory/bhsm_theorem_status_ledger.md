# BHSM Theorem Status Ledger

Theorem complete: `False`
Hidden circularity detected: `False`
Empirical residual dependency detected: `False`

## Ledger Rows

| ID | Status | Completed | Allowed claim | Forbidden upgrade |
| --- | --- | --- | --- | --- |
| `frozen_v1_predictions` | `FROZEN_PREDICTION` | `True` | Frozen no-retuning model outputs are reproducible. | Do not claim all entries are final confirmed predictions. |
| `omega_f` | `BOUNDARY_FUNCTIONAL_DERIVED` | `False` | Derived from symbolic sector boundary functional and parent-action scaffold. | Do not claim complete action derivation. |
| `parent_action` | `PARENT_ACTION_REDUCED` | `False` | Reduced from symbolic parent scaffold under current axioms. | Do not claim full internal action proven. |
| `formal_kernel` | `BASIS_REALIZED` | `False` | Coordinate-free scaffold and finite basis realization are implemented. | Do not claim full index theorem. |
| `ht_gap` | `SEMI_ANALYTIC_SCAFFOLD` | `False` | Corrected formal-kernel finite/semi-analytic scaffold clears current thresholds. | Do not claim no-extra-light-state theorem proven. |
| `scalar_decoupling` | `FINITE_BASIS_SCAFFOLD` | `False` | v1.6 screening scaffold conditionally excludes current fifth-force channels with exactly one Higgs projection and no current forbidden/open scalar risks. | Do not claim scalar decoupling fully proven. |
| `qcd_rg` | `OPEN` | `False` | Approximate/reference-set scaffolds are implemented. | Do not claim precision QCD matching complete. |
| `virtual_dressing` | `ADOPTION_CANDIDATE` | `False` | Dressed branch remains candidate and changes only c/t. | Do not claim dressed branch final. |

## Open Obligations

1. Prove the full twisted Dirac / H_T spectrum and infinite-basis complement bound.
2. Prove Index(D_twist)=3 and complete mirror-mode exclusion from the full operator.
3. Prove scalar/topographic decoupling from the full internal action beyond the v1.5 action scaffold and v1.6 screening scaffold.
4. Complete precision QCD/RG threshold matching for quark mass comparisons.
5. Derive full flavor matrices from the complete action rather than internal-rule screens.

## v1.4 Precision QCD/RG Update

The `qcd_rg` row remains `OPEN`. Branch `bhsm-v1.4-precision-qcd-rg` adds a
precision-oriented comparison architecture with placeholder PDG-style and
precision-QCD reference sets, but no final precision-QCD reference values are
supplied. The forbidden upgrade remains: do not claim precision QCD matching
complete.

## v1.5 Scalar/Topographic Action-Decoupling Update

The `scalar_decoupling` row remains incomplete. Branch
`bhsm-v1.5-scalar-action-proof` adds an action-level scalar/topographic
scaffold with exactly one Higgs projection, heavy/H_T lifted complement modes,
derivative/curvature screened modes, virtual-only channels, and an explicit
forbidden unscreened light scalar falsifier.

## v1.6 Scalar/Topographic Screening Update

Branch `bhsm-v1.6-scalar-screening-proof` derives or constrains
derivative-screening and curvature-screening channels as sufficient
scaffold-level conditions. It reports zero current `OPEN_SCALAR_RISK` rows and
does not claim a full scalar-screening theorem from the complete action.
