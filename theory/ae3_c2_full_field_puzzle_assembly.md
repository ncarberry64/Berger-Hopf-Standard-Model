# AE3 current-C2 full-field puzzle assembly

## Non-serial assembly rule

BHSM completion is treated as a set of coupled puzzle sections, not as a
single line of downstream gates. A valid object may be added to any section
as soon as its local interfaces match. Promotion of a composed result still
requires a common action version, background, variational domain, state
factorization, scale/renormalization convention, and provenance chain.

This rule permits the particle, precision, scattering, localization, and
cosmology sections to advance independently without weakening their eventual
compatibility conditions.

## Current C2 quadratic piece

The retained 1,222-segment descriptor already supplies the lowest product-
Dirac angular channel, with `lambda=3/2`, for both chiralities. On element
`e`, with proper duration `h_e`, midpoint logarithmic radius `x_e`, and

```text
W_e = chirality * (3/2) * exp(-x_e),
```

the real symmetric quadratic form is

```text
K_e = S/h_e + W_e^2 M_e + W_e C,
M_e = h_e A/6,
S = [[1,-1],[-1,1]],
A = [[2,1],[1,2]],
C = [[-1,0],[0,1]].
```

Node zero is the retained C2 birth trace. The last node is removed only to
form the nested Friedrichs proof core; it is not a physical endpoint. The
stored proof centers are enclosure data and are not promoted to selected
physical histories.

The materializer reconstructs every stored diagonal, off-diagonal, mass, and
coefficient array exactly for both chiralities. It therefore attaches a real
current-C2 fermionic quadratic piece without rebuilding the upstream particle
spectrum.

## Reduced LR/HS source jet

The historical rank-16 calculation already derives the source/contact algebra
of a squared product-Dirac operator and the family factor `I3`. For a commuting
reduced LR/HS probe, write

```text
W_e(epsilon) = W_e + epsilon q p_e.
```

Direct differentiation of the current C2 form gives

```text
V_e = d K_e/d epsilon |0
    = 2 W_e q p_e M_e + q p_e C,

Q_e = d^2 K_e/d epsilon^2 |0
    = 2 (q p_e)^2 M_e.
```

These are exact real symmetric first and second action derivatives. `Q_e` is
positive semidefinite by its element factorization. No inverse, pole, fitted
coefficient, or new physical scale is introduced. The machine artifact uses
the unit probe `q=p_e=1`; arbitrary finite real profiles remain available in
the implementation.

## What this fits

This result advances three puzzle sections at once:

- the full-field section gains both current-C2 lowest-Weyl quadratic pencils
  and an exact reduced LR/HS source/contact jet;
- the identity section gains a compatible `I3` tensor attachment for the
  already-defined charged-family fibers;
- the muon section gains a current-C2 two-point operator piece.

It does not derive a dynamical HS coordinate, the broken LR saddle, a family-
noncentral returned mass operator, a simple physical muon pole, a transverse
photon vertex, a Ward identity, a renormalization prescription, or `F2(0)`.
In particular, the family factor `I3` proves that this piece alone cannot
split electron, muon, and tau masses. It is not renamed as the missing
electromagnetic vertex.

The zero-background HS--fermion mixed variation has subsequently been closed:
the mixed Hessian vanishes on the attached symmetric coefficient slice while
the third LR/HS variation remains nonzero. The current-C2 pure dynamical HS
kernel, an action-selected classical fermion Sobolev background embedding,
and the maximal-history operator remain unfitted interfaces of the common
AE3 oracle. Consequently
`CURRENT_FULL_FIELD_ACTION_COMPLETE=FALSE`,
`MUON_MAGNETIC_MOMENT_DERIVED=FALSE`, and `FULL_BHSM_COMPLETE=FALSE`.

## Reproduction

Run:

```bash
python scripts/materialize_ae3_c2_action_puzzle.py
python -m pytest tests/test_ae3_c2_action_puzzle.py -q
```

The machine-readable result is
`artifacts/action_extension/BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json`.
