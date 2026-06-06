# Gate 25C Boundary-Operator Scaffold

This note documents the symbolic scaffold for the boundary operators used in
Gate 25B. As of Gate 25D, the operators are `ACTION_LINKED`: their coefficients
are reproduced by an explicit symbolic phase-contribution rule tied to Hopf
fiber orientation, base-node phase, chirality, weak component, coframe factor,
and family index. They remain not fully `ACTION_DERIVED` until obtained from
variation/spectrum of the full twisted Dirac/bundle action.

## Representation Data Used

The scaffold records one boundary object per charged sector:

| Sector | Color Rank | Weak Component | Hypercharge | Family Index | Hopf Rule |
| --- | ---: | --- | --- | ---: | --- |
| lepton | 1 | lower | -1/2 | 3 | odd |
| up | 3 | upper | 1/6 | 3 | even, q >= 6 |
| down | 3 | lower | 1/6 | 3 | q = 0 mod 4 |

The current values are representation labels for the operational map. They are
not yet produced by varying or diagonalizing the full internal action.

## Operational Boundary Equations

With Hopf charge

```text
q = k - 2j
```

the scaffold records:

```text
Omega_lepton = -q + 2j = 3
Omega_up     =  q - 2j = 6
Omega_down   =  q + 4j = 12
```

The coefficient pairs are:

```text
lepton: (fiber, base) = (-1,  2)
up:     (fiber, base) = ( 1, -2)
down:   (fiber, base) = ( 1,  4)
```

## Symbolic Phase Rule

The Gate 25D action-link rule records:

- Hopf coefficient from fiber phase orientation.
- Base coefficient from base-node phase, weak-component sign, chirality sign,
  and coframe factor.
- Target from family index times sector winding multiplier.

| Sector | Hopf Fiber Phase | Base Node Phase | Chirality Sign | Weak Sign | Coframe Factor | Family Index | Winding Multiplier | Coefficients | Target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| lepton | -1 | 1 | 1 | 1 | 2 | 3 | 1 | `(-1, 2)` | 3 |
| up | 1 | 1 | -1 | 1 | 2 | 3 | 2 | `(1, -2)` | 6 |
| down | 1 | 1 | 1 | 1 | 4 | 3 | 4 | `(1, 4)` | 12 |

All three boundary records are marked `ACTION_LINKED`, not `ACTION_DERIVED`.

## Ledger Recovery

On the nonnegative Hopf-charge Berger scan domain `0 <= j <= floor(k/2)`, the
heavy mode `(0,0)` is included separately. The first two nonzero admissible
modes by increasing Berger action are:

| Sector | Selected Modes |
| --- | --- |
| lepton | `(5,2)`, `(9,3)` |
| up | `(6,0)`, `(10,1)` |
| down | `(6,3)`, `(8,2)` |

This recovers the charged-sector ledger without observed mass inputs.

## Remaining Derivation Gap

The open problem is to derive the coefficient pairs

```text
(-1, 2), (1, -2), (1, 4)
```

from the twisted Dirac/bundle action.

The future target is an action-level derivation from:

- chirality;
- weak component;
- coframe triplet structure;
- Hopf/base boundary phases.

Until that derivation is supplied, the boundary operators remain action-linked
symbolic selection rules and should not be described as first-principles
consequences.
