# Boundary Integer Anomaly Closure Gate

## 1. Motivation

The boundary integer charge/hypercharge bridge reproduces the one-generation Standard Model charge table diagnostically. This gate asks whether that same integer-primitive table also passes one-generation anomaly cancellation under the standard left-handed Weyl convention.

## 2. Why Anomaly Cancellation Matters For SM Derivation

Anomaly cancellation is a required consistency condition for the Standard Model gauge representation ledger. Any BHSM replacement-by-derivation program must eventually derive anomaly cancellation from Berger-Hopf boundary closure, rather than importing it as a Standard Model fact.

## 3. Integer Primitive Charge Bridge Recap

```text
C in {0,1}
ell in {0,1}
sigma in {-1,+1}
w in {0,1}

T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = T3 + Y/2
Q = sigma/2 + C/6 - ell/2
```

## 4. Left-Handed Weyl Convention

Right-handed physical fermions are represented by left-handed charge-conjugate fields in anomaly sums:

```text
u_R physical -> u_R^c left-handed conjugate with Y = -4/3, Q = -2/3
d_R physical -> d_R^c left-handed conjugate with Y = +2/3, Q = +1/3
e_R physical -> e_R^c left-handed conjugate with Y = +2, Q = +1
nu_R optional -> nu_R^c left-handed conjugate with Y = 0, Q = 0
```

The hypercharge convention remains:

```text
Q = T3 + Y/2
```

## 5. One-Generation Anomaly Sums

| field | color multiplicity | weak multiplicity | Y | color charged | weak doublet |
| --- | --- | --- | --- | --- | --- |
| Q_L | 3 | 2 | 1/3 | True | True |
| L_L | 1 | 2 | -1 | False | True |
| u_R_c | 3 | 1 | -4/3 | True | False |
| d_R_c | 3 | 1 | 2/3 | True | False |
| e_R_c | 1 | 1 | 2 | False | False |
| nu_R_c | 1 | 1 | 0 | False | False |

```text
SU(3)^2 U(1):
2*(1/3) + (-4/3) + (2/3) = 0

SU(2)^2 U(1):
3*(1/3) + (-1) = 0

U(1)^3:
6*(1/3)^3 + 3*(-4/3)^3 + 3*(2/3)^3 + 2*(-1)^3 + (2)^3 + 0^3 = 0

gravity^2 U(1):
6*(1/3) + 3*(-4/3) + 3*(2/3) + 2*(-1) + 2 + 0 = 0
```

## 6. Witten SU(2) Parity Check

```text
N_doublets = 3 quark doublets + 1 lepton doublet = 4
4 is even, so the one-generation SU(2) global anomaly parity check passes.
```

## 7. Interpretation As Candidate Boundary Closure

This anomaly-closure gate tests whether the integer primitive charge/hypercharge bridge reproduces Standard Model one-generation anomaly cancellation. It does not derive the integer primitives from Berger-Hopf boundary geometry and does not prove that BHSM has derived or replaced the Standard Model.

Claim labels:

- `BOUNDARY_INTEGER_ANOMALY_CLOSURE_GATE_CANDIDATE`
- `SM_ONE_GENERATION_ANOMALY_CANCELLATION_REPRODUCED_DIAGNOSTIC`
- `ANOMALY_CANCELLATION_AS_BOUNDARY_CLOSURE_CANDIDATE`
- `WITTEN_SU2_PARITY_CHECK_PASSED_DIAGNOSTIC`
- `PRIMITIVE_DERIVATION_REMAINS_OPEN`
- `FULL_SM_DERIVATION_NOT_CLAIMED`

## 8. What This Does Not Prove

- It does not derive `C`, `ell`, `sigma`, or `w` from Berger-Hopf boundary geometry.
- It does not derive anomaly cancellation from first-principles boundary closure.
- It does not claim the Standard Model is derived.
- It does not claim BHSM has replaced the Standard Model.
- It does not claim the full gauge group is derived.

## 9. Next Proof Obligations

- Derive the integer primitives from Berger-Hopf boundary geometry.
- Derive anomaly cancellation as global boundary closure consistency.
- Derive the local gauge group and field content rather than preserving them as infrared inputs.
- Keep collective-curvature/dark-matter interpretation separate from this particle-sector proof.

## Related Finite Algebra Gate

- [Boundary projector algebra gate](boundary_projector_algebra_gate.md)
- [Finite boundary algebra source gate](finite_boundary_algebra_source_gate.md)
