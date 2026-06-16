# Theorem Discharge: Boundary Trace Normalization

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch attempts to derive the boundary trace-normalization factor from the already-derived boundary charge/hypercharge operators, boundary multiplicities, and finite-algebra trace weights, rather than importing Standard Model or GUT normalization as an assumption. Status labels may be promoted only when the derivation is explicit, exact, non-tautological, and does not use known Standard Model normalization as a premise.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the primitive closure spectrum `{1,2,3}`, finite boundary algebra, boundary charge/hypercharge operators, anomaly cancellation as boundary consistency, boundary gauge-algebra skeleton, and boundary gauge-action skeleton.

## 3. Why Trace Normalization Is The Next Theorem Blocker

The gauge-action skeleton needs a trace normalization showing how the residual Abelian boundary phase is placed on the same finite-algebra trace footing as the active-orientation and cyclic-channel curvature blocks.

## 4. Boundary Charge/Hypercharge Table Source

The starting operators are:

```text
Q_boundary = 1/2(S_sigma-I)+2/3 P_C
T3_boundary = 1/2 P_w S_sigma
Y_boundary = 2(Q_boundary-T3_boundary)
```

The eigenvalue forms are:

```text
Q(C,sigma) = (sigma-1)/2 + (2/3)C
T3(C,sigma,w) = w sigma / 2
Y(C,sigma,w) = (4/3)C - 1 + (1-w)sigma
```

## 5. Single Left-Oriented Boundary Trace Basis

This branch uses the single left-oriented boundary basis from the anomaly-consistency layer. Active rows use `w=1`; inactive rows are counted through their conjugate inactive basis.

## 6. Active Boundary Sector

```text
w=1
Y_active(0)=-1
Y_active(1)=1/3
N(C)=1+2C
```

The active sector has two orientation components.

## 7. Conjugate Inactive Boundary Sector

```text
Y_conjugate = -Y_inactive
Y^c in {0, 2, -4/3, 2/3}
```

The channel multiplicities are `1,1,3,3`.

## 8. Abelian Trace Weight (K_1)

Using the physical boundary charge convention `Q=T3+Y/2`, the Abelian trace generator is `T_Y=Y/2`.

```text
K1 =
2*1*(-1/2)^2
+ 2*3*(1/6)^2
+ 1*(0)^2
+ 1*(1)^2
+ 3*(-2/3)^2
+ 3*(1/3)^2
= 10/3
```

## 9. Active-Orientation Trace Weight (K_2)

```text
K2 = (1+3)*(1/2) = 2
```

## 10. Cyclic-Channel Trace Weight (K_3)

```text
K3 = 4*(1/2) = 2
```

## 11. Hypercharge Normalization Factor (eta_Y=3/5)

```text
eta_Y = K2/K1 = 2/(10/3) = 3/5
eta_Y*K1 = 2 = K2 = K3
```

## 12. Normalized Gauge-Action Skeleton

```text
S_gauge_boundary_norm =
k [
  Tr_cyc(F_cyc wedge *F_cyc)
  + Tr_orient(F_orient wedge *F_orient)
  + eta_Y F_Y wedge *F_Y
]
```

## 13. Coupling-Convention Consequence

If a later convention writes the physical hypercharge coupling against `Y/2`, while the normalized gauge coupling is written against `sqrt(eta_Y)Y/2`, then:

```text
g1^2 = (5/3) gY^2
alpha1 = (5/3) alphaY
```

This is a convention consequence of the trace normalization. It is not an RG-running derivation or a measured-coupling prediction.

## 14. Non-Tautology Checks

See [Trace Normalization Non-Tautology Audit](trace_normalization_non_tautology_audit.md).

## 15. Promoted Results, If Any

- `PO_BH_14_BOUNDARY_TRACE_NORMALIZATION_DERIVED_CONDITIONAL`
- `BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL`
- `BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL`
- `NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL`

## 16. Remaining Blockers

- RG running theorem;
- measured gauge coupling theorem;
- Higgs/scalar mechanism theorem;
- mass/Yukawa/mixing theorem-level derivation;
- full low-energy Lagrangian theorem;
- full replacement-level derivation.

## 17. Impact On Coupling/RG Theorem

This branch derives a boundary trace-normalization factor and a coupling-convention relation. It does not derive RG running or measured coupling values.

Follow-up theorem layer: [Theorem discharge: one-loop RG from boundary content](theorem_discharge_one_loop_rg_boundary_content.md) conditionally derives `b1=41/10`, `b2=-19/6`, and `b3=-7` from boundary trace sums, gauge self-interactions, and the active scalar boundary input.

## 18. Impact On Higgs/Scalar Theorem

No Higgs/scalar theorem is discharged here.

## 19. Impact On Mass/Yukawa/Mixing Theorem

No mass, Yukawa, or mixing output changes. No official prediction changes.

## 20. What This Achieves

This branch conditionally discharges the boundary trace-normalization theorem layer. Given the previously derived boundary charge/hypercharge operators and the single left-oriented boundary trace basis, the raw Abelian trace weight is K1=10/3 while the active-orientation and cyclic-channel trace weights are K2=2 and K3=2. Therefore the boundary hypercharge normalization factor is eta_Y=3/5, placing all three gauge-action trace weights on the same normalized footing. The result is derived from boundary multiplicities and trace weights rather than imported from Standard Model normalization.

## 21. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until RG running, measured coupling matching, Higgs/scalar mechanism, mass/Yukawa/mixing, and full low-energy Lagrangian theorem layers are complete.

## Trace Result Table

| name | value | status | interpretation |
| --- | --- | --- | --- |
| `K1_hypercharge_raw` | `10/3` | `BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL` | raw Abelian residual trace weight from boundary rows |
| `K2_orientation` | `2` | `BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL` | active-orientation finite-algebra trace weight |
| `K3_cyclic` | `2` | `BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL` | cyclic-channel finite-algebra trace weight |
| `eta_Y` | `3/5` | `BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL` | factor placing Abelian trace weight on the non-Abelian footing |
| `K1_hypercharge_normalized` | `2` | `NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL` | normalized Abelian trace weight |

## Verdict Labels

- `THEOREM_DISCHARGE_BOUNDARY_TRACE_NORMALIZATION_COMPLETE`
- `PO_BH_14_BOUNDARY_TRACE_NORMALIZATION_DERIVED_CONDITIONAL`
- `BOUNDARY_TRACE_WEIGHTS_DERIVED_CONDITIONAL`
- `BOUNDARY_HYPERCHARGE_NORMALIZATION_DERIVED_CONDITIONAL`
- `NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL`
- `HYPERCHARGE_TRACE_FACTOR_3_5_DERIVED_CONDITIONAL`
- `GAUGE_COUPLING_CONVENTION_5_3_DERIVED_CONDITIONAL`
- `RG_RUNNING_REMAINS_OPEN`
- `MEASURED_COUPLINGS_REMAIN_OPEN`
- `DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
