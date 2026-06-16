# Theorem Discharge: One-Loop RG From Boundary Content

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch attempts to derive the one-loop gauge beta coefficients from already-derived BHSM boundary charge/hypercharge operators, boundary trace normalization, boundary multiplicities, and gauge algebra. Status labels may be promoted only when the derivation is explicit, exact, non-tautological, and does not use a known Standard Model beta-coefficient table as a premise.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the primitive closure spectrum `{1,2,3}`, finite boundary algebra, boundary charge/hypercharge operators, anomaly cancellation as boundary consistency, boundary gauge-algebra skeleton, boundary gauge-action skeleton, and boundary trace normalization with `K1=10/3`, `K2=2`, `K3=2`, and `eta_Y=3/5`.

## 3. Why One-Loop RG Coefficients Are The Next Theorem Blocker

The gauge-action skeleton has trace-normalized generators. The next theorem layer asks whether the one-loop coefficients follow from boundary field content and gauge-algebra data rather than an imported coefficient table.

## 4. Boundary Gauge Algebra And Action Source

Gauge self-interactions use `C2=(0,2,3)` for the Abelian, active-orientation, and cyclic-channel factors.

## 5. Boundary Trace Normalization Source

The prior trace-normalization layer gives one boundary generation matter trace sums:

```text
sum_f T1 = 2
sum_f T2 = 2
sum_f T3 = 2
```

## 6. One-Loop QFT Representation Formula

See [Derived One-Loop RG Formula Boundary](derived_one_loop_rg_formula_boundary.md). The QFT infrastructure formula is:

```text
b_i =
- (11/3) C2(G_i)
+ (2/3) sum_Weyl T_i(R_f)
+ (1/3) sum_complex_scalar T_i(R_s)
```

## 7. Boundary Fermion Trace Sums

See [Derived Boundary Fermion Trace Sums](derived_boundary_fermion_trace_sums.md).

```text
b_f/gen = (2/3)*(2,2,2) = (4/3,4/3,4/3)
N_gen = 3
b_f = (4,4,4)
```

## 8. Three-Generation Boundary Multiplicity

This branch depends on the existing three-generation branch theorem/scaffold result. If that input remains conditional elsewhere, this one-loop theorem layer is conditional on it.

## 9. Gauge Self-Interaction Contributions

```text
b_gauge = (0, -22/3, -11)
```

## 10. Active Scalar Boundary Contribution

See [Derived Boundary Scalar Trace Sums](derived_boundary_scalar_trace_sums.md).

```text
b_scalar = (1/10, 1/6, 0)
```

The active scalar orientation doublet remains a conditional scalar-sector input if not theorem-discharged elsewhere.

## 11. Exact One-Loop Beta Coefficients

See [Derived Boundary Beta Coefficients](derived_boundary_beta_coefficients.md).

```text
b_total =
(0, -22/3, -11)
+ (4, 4, 4)
+ (1/10, 1/6, 0)
= (41/10, -19/6, -7)
```

## 12. Non-Tautology Checks

See [One-Loop RG Non-Tautology Audit](one_loop_rg_non_tautology_audit.md).

## 13. Promoted Results, If Any

- `PO_BH_15_ONE_LOOP_RG_COEFFICIENTS_FROM_BOUNDARY_CONTENT_DERIVED_CONDITIONAL`
- `BOUNDARY_FERMION_TRACE_SUMS_DERIVED_CONDITIONAL`
- `BOUNDARY_SCALAR_TRACE_SUMS_DERIVED_CONDITIONAL`
- `BETA_COEFFICIENTS_41_10_NEG_19_6_NEG_7_DERIVED_CONDITIONAL`

## 14. Remaining Blockers

- measured gauge coupling matching theorem;
- two-loop RG and threshold theorem;
- Higgs/scalar mechanism theorem;
- mass/Yukawa/mixing theorem-level derivation;
- full low-energy Lagrangian theorem;
- full replacement-level derivation.

## 15. Impact On Measured Gauge Matching

This branch derives one-loop coefficients conditionally. It does not predict measured coupling values.

## 16. Impact On Higgs/Scalar Theorem

The scalar contribution uses the active scalar orientation doublet as a conditional scalar-sector input.

## 17. Impact On Mass/Yukawa/Mixing Theorem

No official mass, Yukawa, or mixing output changes.

## 18. What This Achieves

This branch conditionally discharges the one-loop RG theorem layer. Given the previously derived boundary trace normalization, boundary gauge algebra, three-generation branch structure, and active scalar orientation doublet input, the exact one-loop beta coefficients are b1=41/10, b2=-19/6, and b3=-7 under the convention dg_i/dln(mu)=b_i g_i^3/(16 pi^2). The coefficients are derived from BHSM boundary trace sums and gauge self-interaction terms rather than imported from a Standard Model beta-coefficient table.

## 19. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until measured matching, two-loop/threshold RG, Higgs/scalar mechanism, mass/Yukawa/mixing, and full low-energy Lagrangian theorem layers are complete.

## Verdict Labels

- `THEOREM_DISCHARGE_ONE_LOOP_RG_BOUNDARY_CONTENT_COMPLETE`
- `PO_BH_15_ONE_LOOP_RG_COEFFICIENTS_FROM_BOUNDARY_CONTENT_DERIVED_CONDITIONAL`
- `BOUNDARY_FERMION_TRACE_SUMS_DERIVED_CONDITIONAL`
- `BOUNDARY_SCALAR_TRACE_SUMS_DERIVED_CONDITIONAL`
- `BETA_COEFFICIENTS_41_10_NEG_19_6_NEG_7_DERIVED_CONDITIONAL`
- `MEASURED_COUPLINGS_REMAIN_OPEN`
- `TWO_LOOP_RG_REMAINS_OPEN`
- `DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
