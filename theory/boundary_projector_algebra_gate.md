# Boundary Projector Algebra Gate

## 1. Motivation

The previous boundary-state gate defined named state classes whose outputs reproduce the integer primitive bridge. This gate replaces those named classes with candidate commuting boundary projectors and an orientation involution.

## 2. Previous Gates Achieved

```text
C, ell, sigma, w
-> T3, Y, Q
-> SM charge/hypercharge table
-> one-generation anomaly closure
```

## 3. Why Boundary-State Classes Still Need Derivation

The boundary-state class names are still candidate inputs. A replacement-by-derivation program needs operators whose joint eigenvalues produce those labels.

## 4. Candidate Boundary-Projector Algebra

```text
P_C      color/channel projector
P_ell    lepton-closure projector
S_sigma  weak-interface orientation involution
P_w      weak-interface activity projector
```

```text
P_C |psi> = C |psi>,          C in {0,1}
P_ell |psi> = ell |psi>,      ell in {0,1}
S_sigma |psi> = sigma |psi>,  sigma in {-1,+1}
P_w |psi> = w |psi>,          w in {0,1}
```

Candidate algebra constraints:

```text
P_C^2 = P_C
P_ell^2 = P_ell
P_w^2 = P_w
S_sigma^2 = I
[P_C, P_ell] = [P_C, P_w] = [P_C, S_sigma] = [P_ell, P_w] = [P_ell, S_sigma] = [P_w, S_sigma] = 0
```

## 5. Joint Eigenvalue Interpretation

```text
C=1 -> three-channel active sector
C=0 -> single-channel boundary sector
ell=1 -> lepton-closure sector
ell=0 -> hadron/quark-closure sector
sigma=+1 -> upper weak-interface orientation
sigma=-1 -> lower weak-interface orientation
w=1 -> weak-interface active / doublet-like
w=0 -> weak-interface inactive / singlet-like
```

## 6. Closure Constraint

```text
P_C + P_ell = I
C + ell = 1
```

For minimal fermion boundary sectors, the color/channel and lepton-closure projectors are complementary.

## 7. Channel Multiplicity Rule

```text
d_channel = 1 + 2C
C=0 -> d_channel=1
C=1 -> d_channel=3
```

This is a candidate bridge toward color triplicity, not a full SU(3) derivation.

## 8. Bridge To `(T3,Y,Q)`

```text
T3 = w*sigma/2
Y = C/3 - ell + (1-w)*sigma
Q = sigma/2 + C/6 - ell/2
```

| field | C | ell | sigma | w | T3 | Y | Q | d_channel |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nu_L | 0 | 1 | 1 | 1 | 1/2 | -1 | 0 | 1 |
| e_L | 0 | 1 | -1 | 1 | -1/2 | -1 | -1 | 1 |
| u_L | 1 | 0 | 1 | 1 | 1/2 | 1/3 | 2/3 | 3 |
| d_L | 1 | 0 | -1 | 1 | -1/2 | 1/3 | -1/3 | 3 |
| e_R | 0 | 1 | -1 | 0 | 0 | -2 | -1 | 1 |
| u_R | 1 | 0 | 1 | 0 | 0 | 4/3 | 2/3 | 3 |
| d_R | 1 | 0 | -1 | 0 | 0 | -2/3 | -1/3 | 3 |
| nu_R | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |

## 9. Bridge To Anomaly Closure

The physical projector-state registry reproduces the same charge table used by the one-generation anomaly closure gate. The anomaly closure bridge remains diagnostic.

## 10. What This Achieves

This gate makes `(C, ell, sigma, w)` candidate joint eigenvalues of a boundary-projector algebra.

Claim labels:

- `BOUNDARY_PROJECTOR_ALGEBRA_GATE_CANDIDATE`
- `C_ELL_SIGMA_W_AS_PROJECTOR_EIGENVALUES_CANDIDATE`
- `FERMION_CLOSURE_COMPLEMENTARITY_CANDIDATE`
- `CHANNEL_MULTIPLICITY_RULE_CANDIDATE`
- `PROJECTOR_TO_SM_CHARGE_BRIDGE_CONFIRMED_DIAGNOSTIC`
- `PROJECTOR_TO_ANOMALY_CLOSURE_CONFIRMED_DIAGNOSTIC`
- `PROJECTOR_ALGEBRA_DERIVATION_REMAINS_OPEN`
- `FULL_SM_DERIVATION_NOT_CLAIMED`

## 11. What This Does Not Prove

This gate does not fully derive the Standard Model. It replaces named boundary-state classes with a candidate boundary-projector algebra whose joint eigenvalues reproduce the previously audited \(C,\ell,\sigma,w\) primitive bridge. The remaining proof obligation is to derive the projector algebra itself from Berger-Hopf boundary action, automorphism structure, admissible phase closure, and topographic stability.

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived.

## 12. Next Proof Obligations

- Derive `P_C` from admissible three-channel boundary automorphisms.
- Derive `P_ell` from complementary closure condition.
- Derive `S_sigma` from interface orientation.
- Derive `P_w` from weak-interface activity.
- Derive local SU(3), SU(2), and U(1) algebras from projector/automorphism structure.

## Related Finite Algebra Gate

- [Finite boundary algebra source gate](finite_boundary_algebra_source_gate.md)
