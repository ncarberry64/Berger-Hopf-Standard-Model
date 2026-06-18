# Boundary-State Primitive Derivation Gate

## 1. Motivation

The integer primitive bridge reproduces the Standard Model charge/hypercharge table and the one-generation anomaly cancellation sums diagnostically. This gate asks whether those integer primitives can be organized as outputs of a minimal BHSM-native boundary-state system.

## 2. What Previous Gates Achieved

- The charge/hypercharge bridge maps `(C, ell, sigma, w)` to `T3`, `Y`, and `Q`.
- The anomaly closure gate verifies one-generation anomaly cancellation under left-handed Weyl conventions.

## 3. Why `(C, ell, sigma, w)` Still Need Derivation

The labels remain candidate primitives. They are not yet outputs of the Berger-Hopf boundary action, admissible phase closure, automorphism structure, or topographic stability analysis.

## 4. Candidate Boundary-State System

```text
BoundaryState = (channel_class, closure_class, orientation, interface_activity)
```

```text
channel_class:
  "three_channel_active" -> C=1
  "single_channel_boundary" -> C=0

closure_class:
  "leptonic_closure" -> ell=1
  "hadronic_closure" -> ell=0

orientation:
  "upper" -> sigma=+1
  "lower" -> sigma=-1

interface_activity:
  "active" -> w=1
  "inactive" -> w=0
```

## 5. Boundary-State To Integer-Primitives Map

| state component | candidate BHSM meaning | output primitive | output value | derivation status |
| --- | --- | --- | --- | --- |
| three_channel_active | active three-channel boundary sector | C | 1 | candidate, not derived |
| single_channel_boundary | single boundary channel sector | C | 0 | candidate, not derived |
| leptonic_closure | lepton-sector closure class | ell | 1 | candidate, not derived |
| hadronic_closure | hadron/quark-sector closure class | ell | 0 | candidate, not derived |
| upper | upper weak-interface orientation | sigma | +1 | candidate, not derived |
| lower | lower weak-interface orientation | sigma | -1 | candidate, not derived |
| active | weak-interface active/doublet-like | w | 1 | candidate, not derived |
| inactive | weak-interface inactive/singlet-like | w | 0 | candidate, not derived |

## 6. Boundary-State To Charge/Hypercharge Bridge

```text
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = T3 + Y/2
```

| field | boundary state | C | ell | sigma | w | T3 | Y | Q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nu_L | channel=single_channel_boundary, closure=leptonic_closure, orientation=upper, interface=active | 0 | 1 | 1 | 1 | 1/2 | -1 | 0 |
| e_L | channel=single_channel_boundary, closure=leptonic_closure, orientation=lower, interface=active | 0 | 1 | -1 | 1 | -1/2 | -1 | -1 |
| u_L | channel=three_channel_active, closure=hadronic_closure, orientation=upper, interface=active | 1 | 0 | 1 | 1 | 1/2 | 1/3 | 2/3 |
| d_L | channel=three_channel_active, closure=hadronic_closure, orientation=lower, interface=active | 1 | 0 | -1 | 1 | -1/2 | 1/3 | -1/3 |
| e_R | channel=single_channel_boundary, closure=leptonic_closure, orientation=lower, interface=inactive | 0 | 1 | -1 | 0 | 0 | -2 | -1 |
| u_R | channel=three_channel_active, closure=hadronic_closure, orientation=upper, interface=inactive | 1 | 0 | 1 | 0 | 0 | 4/3 | 2/3 |
| d_R | channel=three_channel_active, closure=hadronic_closure, orientation=lower, interface=inactive | 1 | 0 | -1 | 0 | 0 | -2/3 | -1/3 |
| nu_R | channel=single_channel_boundary, closure=leptonic_closure, orientation=upper, interface=inactive | 0 | 1 | 1 | 0 | 0 | 0 | 0 |

Interface activity `w` changes `T3` and `Y`, but not `Q`, for fixed channel/closure/orientation. This explains why weak doublet/singlet partners can preserve electric charge while changing weak/hypercharge assignments. This is diagnostic, not a full derivation.

## 7. Boundary-State To Anomaly-Closure Bridge

The boundary-state registry maps to the same integer primitive charge table used by the anomaly closure gate. Therefore it confirms the anomaly bridge diagnostically:

```text
SU(3)^2 U(1)_Y = 0
SU(2)^2 U(1)_Y = 0
U(1)_Y^3 = 0
gravity^2 U(1)_Y = 0
Witten SU(2) doublet count = 4, even
```

## 8. What This Achieves

This gate proposes and tests a candidate boundary-state source for `C`, `ell`, `sigma`, and `w`.

Claim labels:

- `BOUNDARY_STATE_PRIMITIVE_DERIVATION_GATE_CANDIDATE`
- `C_ELL_SIGMA_W_FROM_BOUNDARY_STATE_CANDIDATE`
- `BOUNDARY_STATE_TO_SM_CHARGE_BRIDGE_CONFIRMED_DIAGNOSTIC`
- `BOUNDARY_STATE_TO_ANOMALY_CLOSURE_CONFIRMED_DIAGNOSTIC`
- `BOUNDARY_STATE_CLASSES_DERIVATION_REMAINS_OPEN`
- `FULL_SM_DERIVATION_NOT_CLAIMED`

## 9. What This Does Not Prove

This gate does not fully derive the Standard Model. It proposes and tests a candidate boundary-state system whose outputs reproduce the previously audited integer primitive bridge. The remaining proof obligation is to derive the boundary state classes themselves from Berger-Hopf boundary action, admissible phase closure, automorphism structure, and topographic stability.

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived.

## 10. Next Proof Obligations

- Derive `channel_class` from Berger-Hopf channel geometry and automorphism algebra.
- Derive `closure_class` from admissible boundary phase closure.
- Derive `orientation` from boundary orientation/asymmetry.
- Derive `interface_activity` from boundary interface dynamics and explain its relation to SM chiral doublet/singlet structure.
- Derive anomaly cancellation from global boundary closure.

## Related Finite Algebra Gate

- [Boundary projector algebra gate](boundary_projector_algebra_gate.md)
- [Finite boundary algebra source gate](finite_boundary_algebra_source_gate.md)
- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
