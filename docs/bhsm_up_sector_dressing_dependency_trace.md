# PO-BH-67 - Up-Sector Dressing Dependency Trace

Current public status: structural architecture integrated conditional; numerical closure open.

This trace follows where the up-sector virtual dressing enters BHSM code,
documentation, and data. The goal is to decide whether the actual released
middle-up dressing source is linked to the PO-BH-66 two-door virtual pair.

No frozen predictions are changed. No official predictions are changed. No
observed quark masses, charm/top ratio, up/top ratio, CKM values, PMNS values,
neutrino data, measured alpha, or target ratios are used to justify
`Z_virt^{u,2}`.

## Dependency Trace Table

| object | source file | source line or key | depends on | feeds into | uses observed data? | links to two-door pair? | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| frozen dressed branch builder | `src/bhsm_v1.py` | `build_bhsm_dressed_v1_candidate` | `pure_fiber_middle_up_rule(); apply_virtual_dressing(model, (rule,))` | `BHSM_DRESSED_V1_CANDIDATE` frozen `c/t` dressing | no | no | `FROZEN_PREDICTION_REFERENCE` | the frozen branch applies the existing rule but is not a derivation source |
| dressed branch freeze guard | `src/bhsm_v1.py` | `BHSMVersion.__post_init__` | sector=`up_quarks`, generation=`middle`, mode=`(6,0)`, factor=`0.5` | rejects non-frozen dressed-branch metadata | no | no | `FROZEN_PREDICTION_REFERENCE` | guards the released value and scope without deriving the virtual pair |
| pure-fiber middle-up rule | `src/virtual_environment.py` | `pure_fiber_middle_up_rule` | `j=0`, `q=6`, `Omega_u=6`, `WEAK_DOUBLE_PROJECTION`, factor=`0.5` | `apply_virtual_dressing` and `BHSM_DRESSED_V1_CANDIDATE` | no | no | `STRUCTURAL_SOURCE` | uses internal mode and boundary data, but not the explicit PO-BH-66 two-door pair |
| virtual dressing application | `src/virtual_environment.py` | `apply_virtual_dressing/_rule_applies` | mode-specific scope and model generation mode `(6,0)` | dressed ratio copy used by frozen branch and diagnostics | no | no | `STRUCTURAL_SOURCE` | applies the rule locally by sector/generation/mode, but does not prove two-door sampling |
| virtual dressing adoption audit | `theory/virtual_dressing_adoption_audit.md` | C1-C6 criteria | sector, mode, Hopf charge, base index, boundary equation, weak-doublet projection | `ADOPTION_CANDIDATE` status language | no | no | `LEGACY_NUMERICAL_CANDIDATE` | records representation-data linkage and output preservation, but says full loop derivation remains open |
| dimension-ratio route | `docs/bhsm_up_sector_virtual_door_applicability.md` | Candidate Virtual Pair | `V_pair^u=span{door_u,door_d}`, `rank(A_virt^u)=1`, `dim(V_pair^u)=2` | `Z_virt_u2_dimension_ratio` | no | yes | `STRUCTURAL_SOURCE` | formalizes the two-door ratio but keeps applicability open |
| frozen prediction reference | `docs/frozen_predictions.md` | `BHSM_DRESSED_V1_CANDIDATE` row | released `Z_virt^{u,2}=1/2` applied only to `c/t` | public frozen prediction package | no | no | `FROZEN_PREDICTION_REFERENCE` | preserves the release; it cannot be used as a derivation |
| bare vs dressed manuscript comparison | `manuscript/bare_vs_dressed_branches.md` | bare/dressed branch table | released bare and dressed values | human-readable release comparison | no | no | `FROZEN_PREDICTION_REFERENCE` | documents branch difference without proving the source of the factor |
| threshold/common-scale comparison rows | `src/virtual_environment.py` | `_comparison_rows` and `adoption_report` | threshold references after dressed ratios are computed | diagnostic residual tables | yes | no | `COMPARISON_ONLY` | comparison occurs after the rule is defined and cannot justify the factor |
| CKM virtual mixing candidate | `src/bhsm_virtual_mixing_solution.py` | `s23_candidate = s23_frozen * (Z_virt^{u,2})^(1/16)` | released `Z_virt` and exploratory `1/16` exponent | non-official CKM 2-3 mixing diagnostic | yes | no | `COMPARISON_ONLY` | exploratory mixing candidate cannot derive the mass dressing factor |

## Applicability Decision

The actual dressed-branch path is:

```text
build_bhsm_dressed_v1_candidate
  -> pure_fiber_middle_up_rule()
  -> apply_virtual_dressing(model, (rule,))
```

The source rule is local to:

```text
sector = up_quarks
generation = middle
mode = (6,0)
j = 0
q = 6
Omega_u = 6
source = WEAK_DOUBLE_PROJECTION
factor = 1/2
```

That is a structural source, but the trace does not find an explicit dependency
from the actual dressing source to the PO-BH-66 two-door pair
`V_pair^u=span{door_u,door_d}`. Therefore:

```text
Z_virt_u2_applicability: OPEN_LOCALIZABLE
Z_virt_u2_dimension_ratio: STRONG_DERIVATION_CANDIDATE
legacy_Z_virt_u2_numerical_candidate: LOCALIZED_NOT_DERIVED
Z_virt_u2_mass_fit_route: FORBIDDEN_AS_DERIVATION
```

Allowed conservative claim:

```text
BHSM has a dimension-ratio candidate for Z_virt^{u,2}=1/2,
but the applicability of that ratio to the actual middle up-sector virtual
correction remains open.
```

## Validation / Invalidation Ledger

Validated:

- dimension-ratio mechanics from PO-BH-66 remain valid;
- two-door virtual interpretation remains a strong candidate;
- no mass input may justify `Z_virt`;
- frozen prediction references are not derivation sources;
- comparison-only residual rows are not derivation sources.

Invalidated or downgraded:

- any source that treats `Z_virt` as derived only because it appears in frozen predictions;
- any source that treats charm/top agreement as derivation;
- any source that uses observed ratios to choose the factor.

Still open:

- actual applicability link;
- `rho_ch`;
- `eta_l`;
- `Pi_l`;
- `alpha_geom`;
- numerical mass closure;
- CKM numerical closure;
- PMNS numerical closure;
- neutral/topographic suppression values.
