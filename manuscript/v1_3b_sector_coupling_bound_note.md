# BHSM v1.3B Sector-Coupling Operator-Norm and Relative-Bound Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3B strengthens the Level 2 `H_T` spectral-bound program by isolating
the off-diagonal sector-coupling block and auditing whether finite operator
norms certify that the block does not close the complement gap.

The audit does not alter frozen BHSM v1.0/v1.1 predictions, constants,
tolerances, mode ledger, or v1.2 action-origin outputs.

## Perturbation Setup

The audited decomposition is:

```text
D^2 = D_0^2 + K_sector
```

where `D_0` is the Level 2 Dirac matrix with `sector_coupling = 0` and
`offdiag_boundary_coupling = 0`, and `K_sector` is the resulting finite
Dirac-squared perturbation:

```text
K_sector = D_full^dagger D_full - D_0^dagger D_0
```

The audit is performed on the finite protected complement `H_perp`.

## Baseline Result

| Quantity | Value |
| --- | --- |
| Required Dirac lower bound | `0.8038064161349437` |
| Base complement lower bound before sector coupling | `1.4641` |
| Full complement lower bound with sector coupling | `1.463040025299567` |
| Sector perturbation spectral norm | `0.4720872031830534` |
| Sector perturbation Frobenius norm | `1.5673539133570085` |
| Sector perturbation row-sum norm | `0.47862045138889886` |
| Weyl lower bound | `0.9920127968169465` |
| Relative bound `a_K` | `0.3224419118796895` |
| Classification | `NORM_BOUND_SUFFICIENT` |

For the Level 2 baseline, Weyl's estimate:

```text
lambda_1(D_0^2 + K_sector) >= lambda_1(D_0^2) - ||K_sector||
```

still clears the required Dirac lower bound.

## Robustness Result

The robustness scan covers:

- `k_max = 4, 6, 8, 10, 12, 16`
- `a = 0.573, 1.0, alpha^{-1}/(12*pi^2)`
- baseline sector coupling and small perturbations

Summary:

| Quantity | Result |
| --- | --- |
| Cases | `72` |
| All finite-basis cases pass | `True` |
| All norm bounds sufficient | `False` |
| Worst Weyl lower bound | `-1.8010264414387993` |
| Worst full complement lower bound | `1.4599918132887826` |

The scan therefore distinguishes norm-certified cases from cases where the
finite-basis spectrum still passes but the conservative norm bound is not
sufficient. Those cases are not reported as analytic proofs.

## Claim Boundary

BHSM v1.3B bounds the Level 2 sector-coupling block by operator-norm and
relative-bound estimates. It does not prove the full `H_T`
no-extra-light-state theorem unless the complement gap is certified
independently of finite-basis assumptions.

## Recommended v1.3C Task

The next task is to derive an infinite-basis operator-norm or relative-bound
estimate for the sector-coupling block, ideally using the sector adjacency
structure and bounded coupling strengths, while keeping the zero-mode
projector proof obligation explicit.
