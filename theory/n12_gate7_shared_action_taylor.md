# Gate-7 common-parameter action residual and triangular transport

Gate 7 remains open. This work evaluates the retained action on the saved
affine solve predictors. It does not identify a predictor with the physical
solution, an adjoint proposal with a certified adjoint, or a residual with a
physical output error.

## Minimal closure graph and unchanged targets

The current numerical obstruction sits on this dependency chain:

1. The original endpoint domain and its actual Hermite--Simpson midpoint,
   together with selected-line, inertia, branch and positive-norm proofs.
2. The action equations, implicit eigenline/response solves and complete
   derivatives on those same parameters.
3. Lifted physical normalization, descriptor contractions, exact midpoint
   relation and complete frozen-output pullback.
4. Uniform physical local errors, their full-history causal transport and
   all required direction/ambient-derivative/rounding remainders.
5. The two-radius inequalities, with all coefficients enclosing the same map:

       B_i(r) = Y_i + sum_j Z_ij r_j + C_i r_L^2
                + 2 M_i r_L r_T + T_i r_T^2 < r_i,
       max_i sum_j (partial_j B_i(r)) r_j/r_i < 1.

6. The physical quotient/operator, signed projected force, KKT root,
   constrained Hessian and continuum obligations retained in the gate ledger.

Items 1 and portions of 4 have substantial reusable certificates. The stored
polynomial inequalities pass for their stated coefficients; the physical
inequalities do not follow while the error flags are open. The next numerical
obstruction is item 2 through item 3, not the already-small normalization rows.
Completing that local obstruction would not by itself establish item 6.

The interval-13 local analysis retains r_L=9.160189721418071e-7 and
r_T=1.9369612593815614e-9 and all 249 midpoint/75 endpoint parameters.
The September 14--15 external handoffs also report a global Hessian budget
1.76875845739832e8 at a different stored witness, approximately
(7.138494894595709e-7, 7.706743304268299e-10). These two witnesses must not be
silently interchanged. The handoff's sufficient missing-coefficient cap
0.14566258071899124 is not an independently certified uniform theorem.

## Action Taylor enclosure

On the original product of scalar intervals, Euclidean balls and box groups,
write each scalar as

    f(theta) in c + a theta + [-r,r].

The same parameter IDs are retained in all state variables and all selected
eigenvector/response predictors. The coefficients use outward Arb arithmetic;
uncertain coefficients are never canceled as exact constants. Linear terms
are combined before their product-domain support is taken. If L(a) bounds
|a theta|, multiplication keeps constant c*d and linear c*b+d*a, and bounds
the discarded part by

    L(a)L(b) + (|c|+L(a))*r_g + (|d|+L(b))*r_f + r_f*r_g.

For a smooth unary function phi on the full input enclosure, keep phi(c) and
phi'(c)*a. Taylor's theorem bounds the remaining part by

    |phi'(c)|*r + sup|phi''|*(L(a)+r)^2/2.

The reciprocal rejects any denominator enclosure containing zero; logarithms
require a strictly positive enclosure. No higher-order derivative is assumed
small. Polynomial degree above one is enclosed explicitly rather than dropped.
The nonlinear support can be conservative; a large remainder is a limitation
of this enclosure until shown otherwise.

The existing action's mixed-derivative algebra is evaluated over this Taylor
algebra. Original quadrature constants, local maps, boundary and global inertia
reciprocal are unchanged. A temporary scalar adapter is always restored, even
after failure. Constant output legs are contracted inside the action before
taking a scalar support. This avoids reconstructing dense action tensors.

## Actual coupled rows and covector scope

The saved seven solves supply p, h, p_u, h_u and their shared-parameter affine
predictors. Border variables are retained too. The chosen eigenvalue predictor
uses the original saved constant and the signed affine Rayleigh coefficients;
it is an arbitrary predictor, not an inclusion of the true eigenvalue.

With A=H-lambda I and lambda_u=p^T H_u p, the four blocks evaluated are

    (A p,                         (p^T p-1)/2),
    (A h+b p-f,                   p^T h),
    (A p_u+gamma_u p+H_u p-lambda_u p, p^T p_u),
    (A h_u+b_u p+H_u h-lambda_u h+b p_u-f_u,
                                  p^T h_u+p_u^T h).

The implementation evaluates a fixed covector contraction of each complete
block, including its bottom row. The covector is a proposal informed by the
original node-14 row 73 of QP and the last response solve. Its construction
retains the physical rate-normalization sensitivity and a selected-line
approximation for the descriptor sensitivity. That approximation selects an
arbitrary exact covector only: it is not asserted as an identity for the
true output adjoint. The response border uses +p; the saved eigenline inverse
uses -p, so the last solution coordinate is flipped in the proposal.

All action terms H, H_u, f and f_u in these contracted residuals are evaluated
from the unchanged action on the common predictor. They are not recovered by
relabeling the old independent residual balls. The full stacked adjoint,
descriptor/output remainder, correction inclusion and exact endpoint-to-
midpoint shared relation remain required before these scalar supports can be
interpreted as a physical column-error bound. In particular, the old local
vector remainder allowance 0.9997125743857969 is not a threshold for any one
of these residual blocks.

## Acyclic implicit transport

For a complete common-parameter secant system ordered by dependency,

    e_i = r_i(theta) + E_ii(theta)e_i + sum_{j<i} E_ij(theta)e_j,

let q_i bound the weighted norm of E_ii, with q_i<1. Large off-diagonal
couplings are permitted. Build polynomial models X_i with a finite Neumann
expansion, retaining theta. Form the complete model defect before bounding:

    d_i = r_i + E_ii X_i + sum_{j<i} E_ij X_j - X_i.

If eta_i bounds ||d_i|| and l_ij bounds ||E_ij|| between the stated block
norms, then

    rho_i = (eta_i + sum_{j<i} l_ij rho_j)/(1-q_i)

bounds ||e_i-X_i|| by induction. For output C, combine sum C_i X_i as a
shared polynomial before taking supports, and add sum ||C_i||rho_i.
The proof follows by moving q_i||e_i-X_i|| to the left in each block.

This theorem removes any need for an unweighted contraction of the entire
feedforward stack. It does not waive diagonal contraction, off-diagonal
amplification, the full secant equations or invariant correction domains.
The implementation rejects graph cycles; genuine feedback requires a block
containing that cycle or a different inclusion argument. The analytic test
e_1=theta, e_2=2e_1-2theta proves zero output despite raw stack norm 2.

## Reproduction and source ownership

The first complete paired scalar-action evaluation gives these outward
supports (approximate display only; exact rationals are in the artifacts):

| Contracted block | Midpoint, 249 parameters | Endpoint, 75 parameters |
|---|---:|---:|
| Eigenline, including normalization | 1.5465867392214272e-18 | 1.1556746320145132e-19 |
| Response, including normalization | 8.565114556801745e-13 | 1.5242590426668365e-14 |
| Axis line, including normalization | 1.6215490906152406e-15 | 2.6854414051072794e-16 |
| Axis response, including normalization | 1.455814275442676e-10 | 7.014322817976109e-12 |

The axis-response Taylor remainder dominates these particular contractions.
All terms and the original parameter groups are retained. Independent fresh
processes produced byte-identical midpoint and endpoint records. These values
remain covector-contracted equation residuals, not physical error margins.

The current artifact names are
`BHSM_N12_GATE7_SHARED_ACTION_RESIDUAL_MIDPOINT_V2_20260919.json`,
`BHSM_N12_GATE7_SHARED_ACTION_RESIDUAL_ENDPOINT_V2_20260919.json`, and
`BHSM_N12_GATE7_SHARED_ACTION_ADJOINT_REPRODUCTION_V2_20260919.json`
under `artifacts/flagship_integration/`.
The V1 records and implementation commit `ca2b0284` remain historical
predictor probes. V1 took midpoints of the state-direction coefficients;
V2 retains their nonzero rounding radii (up to about 1e-160). V1 therefore
does not establish the full original state-domain coverage claimed in its
metadata. V2 supersedes that coverage claim and independently reproduces;
the displayed support values are unchanged. No V1 gate promotion occurred.

From the repository root, use a fresh output path:

```powershell
C:/Python314/python.exe scripts/evaluate_n12_gate7_shared_action_residual.py --evidence-root ../BHSM-ae32-crossing-correction --family midpoint --out tmp/gate7_action/midpoint.json
C:/Python314/python.exe -m pytest -q tests/test_shared_action_taylor.py tests/test_shared_triangular_residual.py tests/test_shared_parameter_residual.py tests/test_joint_input_column.py
```

Each action contraction has a source-bound checkpoint. No action derivative
campaign or existing evidence file is overwritten. Source changes reject reuse.
Fresh output directories provide independent arithmetic reproduction; replay
of a checkpoint alone is not independent recomputation. Saved-data provenance
and the original scientific claim boundaries remain prerequisites.
