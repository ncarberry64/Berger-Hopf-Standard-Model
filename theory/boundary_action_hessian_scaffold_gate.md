# Boundary Action Hessian Scaffold Gate

## 1. Motivation

The closure-spectrum selection audit supported `(1, 2, 3)` using candidate screens. This gate introduces the next proof scaffold: a boundary action and Hessian projector decomposition whose low-energy sectors match that audited selection rule.

## 2. Previous Gate Achieved: Candidate Closure-Spectrum Selection Audit

```text
d=1 reference/single closure
d=2 orientation-pair closure
d=3 cyclic three-channel closure
d>=4 excess/higher/composite closure sectors
```

## 3. Why Action/Hessian Scaffolding Is Now Required

The selection screens remain diagnostic until they are derived from boundary action terms and the full topographic Hessian.

## 4. Candidate Boundary Action

```text
S_boundary_candidate =
S_phase
+ S_orientation
+ S_cyclic_channel
+ S_topographic
+ S_excess
```

| term | purpose / candidate role | selects | remains unproven |
| --- | --- | --- | --- |
| S_phase | Hopf phase closure / global boundary consistency | Hopf phase closure / global boundary consistency | first-principles derivation from boundary action |
| S_orientation | Z2 upper/lower boundary orientation pair | minimal Z2 upper/lower orientation pair | first-principles derivation from boundary action |
| S_cyclic_channel | minimal cyclic three-channel closure | minimal cyclic three-channel closure | first-principles derivation from boundary action |
| S_topographic | fourth-order topographic branch stability | zero/reference plus two stable nonzero branches from L_T | first-principles derivation from boundary action |
| S_excess | gap penalty for higher/composite closures | gap penalty for sectors outside the low-energy branch budget | first-principles derivation from boundary action |

## 5. Candidate Hessian Projector Decomposition

```text
H_boundary_candidate =
mu_ref P_ref
+ mu_orient P_orient
+ mu_cyclic P_cyclic
+ mu_excess P_excess
```

| projector | closure dimension | interpretation | low-energy selected | eigenvalue | status | finite block |
| --- | --- | --- | --- | --- | --- | --- |
| P_ref | 1 | reference/single closure | true | 0 | reference-normalized | C |
| P_orient | 2 | orientation-pair closure | true | 1 | stable low-energy | M2(C) |
| P_cyclic | 3 | cyclic three-channel closure | true | 1 | stable low-energy | M3(C) |
| P_excess | >=4 | higher/composite/excess closure | false | 10 | gapped/excess | higher/composite |

## 6. Stable Low-Energy Branch Interpretation

```text
mu_ref = 0 or reference-normalized
mu_orient > 0 stable
mu_cyclic > 0 stable
mu_excess >= gap > max(mu_orient, mu_cyclic)
```

The values are schematic diagnostics, not physical predictions.

## 7. Closure Spectrum Bridge

```text
P_ref     -> d=1 reference/single closure
P_orient  -> d=2 orientation-pair closure
P_cyclic  -> d=3 cyclic three-channel closure
P_excess  -> d>=4 higher/composite/unsupported low-energy closures
```

## 8. Bridge To Finite Boundary Algebra

```text
P_ref     -> d=1 -> End(C^1)=C
P_orient  -> d=2 -> End(C^2)=M2(C)
P_cyclic  -> d=3 -> End(C^3)=M3(C)
P_excess  -> d>=4 -> higher/composite/unsupported low-energy closures
```

## 9. Bridge To Projector Eigenvalues `(C,ell,sigma,w)`

The Hessian scaffold preserves the previously audited route from closure dimensions to finite algebra blocks and then to the central projectors and orientation grading.

## 10. Bridge To `(T3,Y,Q)`

Because the finite algebra bridge is preserved, the charge operators from the projector gates remain diagnostic consequences.

## 11. Bridge To Anomaly Closure

The one-generation anomaly closure diagnostic remains preserved through the charge/hypercharge bridge.

## 12. What This Achieves

This gate catalogs candidate action terms and a candidate Hessian projector decomposition for the closure-spectrum selection rule.

Claim labels:

- `BOUNDARY_ACTION_HESSIAN_SCAFFOLD_GATE_CANDIDATE`
- `BOUNDARY_ACTION_TERMS_CATALOGED_CANDIDATE`
- `HESSIAN_PROJECTOR_DECOMPOSITION_CANDIDATE`
- `REFERENCE_ORIENTATION_CYCLIC_PROJECTORS_CANDIDATE`
- `EXCESS_CLOSURE_GAP_CANDIDATE`
- `CLOSURE_SPECTRUM_FROM_HESSIAN_SCAFFOLD_DIAGNOSTIC`
- `FULL_HESSIAN_PROOF_REMAINS_OPEN`
- `FULL_SM_DERIVATION_NOT_CLAIMED`

## 13. What This Does Not Prove

This gate does not fully derive the Standard Model. It introduces a candidate Berger-Hopf boundary action and Hessian scaffold whose low-energy projector structure matches the previously audited closure-spectrum selection rule. The full proof still requires deriving this Hessian from the actual Berger-Hopf boundary action, admissible phase closure, and topographic stability operator.

It does not claim BHSM has replaced the Standard Model. It does not claim the full gauge group is derived. It does not claim the closure spectrum is uniquely derived. It does not claim the full Hessian proof is complete.

## 14. Next Proof Obligations

- derive `S_phase`, `S_orientation`, `S_cyclic_channel`, `S_topographic`, and `S_excess` from the actual boundary action;
- compute the full Berger-Hopf boundary Hessian;
- prove the projector decomposition and gap hierarchy;
- prove or reject exclusion of higher closures from low-energy fundamental sectors.

## Related Theorem Scaffold

See [Theorem-Level Boundary Action Derivation Scaffold](theorem_level_boundary_action_derivation.md) for the explicit axiom and proof-obligation ledger needed to upgrade this Hessian scaffold.
