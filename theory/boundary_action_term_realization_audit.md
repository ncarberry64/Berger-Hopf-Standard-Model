# Boundary Action Term Realization Audit

## Motivation

The previous candidate Hessian gate cataloged boundary action terms but did not realize them as explicit mathematical diagnostics. This audit adds finite candidate functionals for those terms so the closure-spectrum scaffold can be tested more concretely.

## Previous Scaffold Achieved

The previous scaffold used

```text
S_boundary_candidate =
S_phase
+ S_orientation
+ S_cyclic_channel
+ S_topographic
+ S_excess
```

and

```text
H_boundary_candidate =
mu_ref P_ref
+ mu_orient P_orient
+ mu_cyclic P_cyclic
+ mu_excess P_excess
```

to organize the reference, orientation, cyclic, and excess branches.

## Why Action Terms Need Mathematical Realization

Catalog labels alone do not show that the terms can be evaluated, audited, or connected to the closure-spectrum route. The realizations below are diagnostic surrogates, not a first-principles derivation of the complete Berger-Hopf boundary action.

## Phase Closure Functional

```text
S_phase(d, theta) = |exp(i d theta) - 1|^2
```

For the canonical closure phase `theta = 2*pi/d`, this functional vanishes. Off closure, it is positive. It enforces global Hopf phase closure, but it does not alone select `d=1,2,3`.

## Orientation Involution Functional

```text
S_orientation(R) = ||R^2 - I||^2 + lambda_trace |Tr(R)|^2
```

For the finite surrogate `R = diag(+1,-1)`, both the involution and trace-balance conditions pass. This is a candidate `Z_2` orientation grading source and a candidate source for `S_sigma`; it is not a full `SU(2)` derivation.

## Cyclic-Channel Functional

```text
U_3^3 = I
1 + U_3 + U_3^2 = 0 on the nontrivial cyclic subspace
```

The 3-cycle diagnostic supports a minimal nontrivial cyclic channel beyond the `Z_2` orientation pair. This is not a full `SU(3)` derivation.

## Topographic Branch/Excess Functional

```text
L_T = nabla^2 - B*nabla^4
lambda_n(k) = k^2 + B*k^4
S_excess(d) = gamma * max(d - 3, 0)^2
```

The interpretation is one reference branch, two stable nonzero branch candidates, and excess modes gapped under the low-energy diagnostic scaffold. Higher `d` values are not declared impossible.

## Combined Candidate Action

The combined diagnostic uses canonical phase closure for each dimension, activates the orientation diagnostic on `d=2`, activates the cyclic diagnostic on `d=3`, and applies the excess penalty for `d>=4`.

| d | branch | selected low-energy | excess penalty | interpretation |
| --- | --- | --- | --- | --- |
| 1 | reference | true | 0.0 | d>=4 is gapped/excess in this diagnostic scaffold, not impossible |
| 2 | orientation | true | 0.0 | d>=4 is gapped/excess in this diagnostic scaffold, not impossible |
| 3 | cyclic | true | 0.0 | d>=4 is gapped/excess in this diagnostic scaffold, not impossible |
| 4 | excess | false | 1.0 | d>=4 is gapped/excess in this diagnostic scaffold, not impossible |
| 5 | excess | false | 4.0 | d>=4 is gapped/excess in this diagnostic scaffold, not impossible |
| 6 | excess | false | 9.0 | d>=4 is gapped/excess in this diagnostic scaffold, not impossible |
| 7 | excess | false | 16.0 | d>=4 is gapped/excess in this diagnostic scaffold, not impossible |
| 8 | excess | false | 25.0 | d>=4 is gapped/excess in this diagnostic scaffold, not impossible |

## Connection To Hessian Projectors

The realized terms support the same candidate projectors: `P_ref`, `P_orient`, `P_cyclic`, and `P_excess`. The link is diagnostic: it shows compatible finite functionals for the earlier Hessian scaffold but does not derive the Hessian from the complete boundary action.

## Connection To Closure Spectrum `(d=1,2,3)`

The candidate diagnostics select the low-energy dimensions `[1, 2, 3]`: reference, orientation pair, and cyclic channel. The excess term marks `d>=4` as gapped/excess in this scaffold.

## What This Achieves

- Gives explicit candidate functional realizations for the action-term catalog.
- Preserves the previous closure-spectrum and Hessian projector bridges.
- Keeps negative results and uncertainty labels explicit.

## What This Does Not Prove

This audit does not fully derive the Standard Model. It gives candidate mathematical realizations of the boundary action terms used in the Hessian scaffold. These functionals support the previously audited closure-spectrum route diagnostically, but the full Berger-Hopf boundary action and Hessian remain unproved.

It also does not make a replacement claim for BHSM, does not make a full gauge-group derivation claim, and higher `d` values are not declared impossible.

## Next Proof Obligations

- Derive these terms from the full Berger-Hopf boundary action.
- Derive the Hessian projector decomposition from the complete second variation.
- Prove the topographic stability operator and excess gap from the full action rather than a diagnostic surrogate.

## Claim Labels

- BOUNDARY_ACTION_TERM_REALIZATION_AUDIT_COMPLETE
- PHASE_CLOSURE_FUNCTIONAL_CANDIDATE
- ORIENTATION_INVOLUTION_FUNCTIONAL_CANDIDATE
- CYCLIC_CHANNEL_FUNCTIONAL_CANDIDATE
- TOPOGRAPHIC_EXCESS_GAP_FUNCTIONAL_CANDIDATE
- ACTION_TERMS_SUPPORT_CLOSURE_SCAFFOLD_DIAGNOSTIC
- BOUNDARY_ACTION_DERIVATION_REMAINS_OPEN
- FULL_HESSIAN_PROOF_REMAINS_OPEN
- FULL_SM_DERIVATION_NOT_CLAIMED
- FROZEN_PREDICTIONS_UNCHANGED
- OFFICIAL_PREDICTIONS_UNCHANGED
