# BHSM v1.3C Structured Sector-Coupling Relative-Bound Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3C investigates whether the Level 2 sector-coupling block has enough
internal structure to support stronger relative-bound estimates than raw
finite-matrix norms.

This phase does not alter frozen BHSM v1.0/v1.1 predictions, canonical
constants, tolerances, mode ledger, public release tags, or v1.2 action-origin
outputs.

## Structural Findings

The Dirac-level sector-coupling block satisfies these Level 2 selection rules:

| Structural property | Result |
| --- | --- |
| Connects distinct sectors only | `True` at Dirac level |
| Preserves `k` | `True` |
| Preserves `j` | `True` |
| Preserves Hopf charge `q` | `True` |
| Preserves chirality | `True` |
| Vanishes on protected zero-mode block | `True` |
| Sparse support | `True` in the finite basis |
| Banded support | block-banded after `(k,j,chirality)` ordering |
| Finite rank | finite rank at fixed `k_max`; not certified finite rank as `k_max -> infinity` |
| Compactness | relative-bound candidate only; no compactness theorem |

After squaring, the induced `D^dagger D` perturbation includes same-sector
diagonal contributions from the square of the off-diagonal Dirac block. The
audit therefore distinguishes Dirac-level off-diagonal structure from the
Dirac-squared perturbation.

## Structured Relative-Bound Certificate

The structured finite-basis bound computes:

```text
a_K = || B^{-1/2} K B^{-1/2} ||
```

on the protected complement, where `B = D_0^dagger D_0` and `K` is the
sector-coupling perturbation.

Baseline result:

| Quantity | Value |
| --- | --- |
| `a_K` | `0.015621013485509948` |
| `b_K` | `0.0` |
| Base lower bound | `1.4641` |
| Structured lower bound | `1.4412292741558648` |
| Full finite-basis lower bound | `1.463040025299567` |
| Required Dirac lower bound | `0.8038064161349437` |
| Classification | `RELATIVE_BOUND_CANDIDATE` |

The structured certificate is sufficient in the Level 2 finite-basis baseline,
but it is deliberately not classified as a completed theorem.

## Robustness Result

The structured scan covers:

- `k_max = 4, 6, 8, 10, 12, 16, 20`
- `a = alpha^{-1}/(12*pi^2), 1.0, 0.573`
- baseline and v1.3B perturbation cases

Summary:

| Quantity | Result |
| --- | --- |
| Cases | `84` |
| All structured finite-basis bounds sufficient | `True` |
| All finite-basis gaps pass | `True` |
| Classification in scan | `RELATIVE_BOUND_CANDIDATE` |

## Claim Boundary

BHSM v1.3C investigates structured relative bounds for the Level 2
sector-coupling block. It may certify stronger finite-basis or semi-analytic
control, but it does not prove the full `H_T` theorem unless the
zero-mode/complement and infinite-basis limits are also certified.

## Recommended v1.3D Task

The next task is to convert the finite structured relative-bound candidate into
a uniform-in-`k_max` estimate, or to isolate which part of the zero-mode /
complement construction prevents that upgrade.
