# BHSM v1.3A H_T Term Inventory and Bound Classification Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3A inventories the existing Level 2 twisted Dirac / `H_T` scaffold and
classifies each term by its current lower-bound status. This is a preparatory
analytic-bound audit. It does not change the frozen BHSM v1.0/v1.1 predictions,
constants, tolerances, mode ledger, or v1.2 action-origin outputs.

The target remains:

```text
H_T|_{H_perp} >= (4 pi^2 v)^2
```

or, in the dimensionless Hopf-gap normalization used in the repository:

```text
H_T|_{H_perp} >= mu_H = 64 pi^5
```

## Inventory Summary

| Term | Current classification | Lower-bound method | Can lower complement gap |
| --- | --- | --- | --- |
| `berger_dirac_kinetic` | `DIAGONAL_EXACT` | exact diagonal minimum and restricted min-max after squaring | `False` |
| `hopf_twist` | `SIGN_INDEFINITE_BOUNDED` | Weyl bound with finite Hopf-charge range | `True` |
| `boundary_term` | `SIGN_INDEFINITE_BOUNDED` | Weyl bound with finite boundary-residual range | `True` |
| `chirality_term` | `SIGN_INDEFINITE_BOUNDED` | Weyl bound from explicit chirality coefficient | `True` |
| `sector_coupling` | `OFF_DIAGONAL_BOUNDED` | Gershgorin and restricted min-max estimates | `True` |
| `heat_lift` | `PSD_EXACT` | monotone heat-lift inequality | `False` |
| `psd_profile` | `PSD_EXACT` | PSD nonnegative Weyl contribution | `False` |
| `zero_complement_projector` | `FINITE_BASIS_ONLY` | finite-basis restricted complement projection | `False` |

## Current Best Lower-Bound Chain

1. Restrict the finite Level 2 Dirac matrix to the complement of the three
   protected zero modes.
2. Use the exact finite-basis diagonal contribution and explicit finite
   Hopf-charge / boundary-residual ranges for sign-indefinite diagonal terms.
3. Control off-diagonal sector couplings with Gershgorin and restricted
   min-max bounds.
4. Square the symmetric Level 2 Dirac matrix and take the conservative
   complement lower bound.
5. Apply the monotone heat lift using the fixed natural cutoff
   `Lambda^2 = 1/(4*pi)`.
6. Add only positive-semidefinite curvature/profile contributions.

## Weakest Blocks

The weakest analytic block is `zero_complement_projector`, because the full
action-level statement `dim ker D_twist = 3` and the infinite-dimensional
complement decomposition remain open.

The weakest matrix term is `sector_coupling`, because its present control is
finite-basis Gershgorin / min-max rather than an infinite-basis operator-norm
bound.

## Claim Boundary

BHSM v1.3A inventories and classifies the Level 2 `H_T` operator terms for
analytic-bound development. It does not prove the full no-extra-light-state
theorem.

## Next Technical Target

The recommended v1.3B task is to derive an analytic or semi-analytic
infinite-basis bound for the off-diagonal sector-coupling block while keeping
the protected zero-mode projector explicit.
