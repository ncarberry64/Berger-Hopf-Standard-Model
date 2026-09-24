# Residual cancellation before the physical scalar output bound

This is a single fixed-direction, fixed-output-row calculation on the original
interval-13 midpoint family. It is not a Gate-7 closure certificate, a complete
right-column bound, or a bound on the full-history operator.

## Exact target

Keep the original midpoint direction w0, interval step dt, frozen output map
P and stored projector Q=I-aa^T. Exact unit length of a is not assumed. Define

    z^T = row_73[(2 dt/3) Q P],
    Y(theta) = z^T DF(Z_M(theta)) w0.

The target here is a uniform enclosure of Y-Y0, where Y0 is the original
verified point derivative contracted with the same z. The midpoint outer
family has all original 249 parameters, including the endpoint-field remainder.
Proving this enclosure can remove a scalar midpoint obstruction. It does not
certify the 74-component Euclidean norm or the complete endpoint chain.

## Complete coupled unknowns and inherited inclusion

Use U=(p,lambda,h,b,p_u,gamma_u,h_u,b_u), with four blocks of 62 unknowns.
The unchanged equations G(theta,U)=0 are the four coupled action/normalization
blocks in `n12_gate7_shared_action_taylor.md`. The saved oriented eigenpair box
and three uniform solve boxes enclose this same physical graph. Their source
bindings, independent physical reproductions and full-graph flags are checked.

For the saved affine predictor Uhat_i(theta), choose the explicit radius

    rho_i >= sup_{u_i in [U_i]} |u_i-Uhat_i(0)|
             + support(Uhat_i(theta)-Uhat_i(0)).

Thus every true solution can be written

    U(theta)=Uhat(theta)+diag(rho)*eta,   |eta_i|<=1.

The calculation uses the original 249 parameters plus all 248 correction
coordinates. It preserves the shared parameters through every action
contraction and physical-output operation. The independent correction box is
used only after the complete output-minus-residual expression is formed; it
does not replace the original parameter graph or assert that all corrections
are physically attainable. No original physical radius is reduced.

The saved state-direction coefficients have small but nonzero rounding radii.
They are retained as Arb coefficient balls. Taking their midpoints is valid
for an arbitrary predictor probe, but cannot establish coverage of the entire
original physical state domain. The V1 action probes are superseded for this
coverage claim by the V2 evaluator with full direction-coefficient balls.

## Full output and descriptor contractions

Let W denote the reduced metric weights, D=diag(W/w_reduced), q the original
weighted configuration and u the raw input direction. Extend reduced vectors
by zero in the configuration slots; set a=Dp, d=(q/w_q,Dh), a_u=Dp_u and
d_u=(q_u/w_q,Dh_u). For the retained action S,

    c = D3S[p,p,a],
    R = D3S[p,p,d],
    c_u = D4S[p,p,a,u] + 2 D3S[p,p_u,a] + D3S[p,p,a_u],
    R_u = D4S[p,p,d,u] + 2 D3S[p,p_u,d] + D3S[p,p,d_u].

These are the original third/fourth descriptor contractions, not second/third
derivatives. Both occurrences of p and all metric factors are retained. Then

    N=(s q,W(b p+s h)),        delta=b c+s R,
    N_u=(s_u q+s q_u,W(b_u p+b p_u+s_u h+s h_u)),
    delta_u=b_u c+b c_u+s_u R+s R_u,
    n=sqrt(N^T N),
    F_u=(N_u,delta_u)/n - (N,delta)*(N^T N_u)/n^3.

The Taylor evaluator requires positivity of the entire norm enclosure before
using its reciprocal. All action contractions include the original boundary
and global inertia reciprocal. No stored independent residual ball is relabeled
as a shared-parameter coefficient.

## Anchor adjoint

At the saved predictor anchor, compute J=D_U G and l=D_U(z^T F_u). The reduced
Hessian is recovered from the already certified inverse defect D0=I-R0 J0,
rather than recomputed. Only the needed third/fourth action contractions are
evaluated. Formal first jets differentiate the full readout, including the
descriptor contractions and physical norm.

Solve beta J=l in outward Arb arithmetic and choose the exact midpoint beta.
Retain and report l-beta J; do not assume it vanishes. The midpoint run's
weighted anchor defect is approximately 2.1396726231505813e-136 and reproduces
byte-for-byte. This tiny anchor defect does not establish a uniform adjoint.

## Uniform residual identity

For any fixed beta, define

    V(theta,eta)=Y(theta,Uhat(theta)+diag(rho)eta)
                - beta G(theta,Uhat(theta)+diag(rho)eta).

On the inherited true graph, G=0, so V=Y exactly. Consequently a Taylor
enclosure of V-Y0 over the stated product domain bounds the actual physical
scalar Y-Y0. This conclusion does not require beta to be an exact adjoint.
The anchor adjoint only makes the linear correction coefficients small.

All 248 correction coefficients and the full nonlinear Taylor remainder are
retained. The code reports their supports separately. A large remainder is
an enclosure obstruction; it is not a physical instability. A small anchor
defect alone cannot be used in place of this uniform remainder.

## Reproduction

The September 19 calculation gives the following outward decimal upper
bounds (the artifact stores the tighter exact rational endpoints):

    |Y(theta)-Y0| <= 0.341177266859,
    |Y(theta)|    <= 0.384496713820.

The deviation consists of signed linear support at most
0.000022921929173 and a nonlinear remainder at most 0.341154344930,
plus anchor constant uncertainty below 1.645e-100. The support from the
248 linear correction coordinates is below 4.666e-138. This last value
checks the complete anchor cancellation; the nonlinear remainder is still
included in the physical bound. No positive full-column or global margin
is inferred from these scalar numbers.

The original evaluator's `covector_kind` string is a stale descriptive
label (`FROZEN_LAST_RESPONSE_OUTPUT_ADJOINT_PROPOSAL`). The actual input is
the complete 248-component anchor adjoint, enforced by the algorithm,
dimension and four exact-covector checks. This label does not limit the
residual subtraction to the last response block. The raw output is preserved
to retain its independently reproduced bytes.

From the repository root, using fresh output paths:

```powershell
C:/Python314/python.exe scripts/evaluate_n12_gate7_full_output_adjoint.py --evidence-root ../BHSM-ae32-crossing-correction --out tmp/gate7_adjoint/midpoint.json
C:/Python314/python.exe scripts/certify_n12_gate7_shared_scalar_output.py --evidence-root ../BHSM-ae32-crossing-correction --adjoint tmp/gate7_adjoint/midpoint.json --out tmp/gate7_scalar/midpoint.json
```

Each scalar action contraction has a source-bound checkpoint. Checkpoint reuse
is a restart mechanism, not independent reproduction. Source changes reject
checkpoint reuse. Fresh processes and distinct checkpoint directories are
required for the independent arithmetic pair.

The independently reproduced scalar artifact is
`artifacts/flagship_integration/BHSM_N12_GATE7_RESIDUAL_CANCELLED_MIDPOINT_SCALAR_20260919.json`,
with SHA256
`906DDD0BEB1C9A14BEF7547E9C52E3115564C8A60228A01A64B4A74DABF886C3`.

For coefficient inspection, `scripts/export_n12_gate7_scalar_taylor.py`
recovers the two full physical Taylor models from the existing checkpoints.
It requires the recovered certificate to match every original byte before
export. Arb's ordinary radius constructor can round an already stored
30-bit radius upward; the exporter restores that exact magnitude using a
dyadic tuple and checks equality. No reconstructed radius may differ from
the saved radius. This recovery is not independent action reproduction.

```powershell
C:/Python314/python.exe scripts/export_n12_gate7_scalar_taylor.py --evidence-root ../BHSM-ae32-crossing-correction --adjoint tmp/gate7_adjoint/midpoint.json --certificate tmp/gate7_scalar/midpoint.json --checkpoints tmp/gate7_scalar/midpoint.terms --out tmp/gate7_scalar/coefficients.json
```
