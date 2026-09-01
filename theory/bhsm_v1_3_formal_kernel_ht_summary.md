# BHSM v1.3 Formal-Kernel H_T Summary

Status: `FORMAL_KERNEL_HT_SCAFFOLD_PACKAGED`

Theorem complete: `False`

BHSM v1.3A-O packages the corrected Level 2 `(H_T)` scaffold around the
formal sector-labeled kernel. The corrected reference operator is:

```text
DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
```

The old coordinate-first protected block `(0,1,2)` is superseded wherever
Level 2 `(H_T)` conclusions depended on that block.

## Coordinate-Free Kernel

```text
K_formal = span{|ell,0,0,q=0,chi=-1>, |u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}
H_perp = K_formal^perp
```

Finite sector-major realization:

```text
M(k_max)=sum_{k=0}^{k_max}(floor(k/2)+1)
ell=0, u=2M, d=4M
```

For `k_max=4`, this gives `(0,18,36)`.

## v1.3A-O Ledger

| Gate | Result | Status |
| --- | --- | --- |
| v1.3A term inventory | Level 2 terms inventoried and classified | `SCAFFOLD` |
| v1.3B sector-coupling norm bound | finite operator-norm and Weyl rows built | `NORM_BOUND_SUFFICIENT` baseline |
| v1.3C structured sector coupling | block structure and relative-bound candidate built | `RELATIVE_BOUND_CANDIDATE` |
| v1.3D uniform relative-bound scan | increasing `k_max` audit supports uniform candidate | `UNIFORM_BOUND_CANDIDATE` |
| v1.3E Hilbert-space domain | domain assumptions recorded | `DOMAIN_SCAFFOLD` |
| v1.3F state ontology | internal/virtual/state distinctions recorded | `STATE_ONTOLOGY_SCAFFOLD` |
| v1.3G zero-mode/complement split | zero-mode and complement projector scaffold recorded | `INDEX_SCAFFOLD` |
| v1.3H diagonal/mirror audit | diagonal complement clears finite threshold; mirror candidates exposed | `MIRROR_AUDIT_SCAFFOLD` |
| v1.3I mirror exclusion | chiral projector excludes generated mirrors at scaffold level | `MIRROR_EXCLUSION_SCAFFOLD` |
| v1.3J alignment audit | formal labels and coordinate-first block mismatch found | `OPEN_ALIGNMENT_GAP_FOUND` |
| v1.3K formal projector audit | coordinate-first gap fails under formal projector | `COORDINATE_ARTIFACT_FOUND` |
| v1.3L formal-kernel operator | corrected operator protects `(0,18,36)` | `FORMAL_KERNEL_GAP_RESTORED` |
| v1.3M regression/convergence | corrected lower-bound scans rerun | `FORMAL_KERNEL_CONVERGENCE_SUPPORTED` |
| v1.3N action-origin/semi-analytic bound | basis formula and complement bound packaged | `SEMI_ANALYTIC_BOUND_SCAFFOLD_PASSES` |
| v1.3O symbolic formal kernel | coordinate-free kernel/operator scaffold packaged | `COORDINATE_FREE_SCAFFOLD` |

## Corrected Bound Values

| Quantity | Value |
| --- | --- |
| required Dirac lower bound | `0.8038064161349437` |
| structured relative lower bound | `6.729508865520464` |
| exact finite lower bound | `6.8171156827281205` |
| heat-lift lower bound | `19591.98933512353` |
| corrected formal-kernel coordinates at `k_max=4` | `(0,18,36)` |

## Symbolic Operator

```text
D_FK^2 = D_diag^2 + V_Hopf + V_boundary + V_chi + K_sector + P_lift^perp
```

Term roles:

| Term | Bound status |
| --- | --- |
| `D_diag^2` | `DIAGONAL_EXACT` |
| `V_Hopf` | `SIGN_INDEFINITE_BOUNDED` |
| `V_boundary` | `SIGN_INDEFINITE_BOUNDED` |
| `V_chi` | `SIGN_INDEFINITE_BOUNDED` |
| `K_sector` | `OFF_DIAGONAL_BOUNDED` / structured relative-bound candidate |
| `P_lift^perp` | `PSD_EXACT` |
| `V_profile` | `PSD_EXACT` if the profile positivity assumption holds |

## Correct Claim

BHSM v1.3 packages a corrected formal-kernel Level 2 `(H_T)` scaffold. The
finite and semi-analytic evidence supports the corrected scaffold under the
formal sector-labeled kernel. The full no-extra-light-state theorem remains
open until the complete twisted Dirac operator, topological index theorem,
mirror exclusion, profile positivity, and infinite-basis complement bound are
proven.

## Limitations

- This is a corrected formal-kernel scaffold, not the full analytic `(H_T)` spectrum.
- Coordinate-first Level 2 conclusions are superseded only where they depended on `(0,1,2)`.
- The current corrected reference is `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`.
- No frozen BHSM v1.0/v1.1 predictions, constants, tolerances, or branches are changed.
