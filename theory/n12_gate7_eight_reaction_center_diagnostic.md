# Interval-13 eight-reaction center diagnostic

Base checkpoint: `e0986d0bb8b8c2d4893a23d8a893bc5d8000f7df`, verified on both
local and remote `theory/gate7-66d-reduced-adjoint-integration` branches.
The saved M_13 and its recorded sources pass hash replay. No M_13, Stage-B
derivative, action or Hessian producer was rerun.

**STOP_CENTER_REACTION_REPLAY_FAILED:** the algebraic 8×8 block is invertible,
but its homogeneous shooting-residual slaving proposal does not reproduce the
frozen descriptor row. This is not a validated center slaving milestone or
evidence of physical failure.

## Recovered coordinates

The direct Stage-B archive supplies the node-14 tangent T and action Hessian H.
Use the final frozen R23 interface A and saved child null basis Z, not the earlier
coarse interface. Normalize A by the seven fixed row scales from the final
numerical adjudication to obtain A_n. Reconstruct the historical action-Hessian
right inverse:

```
H_T = T^T H T
L = H_T^-1 A_n^T (A_n H_T^-1 A_n^T)^-1.
```

No Euclidean substitute or positivity assumption is introduced. Channel order
is trace 0/1/2, canonical momentum 0/1, dynamic flux 0/1. Boundary coordinates are
interface variations divided by the frozen row scales. At 512-bit Arb precision,
the child, complement and combined stored-operand frame have certified column
ranks 66, 7 and 73. Frobenius residuals are at most 5.231e-16 for A_n Z and
2.960e-142 for A_n L minus identity. These are stored-algebra certificates, not
new interval authority for the finite-difference interface.

Using the frozen Case-B map X, define trial P=diag(X[Z,L],1) and test P^-T.
The transformed shooting matrix is N=P^-1 M_13 P, partitioned 66+8. Historical
descriptor trial/test scales 1e-7 and 1e6 remain in the original frames; they
are not applied again. The descriptor remains an internal reaction coordinate.

These are explicit **dual coordinates of the shooting residual**. Their last
eight rows have not been identified with the owned boundary/descriptor equations.
The coordinate choice is not claimed as a newly owned physical test frame.

## Results

| Quantity | Result |
| --- | --- |
| M_qq rank | 8 |
| Singular values, diagnostic | 1.009925743, 1.000751629, 1.000271771, 1.000019858, 0.999933874, 0.999283128, 0.997856735, 0.099392615 |
| Condition number | 10.16097366; full M_13: 49.36240341 |
| Determinant | approximately 0.100190035518 |
| Left/right inverse residual upper bounds | 1.135e-16 / 1.118e-16 |
| Arb transform-back residual upper bound | 4.639e-126 |
| Saved binary64 transform-back residual upper bound | 1.429e-12 |
| Trial transformation condition, diagnostic | 2.40208e8 |

Condition numbers depend on the declared channel normalization. Invertibility
uses an inverse residual strictly below one, not a chosen condition-number cutoff.
Exact rational outward bounds are retained in the report.

The candidate Dphi_0=-M_qq^-1 M_qp has shape 8×66 and solves its own equation
to a Frobenius residual at most 1.725e-133. The physical behavior replay fails:

- Normalized boundary discrepancy has operator norm approximately 1.42417e-4,
  whereas A_n Z is approximately zero. This is not asserted to exceed every
  uncertainty in the finite-difference source.
- Expected descriptor proof-row norm: 0.0780685441. Candidate norm:
  0.00181077748. Difference: 0.07882691264, or 7.882691264e-9 physical units.
- Propagated Case-B descriptor allowance: at most 8.916e-7 proof units,
  or 8.916e-14 physical. This uses the saved full causal descriptor graph row,
  node-14 child reprojection error and tangent Gram bound. Arb certifies that
  the stored-row discrepancy exceeds this allowance. It is not a complete
  physical-tube uncertainty certificate.

## Exact missing object and stop boundary

M_13 is a **right-endpoint shooting partial**. The frozen descriptor proposal
comes from a causal/reset-plus-flow family, while the Stage-B child fixes its
interface environment. A dual coordinate partition alone does not turn the last
eight homogeneous shooting equations into these physical constraints.

The next mathematical object is an owner-bound identity relating the seven
boundary residuals and descriptor graph to the selected eight reaction residual
rows, including the left-endpoint/history forcing derivative. For N x=f(p),

```
Dphi_0 = M_qq^-1 (D_p f_q - M_qp).
```

Dropping D_p f_q requires an owned justification. Fitting it to the desired answer
or selecting dual frames until the replay passes would not provide one.
Alternatively, derive the actual eight boundary/descriptor residual rows directly
from retained authority. This missing identity must precede nonlinear slaving.

Per the requested stop rule, no nonlinear K(p), inclusion, curvature, adjoint
support or all-history work followed. Stage B, Case B, gain 0.72221510, descriptor
scales and endpoint ownership remain frozen. `Gate7_closed=False` and
`FULL_BHSM_COMPLETE=False`.

## Reproduction

`artifacts/flagship_integration/gate7_8reaction_center_20260926/` holds the report,
arrays, reproduction receipt and immutable source archive. It includes both
transforms, complement, all four blocks, inverse proposal, candidate Dphi_0 and
replay discrepancies. Arrays are binary64 proposals; the report records Arb checks
against reconstructed frozen algebra. The archived producer is never executed.

Run `scripts/diagnose_n12_gate7_eight_reaction_center.py --out <new-directory>`.
Two fresh processes produced byte-identical reports and arrays. Validation:
`python -m pytest --noconftest tests/test_gate7_eight_reaction_center.py tests/test_gate7_66d_tangent_binding.py -q`.
Result: **12 passed**. The focused suite checks hashes, action-Hessian lifting, transform-back replay,
inverse residuals and the stop on descriptor mismatch. No general audit was run.
