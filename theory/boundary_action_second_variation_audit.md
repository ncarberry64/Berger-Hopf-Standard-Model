# Boundary Action Second-Variation Audit

## Motivation

The boundary action term-realization audit supplied finite candidate functionals for the phase, orientation, cyclic-channel, topographic, and excess terms. This audit computes their local quadratic behavior near candidate minima.

## Previous Gate Achieved: Candidate Action Term Realization

The previous gate realized the schematic terms:

```text
S_phase(d, theta)=|exp(i d theta)-1|^2
S_orientation(R)=||R^2-I||^2 + lambda_trace |Tr(R)|^2
S_cyclic_channel: U_3^3=I diagnostic
S_topographic: lambda_n(k)=k^2+B*k^4
S_excess(d)=gamma max(d-3,0)^2
```

## Why Second Variation Is Needed

The Hessian projector scaffold needs local quadratic coefficients, not only finite functional labels. The coefficients here are computed for diagnostic surrogates and are not yet the actual Berger-Hopf Hessian.

## Phase Closure Hessian Coefficient

For `theta = 2*pi/d + epsilon`,

```text
S_phase = 2 - 2 cos(d epsilon)
        = d^2 epsilon^2 + O(epsilon^4)
```

Using `S ~= 1/2 H epsilon^2`, the candidate Hessian coefficient is

```text
H_phase(d)=2d^2
```

This enforces local phase-closure stiffness but does not by itself select the closure spectrum.

## Orientation Involution Hessian Block

For `R = diag(s_i + epsilon_i)` with `s_i^2=1`,

```text
S_orientation_quad ~= 4 sum_i epsilon_i^2 + lambda_trace (sum_i epsilon_i)^2
H_orientation = 8 I + 2 lambda_trace J
```

For `R=diag(+1,-1)`, this is a candidate source of `Z_2` orientation grading, `S_sigma`, `P_orient`, and the `d=2` orientation-pair closure. It is not a full `SU(2)` derivation.

## Cyclic-Channel Hessian Coefficient

For an order-`n` cyclic phase perturbation,

```text
S_cyclic(n, epsilon)=|exp(i n epsilon)-1|^2
S_cyclic ~= n^2 epsilon^2
H_cyclic(n)=2n^2
```

For `n=3`, `H_cyclic(3)=18`. This supports a candidate stable cyclic-channel Hessian coefficient for `P_cyclic`, not a full `SU(3)` derivation.

## Topographic/Excess Hessian Bridge

The topographic diagnostic uses

```text
lambda_n(k)=k^2+B*k^4
```

with `B>0` as the stable convention. The excess term uses

```text
S_excess(d)=gamma max(d-3,0)^2
H_excess = 0 for d <= 3
H_excess = 2 gamma for d > 3
```

Higher closures are gapped/excess under the diagnostic scaffold, not mathematically impossible.

## Candidate Hessian Projector Decomposition

| projector | coefficient / block | interpretation |
| --- | --- | --- |
| `P_ref` | `0` | reference-normalized |
| `P_orient` | `8 I + 2 lambda_trace J` | orientation involution Hessian block |
| `P_cyclic` | `18` | cyclic-channel Hessian coefficient |
| `P_excess` | `2` | excess/gapped Hessian coefficient |

## Closure Spectrum Bridge

| d | H_phase(d) | H_excess(d) | selected low-energy |
| --- | --- | --- | --- |
| 1 | 2 | 0 | true |
| 2 | 8 | 0 | true |
| 3 | 18 | 0 | true |
| 4 | 32 | 2 | false |
| 5 | 50 | 2 | false |
| 6 | 72 | 2 | false |
| 7 | 98 | 2 | false |
| 8 | 128 | 2 | false |

## Finite Algebra Bridge

The selected diagnostic dimensions `[1, 2, 3]` preserve the finite algebra bridge to `C`, `M2(C)`, and `M3(C)`.

## Projector Eigenvalue Bridge

The local second-variation coefficients support the existing `P_ref`, `P_orient`, `P_cyclic`, and `P_excess` decomposition diagnostically.

## Charge/Hypercharge And Anomaly Bridge

Because the finite algebra and projector bridges are preserved, the downstream charge/hypercharge and anomaly bridges remain unchanged. No official or frozen prediction output is recomputed here.

## What This Achieves

The audit supports a candidate route from realized boundary action terms to the Hessian projector scaffold. It does not prove that the actual Berger-Hopf boundary action uniquely produces these projectors.

## What This Does Not Prove

This audit does not fully derive the Standard Model. It computes candidate second-variation behavior of the finite boundary action surrogates and shows that their local quadratic structure supports the previously introduced Hessian projector scaffold. The full Berger-Hopf boundary action and full topographic Hessian remain unproved.

It also makes no replacement claim, no full gauge-group derivation claim, and no exclusion claim for higher closures.

## Next Proof Obligations

- Derive the finite surrogate functionals from the full Berger-Hopf boundary action.
- Derive the second variation from the complete boundary action rather than diagnostic coordinates.
- Prove the full topographic Hessian and projector decomposition.

## Claim Labels

- `BOUNDARY_ACTION_SECOND_VARIATION_AUDIT_COMPLETE`
- `PHASE_CLOSURE_HESSIAN_COEFFICIENT_CANDIDATE`
- `ORIENTATION_INVOLUTION_HESSIAN_BLOCK_CANDIDATE`
- `CYCLIC_CHANNEL_HESSIAN_COEFFICIENT_CANDIDATE`
- `TOPOGRAPHIC_EXCESS_HESSIAN_BRIDGE_CANDIDATE`
- `ACTION_TERMS_TO_HESSIAN_PROJECTORS_DIAGNOSTIC`
- `BOUNDARY_ACTION_DERIVATION_REMAINS_OPEN`
- `FULL_HESSIAN_PROOF_REMAINS_OPEN`
- `FULL_SM_DERIVATION_NOT_CLAIMED`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`

## Related Theorem Scaffold

The next theorem-level layer is [Theorem-Level Boundary Action Derivation Scaffold](theorem_level_boundary_action_derivation.md), which separates axioms, lemmas, theorem statements, proof obligations, and non-tautology checks.
