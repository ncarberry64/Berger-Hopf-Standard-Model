# Gate-7 full output vector for the retained midpoint direction

Gate 7 remains OPEN. This certificate includes all 74 output components of
`Y_phys=(2h/3) Q P DF(Z_M(theta)) w0`, on the original 249-parameter midpoint
domain and all 248 inherited implicit correction coordinates. It does not
replace the other input directions, endpoint transport, or global inequalities.

The independently reproduced Euclidean anchor-deviation bound is

    ||Y_phys(theta)-Y_phys,0||_2 <= 0.637526490805.

This decimal is rounded outward. Exact rational bounds, all signed shared
coefficients, per-component centers, linear supports, nonlinear remainders,
descriptor projection multipliers, dominant sources and scope are stored in
`artifacts/gate7/GATE7_PROJECTED_VECTOR_CERTIFICATE_v1.json`.

## Exact lifting identity

Write the normalized derivative as `F_u=(g,d)`, with 98 numerator-rate
coordinates g and one descriptor-rate coordinate d. Set `L=(2h/3)QP` and
`ell=L[:,98]`. The original scalar is `y=L[73,:]F_u`. Since `ell_73` is
rigorously nonzero, define

    v_i = ell_i/ell_73,
    C_ij = L_ij-v_i L_73,j  (j<98).

Then every output component obeys the exact identity

    (L F_u)_i = v_i y + sum_{j<98} C_ij g_j.

For row 73, v=1 and C=0 identically. This is algebraic descriptor elimination;
no component is discarded and exact unit length of the stored Q axis is not
assumed. Arb enclosures of v and C include these exact fixed coefficients.

The existing scalar model W encloses `y-beta G` on the common parameter and
correction domain. On the inherited physical graph G=0, hence W encloses y.
Reconstruct g from the SAME shared state, seven saved predictors and correction
radii, including complete physical normalization. Substituting W in the identity
therefore gives a rigorous Taylor enclosure for every physical output row.
It uses the vector residual covector `v beta`, whose role is cancellation;
no uniform adjoint theorem is assumed.

Shared linear coefficients are retained through this entire expression. Only
then are per-row product-domain supports and the Euclidean norm taken. The
full nonlinear remainder stays in every row. This final support relaxation
gives the reported finite vector bound without replacing the earlier shared
implicit dependencies by independent physical coordinate boxes.

## Reproduction and provenance

Starting checkpoint: `b33d94e4eaa94b6be9d7ca423d45205a23f5e797`.
Continuation branch: `codex/g7-vector-endpoint-final-closure`.
The required initial branch/status/log/stat/diff reconciliation found that
HEAD exactly matched the checkpoint and the working tree was clean.

```powershell
C:/Python314/python.exe scripts/certify_n12_gate7_projected_vector_lift.py --evidence-root ../BHSM-ae32-crossing-correction --scalar artifacts/flagship_integration/BHSM_N12_GATE7_RESIDUAL_CANCELLED_MIDPOINT_SCALAR_20260919.json --coefficients artifacts/flagship_integration/BHSM_N12_GATE7_RESIDUAL_CANCELLED_MIDPOINT_TAYLOR_COEFFICIENTS_20260919.json --out tmp/gate7_vector/fresh.json
```

Run twice with fresh distinct output files. The two current outputs are
byte-identical with SHA256
`DC23DA79789ED590437DB04813A7571B079F584357E07430158FBE3CFC56B6BF`.
No new action derivative was evaluated for this lift. The certificate binds
the inherited scalar, coefficient export, full physical source pairs, domain,
frozen projection and evaluator implementation.

There is no allocated midpoint-only Gate-7 acceptance threshold. In particular,
the difference between this bound and the complete-column budget is not a
global contraction margin. The next required operation is the complete
same-parameter endpoint/midpoint chain documented in the progress packet.

## Validated correction refinement (V2)

The complete vector bound improves to

    ||Y_phys(theta)-Y_phys,0||_2 <= 0.409189271846.

For a saved implicit predictor `u_hat=u0+J0 theta`, the original uniform
derivative solve enclosure `[Du]` and verified point solve `[u(0)]` give

    |u(theta)-u_hat(theta)|
      <= |[u(0)]-u0| + support(([Du]-J0) theta).

Intersect this correction radius with the original one. This is a bound on
the same physical solution over the unchanged input domain. The source
graph pairs solve blocks `(0,4)`, `(1,5)` and `(2,6)` as response/derivative,
axis-eigenline/mixed derivative and axis-response/mixed derivative. Its
normalization border equations are retained as well.

Substitute `eta_old=(rho_new/rho_old) eta_new` in the existing scalar Taylor
model, retaining its entire old nonlinear remainder. Reconstruct the
normalized numerator with the new correction radii and apply the same exact
descriptor identity. No action derivative is recomputed. The input domain,
parameters, norm and physical projector remain unchanged.

The refined certificate is `artifacts/gate7/GATE7_PROJECTED_VECTOR_CERTIFICATE_v2.json`;
its independent pair has SHA256
`8E9E931CCCD41C6217A4683F014D58EDCC17EDAEDFF64886868B720BEBF2C232`.
Use the same command above with producer
`scripts/certify_n12_gate7_projected_vector_lift_refined.py` and fresh output
paths to reproduce it. V1 remains valid and preserved.
