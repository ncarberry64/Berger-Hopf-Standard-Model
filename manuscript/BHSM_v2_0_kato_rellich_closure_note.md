# BHSM v2.0 Kato-Rellich Perturbation Closure Note

Branch: `bhsm-v2.0-kato-rellich-perturbation-closure`

## Purpose

BHSM v2.0 attacks the perturbation side of the Kato-Rellich route after v1.9 closed the diagonal reference operator foundation.

The reference operator remains:

```text
A0 = D_diag^2
```

with `DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN` and `GRAPH_NORM_DOMAIN_PROVEN`.

## Perturbation

The perturbation inventory is:

```text
V = V_Hopf + V_boundary + V_chi + K_sector
```

with heat lift and PSD profile tracked as additional positive/domain-relevant terms.

## v2.0 Status

| Chain Element | Status |
| --- | --- |
| Perturbation symmetry | `PERTURBATION_SYMMETRY_CONDITIONAL` |
| Perturbation domain inclusion | `PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL` |
| Relative-bound closure | `RELATIVE_BOUND_CONDITIONAL` |
| Kato-Rellich closure | `KATO_RELLICH_CLOSURE_CONDITIONAL` |
| Lower-bound preservation | `LOWER_BOUND_CONDITIONAL` |
| H_T dependency | `HT_THEOREM_BLOCKED_BY_PERTURBATION` |

## Relative Bound

The favorable relative-bound estimate is preserved:

```text
a <= 0.015621013485509948 < 1
```

But this is not a completed proof because Hopf, boundary, and sector-coupling terms still require complete infinite-basis relative-bound and domain-inclusion proofs.

## Lower Bound

The conditional lower-bound estimate clears the required Dirac threshold, but it is not yet a theorem on the formal complement because formal-complement stability, index, and mirror exclusion are still outside this branch.

## Limitation

This branch does not prove the full H_T theorem and does not permit final paper or Zenodo release. It sharply identifies the next obstruction: perturbation domain inclusion and complete infinite-basis relative bounds.

