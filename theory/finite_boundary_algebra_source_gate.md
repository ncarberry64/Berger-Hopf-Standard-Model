# Finite Boundary Algebra Source Gate

## 1. Motivation

The previous projector gate made the integer primitives `(C, ell, sigma, w)` joint eigenvalues of a candidate boundary-projector algebra. This gate asks what finite boundary algebra could source those projectors.

## 2. Previous Gate Achieved: Projector Eigenvalue Diagnostics

```text
P_C |psi> = C |psi>
P_ell |psi> = ell |psi>
S_sigma |psi> = sigma |psi>
P_w |psi> = w |psi>
```

with diagnostic bridges:

```text
C + ell = 1
d_channel = 1 + 2C
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = sigma/2 + C/6 - ell/2
```

## 3. Why Projectors Need A Source

The projector eigenvalues remain declared until a boundary algebra, action, or spectral construction forces the central projections and orientation grading. This gate formalizes a candidate finite algebra source layer.

## 4. Candidate Finite Boundary Algebra

```text
A_boundary_candidate = A_channel tensor A_weak
```

## 5. Channel Algebra `(C_ell direct_sum M_3(C)_C)`

```text
A_channel = C_ell direct_sum M_3(C)_C
```

- `C_ell`: single-channel leptonic closure block.
- `M_3(C)_C`: three-channel active boundary block and candidate source of color triplicity.

## 6. Weak-Interface Algebra `(M_2(C)_{w=1} direct_sum C_+ direct_sum C_-)`

```text
A_weak = M_2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}
```

- `M_2(C)_{w=1}`: weak-interface active two-state block.
- `C_{sigma=+}` and `C_{sigma=-}`: weak-interface inactive singlet blocks with retained orientation labels.

## 7. Projectors And Orientation Grading

```text
P_C = central projection onto M_3(C)_C
P_ell = central projection onto C_ell
P_w = central projection onto M_2(C)_{w=1}
S_sigma = orientation grading with eigenvalues +1 and -1
```

Candidate closure:

```text
P_C + P_ell = I_channel
C + ell = 1
d_channel = 1 + 2C
```

## 8. Charge Operators

```text
P_ell = I - P_C
T3_hat = (1/2) P_w S_sigma
Y_hat = (4/3) P_C - I + (I - P_w) S_sigma
Q_hat = T3_hat + Y_hat/2
```

## 9. Electric-Charge Simplification

```text
Q_hat
= (1/2)P_w S_sigma
  + (1/2)[(4/3)P_C - I + (I-P_w)S_sigma]
= (2/3)P_C - (1/2)I + (1/2)S_sigma
= (1/2)(S_sigma - I) + (2/3)P_C
```

Electric charge depends only on the channel projector `P_C` and the orientation grading `S_sigma`. Weak-interface activity `P_w` redistributes charge between `T3` and `Y`, but cancels out of `Q`.

| state | C | sigma | Q |
| --- | --- | --- | --- |
| lepton upper | 0 | +1 | 0 |
| lepton lower | 0 | -1 | -1 |
| quark upper | 1 | +1 | 2/3 |
| quark lower | 1 | -1 | -1/3 |

Full diagnostic registry:

| state | channel block | weak block | orientation | C | ell | w | sigma | T3 | Y | Q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nu_L | C_ell | M2_active | upper | 0 | 1 | 1 | 1 | 1/2 | -1 | 0 |
| e_L | C_ell | M2_active | lower | 0 | 1 | 1 | -1 | -1/2 | -1 | -1 |
| u_L | M3_C | M2_active | upper | 1 | 0 | 1 | 1 | 1/2 | 1/3 | 2/3 |
| d_L | M3_C | M2_active | lower | 1 | 0 | 1 | -1 | -1/2 | 1/3 | -1/3 |
| e_R | C_ell | C_sigma_minus |  | 0 | 1 | 0 | -1 | 0 | -2 | -1 |
| u_R | M3_C | C_sigma_plus |  | 1 | 0 | 0 | 1 | 0 | 4/3 | 2/3 |
| d_R | M3_C | C_sigma_minus |  | 1 | 0 | 0 | -1 | 0 | -2/3 | -1/3 |
| nu_R | C_ell | C_sigma_plus |  | 0 | 1 | 0 | 1 | 0 | 0 | 0 |

## 10. Bridge To Anomaly Closure

The finite boundary algebra registry reproduces the projector eigenvalue bridge, the charge/hypercharge bridge, and the same one-generation anomaly closure diagnostics used by the prior gates.

## 11. What This Achieves

This gate supplies a candidate finite algebraic source for the previously audited boundary-projector eigenvalue system.

Claim labels:

- `FINITE_BOUNDARY_ALGEBRA_SOURCE_GATE_CANDIDATE`
- `PROJECTORS_AS_FINITE_ALGEBRA_CENTRAL_PROJECTIONS_CANDIDATE`
- `ORIENTATION_GRADING_SOURCE_FOR_SIGMA_CANDIDATE`
- `CHANNEL_BLOCK_SOURCE_FOR_COLOR_TRIPLICITY_CANDIDATE`
- `WEAK_INTERFACE_BLOCK_SOURCE_FOR_W_CANDIDATE`
- `CHARGE_OPERATOR_SIMPLIFICATION_CONFIRMED_DIAGNOSTIC`
- `FINITE_ALGEBRA_DERIVATION_REMAINS_OPEN`
- `FULL_SM_DERIVATION_NOT_CLAIMED`

## 12. What This Does Not Prove

This gate does not fully derive the Standard Model. It proposes a candidate finite Berger-Hopf boundary algebra whose central projections and orientation grading reproduce the previously audited projector eigenvalue system. The remaining proof obligation is to derive this finite algebra from Berger-Hopf boundary action, admissible phase closure, automorphism structure, and topographic stability.

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived. It does not introduce a new official mass formula or change frozen predictions.

## 13. Next Proof Obligations

- Derive `C_ell direct_sum M_3(C)_C` from Berger-Hopf boundary action and admissible phase closure.
- Derive `M_2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}` from boundary interface dynamics.
- Derive `S_sigma` as a geometric orientation grading.
- Derive the local gauge algebras from the finite boundary algebra and automorphism structure.
- Prove topographic stability selects this finite algebra rather than nearby alternatives.

## Related Automorphism Closure Gate

- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
- [Closure spectrum selection rule audit](closure_spectrum_selection_rule_audit.md)
- [Boundary action Hessian scaffold gate](boundary_action_hessian_scaffold_gate.md)
