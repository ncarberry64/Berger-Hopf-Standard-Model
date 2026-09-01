# BHSM v1.3D Uniform-in-k_max Relative-Bound Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3D tests whether the structured sector-coupling relative-bound
certificate from v1.3C remains stable as the finite basis is enlarged. The
goal is to identify whether the Level 2 sector-coupling block is a plausible
uniform relative-bound candidate for the future infinite-basis `H_T` problem.

This phase does not alter frozen BHSM v1.0/v1.1 predictions, canonical
constants, tolerances, mode ledger, public release tags, or v1.2 action-origin
outputs.

## Scan Definition

The scan covers:

- `k_max = 4, 6, 8, 10, 12, 16, 20, 24, 32`
- `a = alpha^{-1}/(12*pi^2)`, `1.0`, `0.573`
- baseline and v1.3B sector-coupling perturbation cases
- natural cutoff `Lambda^2 = 1/(4*pi)`

Each row reports basis size, sparsity, mode-block band width, spectral norm,
row-sum norm, block-wise norm, `a_K`, `b_K`, structured lower bound, finite
complement lower bound, and pass/fail against the required Dirac lower bound.

## Uniform Scan Result

| Quantity | Result |
| --- | --- |
| Scan rows | `108` |
| Classification | `UNIFORM_BOUND_CANDIDATE` |
| All rows pass required bound | `True` |
| All `b_K` values remain zero | `True` |
| Max `a_K` | `0.03095889839310559` |
| Min structured lower bound | `1.418773076862654` |
| Min finite-basis lower bound | `1.4599918132873242` |
| Max mode-block bandwidth | `2` |

## Trend Summary

For the canonical baseline:

| Quantity | Trend |
| --- | --- |
| `a_K` | stable |
| `b_K` | stable at zero |
| sparsity | increasing |
| band width | stable |
| structured lower bound | stable |
| finite-basis complement lower bound | stable |

## Interpretation

The scan supports the sector-coupling block as a uniform-bound candidate across
the tested finite truncations. It does not prove the infinite-basis result.
The remaining blockers are:

- finite scans do not prove a `k_max`-uniform analytic estimate;
- the zero-mode/complement separation is still finite-basis inserted/projected;
- sector-coupling rank grows with `k_max`, so compactness is not certified;
- bounded mode-block bandwidth still needs an action-level infinite-basis
  proof.

## Claim Boundary

BHSM v1.3D tests whether the structured sector-coupling relative bound is
uniform across increasing finite-basis truncations. It does not prove the full
`H_T` theorem unless the zero-mode/complement split and infinite-basis limit
are certified.

## Recommended v1.3E Task

Convert the observed finite uniform-bound candidate into an analytic
infinite-basis estimate, or isolate the precise Hilbert-space domain and
zero-mode complement assumptions needed to state that estimate rigorously.
