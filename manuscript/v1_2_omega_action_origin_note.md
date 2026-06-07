# BHSM v1.2 Omega Action-Origin Note

This development note extends the Berger-Hopf Standard Model boundary-operator
program beyond the v1.1 public release. It does not change the frozen v1.0 or
v1.1 prediction packages, and it does not retune any residual.

## Objective

The current charged-sector boundary operators are

```text
Omega_ell = -q + 2j = 3
Omega_u   =  q - 2j = 6
Omega_d   =  q + 4j = 12
```

In v1.1 these operators were ACTION_LINKED, not fully action-derived. The
v1.2 branch introduces an action-origin scaffold in which the coefficients are
derived inside an explicit symbolic sector boundary functional.

## Boundary Functional Inputs

The functional combines:

- Hopf fiber phase;
- base S^2 node phase;
- weak chirality;
- weak component;
- coframe triplet participation;
- Higgs-selected U(1) boundary phase;
- generation index and sector winding.

The coefficient rule is:

```text
c_q = hopf_fiber_orientation * hypercharge_higgs_boundary
c_j = base_node_phase * chirality_sign * weak_component_sign * coframe_participation
target = family_index * sector_winding_multiplier
```

## Coefficient Status

| Sector | Fiber coefficient | Base coefficient | Target | Status |
| --- | ---: | ---: | ---: | --- |
| lepton | -1 | 2 | 3 | DERIVED_FROM_BOUNDARY_FUNCTIONAL |
| up | 1 | -2 | 6 | DERIVED_FROM_BOUNDARY_FUNCTIONAL |
| down | 1 | 4 | 12 | DERIVED_FROM_BOUNDARY_FUNCTIONAL |

This status means the coefficients follow from the explicit symbolic boundary
functional implemented in `src/omega_derivation.py`. It does not mean the
operators have been fully derived from variation or spectrum of the complete
Berger-Hopf internal action.

## Dependency Graph

The coefficient dependencies are:

| Coefficient | Symbolic source | Boundary/action terms |
| --- | --- | --- |
| `fiber_q` | `hopf_fiber_orientation * hypercharge_higgs_boundary` | `I_HOPF`, `I_U1` |
| `base_j` | `base_node_phase * chirality_sign * weak_component_sign * coframe_participation` | `I_BASE`, `I_WEAK`, `I_COF` |
| `target` | `family_index * sector_winding_multiplier` | `I_BDY` |

Open parts:

- derive the sector boundary functional from variation of the full internal action;
- derive coframe triplet participation from the complete bundle action;
- derive the Higgs-selected U(1) boundary phase from the full topological sector;
- compute the full twisted Dirac/bundle spectrum.

## What v1.2 Proves and Does Not Prove

Within the scaffold, v1.2 proves that the charged-sector omega coefficients
follow from the explicit symbolic sector boundary functional.

It does not prove that the full twisted Dirac/bundle action uniquely generates
that functional. That remains the central action-origin proof obligation.

## Mode Ledger Recovery

Using the action-origin functional, the expected charged-sector ledger is
recovered without empirical masses or CKM values:

| Sector | Heavy | Middle | Light |
| --- | --- | --- | --- |
| charged leptons | (0,0) | (5,2) | (9,3) |
| up quarks | (0,0) | (6,0) | (10,1) |
| down quarks | (0,0) | (6,3) | (8,2) |

## Frozen Package Protection

The v1.2 action-origin program does not modify:

- `BHSM_BARE_V1`;
- `BHSM_DRESSED_V1_CANDIDATE`;
- `a = alpha^{-1}/(12*pi^2)`;
- `S = 1/(4*pi)`;
- frozen tolerances, ledgers, prediction outputs, or release tags.

## Remaining Gap

The remaining proof obligation is to obtain the sector boundary functional
itself from the full Berger-Hopf twisted Dirac/bundle action. Until then,
`Omega_f` is action-origin scaffolded, not a completed first-principles
derivation.
