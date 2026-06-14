# BHSM Boundary Action Closure Candidate

## Problem Statement

The P0 blocker is `BOUNDARY_OPERATORS_NOT_ACTION_DERIVED`: the current BHSM repo recovers the charged-sector mode ledger using operational omega operators, but the operators are not yet forced by a full action, spectral condition, or boundary principle.

## Existing Scaffold Status

Previous audits classified the status as `STRUCTURALLY_MOTIVATED_NOT_DERIVED` or `ACTION_LINKED`, not action-derived.

## Proposed Minimal Boundary Action

Candidate functional:

```text
S_boundary[f] = integral_boundary Psi_f^dagger B_f(q,j,Y,T3,color,component,N_gen) Psi_f dSigma
B_f = sign(Y_f) q - 4 T3_f C_f j
target_f = N_gen W_f
```

Here `C_f` is a coframe multiplier and `W_f` is a sector boundary winding. Both are structural candidate rules, not yet derived from the complete boundary variation.

## Allowed Ingredients

- Hopf fiber charge `q`
- base/spin index `j`
- hypercharge sign `Y`
- weak isospin `T3`
- weak component
- color rank / coframe participation
- family index

## Derivation Attempt

The ansatz computes fiber signs from hypercharge orientation and base signs from `-4*T3*C_f`. It reproduces the operational pattern without using masses, CKM values, or residual minimization. It does not yet prove the coframe multiplier or winding rule.

## Derived Candidate Generators

| Sector | Candidate Omega | Forced by action | Unproven rules |
| --- | --- | --- | --- |
| `lepton` | `Omega_lepton = -q + 2j = 3` | `False` | `coframe_multiplier(field) not derived from an action variation; sector_boundary_winding(field) not derived from a spectral boundary condition` |
| `up` | `Omega_up = q - 2j = 6` | `False` | `coframe_multiplier(field) not derived from an action variation; sector_boundary_winding(field) not derived from a spectral boundary condition` |
| `down` | `Omega_down = q + 4j = 12` | `False` | `coframe_multiplier(field) not derived from an action variation; sector_boundary_winding(field) not derived from a spectral boundary condition` |

## Derivation Of Lepton Operator

`Y=-1/2` gives fiber orientation `-q`; `T3=-1/2` with `C_f=1` gives `+2j`; `N_gen=3` and `W_f=1` give target `3`.

## Derivation Of Up-Sector Operator

`Y=1/6` gives fiber orientation `+q`; `T3=+1/2` with `C_f=1` gives `-2j`; `N_gen=3` and `W_f=2` give target `6`.

## Derivation Of Down-Sector Operator

`Y=1/6` gives fiber orientation `+q`; `T3=-1/2` with colored lower-component `C_f=2` gives `+4j`; `N_gen=3` and `W_f=4` give target `12`.

## Whether Coefficients Are Forced Or Assumed

Classification: `STRUCTURALLY_MOTIVATED_CANDIDATE`
Coefficients forced: `False`
Coefficients inserted: `False`

The coefficients are not directly inserted as `(-1,2)`, `(1,-2)`, and `(1,4)`, but the coframe multiplier and sector winding rule are still candidate rules. That prevents promotion to `BOUNDARY_ACTION_DERIVED`.

## Selected-Mode Checks

| Sector | Mode | q | Omega | Target | Match |
| --- | --- | --- | --- | --- | --- |
| `lepton` | `(5, 2)` | `1` | `3` | `3` | `True` |
| `lepton` | `(9, 3)` | `3` | `3` | `3` | `True` |
| `up` | `(6, 0)` | `6` | `6` | `6` | `True` |
| `up` | `(10, 1)` | `8` | `6` | `6` | `True` |
| `down` | `(6, 3)` | `0` | `12` | `12` | `True` |
| `down` | `(8, 2)` | `4` | `12` | `12` | `True` |

## Consequences For Z_virt^{u,2}=1/2

Helps derive `Z_virt^{u,2}=1/2`: `False`.

## Consequences For CKM 1/16 Exponent

Helps derive CKM `1/16`: `False`.

## Promotion Criteria

- derive coframe_multiplier(field) from the boundary variation
- derive sector_boundary_winding(field) from the spectral or self-adjoint boundary condition
- show no competing structural ansatz recovers the ledger with different operators
- keep frozen predictions unchanged through promotion

## Rejection Criteria

- coframe multiplier is shown to be fitted to the down-sector target
- sector winding is not derivable from BHSM geometry or field ledger
- a competing non-fitted boundary action yields different admissible modes

## Candidate Verdict

This is a structurally motivated boundary-action candidate, not an official BHSM closure. The P0 blocker remains open until the coframe multiplier and sector winding are derived from the complete boundary action or spectral condition.
