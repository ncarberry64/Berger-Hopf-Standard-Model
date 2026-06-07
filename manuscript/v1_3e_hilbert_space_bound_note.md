# BHSM v1.3E Hilbert-Space Domain and Infinite-Basis Bound Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem status: `THEOREM_SCAFFOLD`

Theorem complete: `False`

## Purpose

BHSM v1.3E defines the Hilbert-space/domain assumptions under which the
structured sector-coupling relative bound from v1.3C/v1.3D would extend beyond
finite truncations. This phase does not prove the full `H_T` theorem.

No frozen BHSM v1.0/v1.1 predictions, canonical constants, tolerances, mode
ledger, public release tags, or v1.2 action-origin outputs are changed.

## Hilbert-Space Domain

The formal basis labels are:

```text
e_{k,j,q,chi,sector}
```

with:

- `k` in nonnegative integers;
- `0 <= j <= floor(k/2)`;
- `q = k - 2j`;
- `chi in {-1, +1}`;
- `sector in {lepton, up, down}`.

The protected zero-mode scaffold uses three labels:

| k | j | q | chi | sector |
| --- | --- | --- | --- | --- |
| `0` | `0` | `0` | `-1` | `lepton` |
| `0` | `0` | `0` | `-1` | `up` |
| `0` | `0` | `0` | `-1` | `down` |

The complement `H_perp` is the closed orthogonal complement of this protected
subspace. The full proof that this is the physical kernel/complement remains
open.

## Operator Domains

The scaffold records domains for:

- diagonal Berger/Dirac kinetic operator `D0^2`;
- sector-coupling perturbation `K_sector`;
- common finite-support dense core;
- protected zero-mode subspace;
- orthogonal complement `H_perp`.

## Assumptions A1-A6

| ID | Status | Statement |
| --- | --- | --- |
| `A1` | `SUPPORTED_BY_FINITE_EVIDENCE` | `K_sector` preserves `(k,j,q,chi)` and only mixes charged-sector labels. |
| `A2` | `SUPPORTED_BY_FINITE_EVIDENCE` | `K_sector` has uniformly bounded mode-block bandwidth. |
| `A3` | `ASSUMED_FOR_THEOREM_SCAFFOLD` | `K_sector` is `D0^2`-relative bounded on `H_perp` with `a_K <= 0.04`, `b_K = 0`. |
| `A4` | `SUPPORTED_BY_FINITE_EVIDENCE` | `K_sector` vanishes on protected zero modes. |
| `A5` | `OPEN` | The complement projection is well-defined and commutes with the relevant block decomposition. |
| `A6` | `ASSUMED_FOR_THEOREM_SCAFFOLD` | The diagonal complement lower bound clears the relative-bound requirement. |

## Conservative Candidate

The finite evidence bridge from v1.3D found:

- observed max `a_K = 0.03095889839310559`;
- all observed `b_K = 0`;
- minimum structured lower bound `1.418773076862654`;
- required Dirac lower bound `0.8038064161349437`.

v1.3E proposes the conservative theorem-scaffold assumption:

```text
a_K^max = 0.04, b_K = 0
```

Using candidate diagonal lower bound `d0 = 1.4641`:

```text
(1 - 0.04) d0 = 1.405536
```

with margin:

```text
1.405536 - 0.8038064161349437 = 0.6017295838650562
```

This is an assumption candidate, not a fitted theorem.

## Conditional Implication

If A1-A6 hold on the full Hilbert-space domain, then `K_sector` is
`D0^2`-relative bounded on `H_perp` and cannot close the required complement
gap.

## Claim Boundary

BHSM v1.3E defines the Hilbert-space/domain assumptions under which the
structured sector-coupling relative bound would extend beyond finite
truncations. It does not prove the full `H_T` theorem until those assumptions
and the zero-mode/complement split are derived from the complete operator.

## Recommended v1.3F Task

Prove or further constrain A5 and A6: the full protected kernel/complement
projection and the diagonal complement lower bound on the infinite Hilbert
space.
