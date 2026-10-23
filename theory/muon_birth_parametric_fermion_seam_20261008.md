# Parametric incoming fermion parent and seam cotangent

The companion reaches **milestone 3**: the retained incoming carrier and positive AE2 seam admit uniform response/cotangent transport bounds, but the **incoming C1 additive LR/Higgs bridge action cotangent** remains unenclosed. No physical lambda, duration, covariance or reset representative is selected. The previous `P_F`, order 0, point-input result and six-argument guard remain unchanged.

Starting head: `60a6078844d08c0b101462eb712afbae8c12a739`; branch `codex/muon-parent-maxwell-density-review`; scientific reference `524ed90689bd5923c249bba2e699abf627e703cd`. All four retained coefficient-family, negative-axis, force-adjoint and intrinsic-time-quotient records are reconciled without rerunning their producers.

## Same-domain response decomposition

On incoming C1/branch23/E1-minus, `A_car=d_tau+W`, `W=chi*mu*exp(-x_C1)`, and `M_f=M11=d/b` after the existing zero-birth Dirichlet reference. The canonical normal zero-mode pullback and action trace pairing are inherited. The carrier internal identity adds no family mass or normalization; AE4 statistics grading stays inherited.

```text
P_F(lambda,z)=P_F,carrier(lambda,z)+P_F,owned_LO(lambda,z),
P_F,owned_LO := DtN(retained full incoming quadratic action/domain)
               -DtN(carrier quadratic action/domain).
```

This exact same-domain response difference retains interior solutions, pairing, outward orientation and boundary/domain pullbacks. It is not `M_f` plus a local mass matrix; its lower-order value remains null. If an existing common first-order embedding `D_full=D_car+E_LR` is verified, the squared form includes `D_car^dagger E_LR+E_LR^dagger D_car+E_LR^dagger E_LR`. This conditional expansion does not establish that incoming embedding.

The additive bridge is not absorbed into the literal AE2 antisymmetrized density: beta-Hermitian `P_Y=-M_LR` would cancel there rather than reproduce the separate `-beta M_LR` action. The retained convention guard remains intact.

## Uniform carrier and seam bounds

For `0<lambda<=lambda_star=1.33025636847111862e-30`, the retained theorem gives `T=a(lambda)lambda^2`. For one retained product channel and fixed `z=-kappa^2<0`,

```text
exp(-4 S a_upper lambda^2)/(a_upper lambda^2) <= M_f,
M_f <= max_T [1/T+S+(S^2+kappa^2)T/3],
S_car=M_f+U_R^dagger M_C2 U_R >= M_f > 0.
```

The [carrier companion](../src/bhsm/interface/muon_birth_parametric_carrier_bounds.py) evaluates exact rational bounds using `delta=4 S a_upper lambda_star^2<1`, `exp(-x)>=1-x` and `exp(x)<=1/(1-x)`:

```text
(1-delta)/a_upper <= lambda^2 M_f
 <= 1/a_lower+S lambda_star^2+(S^2+kappa^2)a_upper lambda_star^4/3,
||S_car^-1|| <= a_upper lambda^2/(1-delta)
             <= b_star=a_upper lambda_star^2/(1-delta).
```

Unscaled `M_f` has no finite uniform upper bound as lambda approaches its excluded zero endpoint; the scaled response and seam inverse do. The spectral probe is a bound scope, not physical momentum. A finite-channel certificate does not bound every spatial level, every negative spectral probe or a continuum tail.

Retained JSON decimals are read as exact Fractions. To preserve the additional producer edge-duration rounding, the coefficient interval is widened to contain the original bounds and `T_edge/lambda_star^2`. This is a conservative whole-family envelope and does not select the edge as a physical member. Replay records exact rationals and outward 80-digit decimal brackets.

For the retained lowest product channel at `z=-1`, conservative short decimal bounds are `9.51278567e-16 <= lambda^2 M_f <= 8.2373015e-15`, `b_star <= 1.860214313e-45`, and `b_star^2 <= 3.460397288e-90`. These are uniform family bounds at that channel/probe scope. The reported returned-load ratio also retains the maximum of the exact analytic majorant and the original rounded ratio, avoiding a stronger precision claim from decimal replay alone.

The original worst-duration facts remain: lowest product channel, `z=-1`, `M_f in [5.375724686360878e44,4.654941939686264e45]`; returned C2 load at most `4.450533100137867e7`; ratio `8.278945369783579e-38`. The stored maximum sampled ratio is about `2.15e-37` over the source rows. These are retained reproducibility/dominance bounds at their certified scopes, rather than physical `P_F[0]` values or all-probe bounds.

## Uniform cotangent transport and retained action adjoint

The existing implicit-adjoint pattern is applied to the invertible carrier seam:

```text
S_car v=r, S_car^dagger p=g,
<g,Dv>=<p,Dr-(D S_car)v>,
D(S_car^-1)=-S_car^-1 (D S_car) S_car^-1.
```

The evaluated transport factors give `||p||<=b_star||g||` and `||D S_car^-1||<=b_star^2||D S_car||`. The seam-solve operator cotangent has norm at most `b_star^2||g||||r||`. For `ReTr(G^dagger S_car^-1)`, its signed cotangent is `W_S=-S_car^(-dagger)G S_car^(-dagger)` with `||W_S||<=b_star^2||G||`. These factors multiply actual source/readout bounds; no unit physical source or terminal covector is inserted. The symbolic contraction residual is zero.

The retained transition-covariant derivative absorbs ordinary frame derivatives of `U_R`, so `nabla U_R=0` and `nabla S_car=nabla M_f+U_R^dagger(nabla M_C2)U_R`, with fermion `W_phys=0`. This retains covariant measure/domain response and does not freeze a physical moving interface.

The existing nested action adjoint and endpoint projection are reused:

```text
-D_tau p=A^dagger p+q, p(T)=Pi_T^dagger g_T,
q_xi=B_reset^dagger p(0)+q_direct.
```

Only the exact whole-system time orbit is quotiented. Common scale remains physical. The retained `q_rep|ker D_C=0 iff q_rep in range(D_C^dagger)` is read, not rederived. Actual complete E1 `q`, `g_T` and `q_direct` remain null.

For a completed seam correction `R_Sigma`, an owned relative bound `rho=||S_car^(-1/2)R_Sigma S_car^(-1/2)||<1` permits `||S_total^-1||<=b_star/(1-rho)`. Here `rho` stays null. Positivity of bulk `D^dagger D` does not make its response correction nonnegative or preserve the old numerical inverse bound. The positive AE2 formation seam is not declared equal to the complete retarded AE4 KKT Schur block.

## Exact blocking action contribution and sector ownership

The adopted collar action already contains `S_H=-integral dmu4[bar(Psi_+)Y_f H Psi_-+h.c.]`. Its incoming LR coefficient and action variation are

```text
M_LR,C1(lambda,rho)=[[0,Y_f H_C1],[H_C1^dagger Y_f^dagger,0]],
K_alpha,LR,C1=-[(b_alpha beta+delta_alpha beta)M_LR,C1
               +beta delta_alpha M_LR,C1],
b_alpha=delta_alpha log dmu.
```

The unresolved object is **this incoming additive LR bridge action cotangent**, with its normalized trace/domain pullback and DtN/contact response in the consumed E1 directions. The carrier family bounds `W=chi*mu*exp(-x_C1)` but contains no uniform `H_C1(lambda,rho)` or `delta_alpha H_C1` restriction. Thus it does not enclose this term or prove its CAR projection zero. Only its projected contribution is necessary; pieces in the frozen CAR tangent annihilator need no further reconstruction. A bound or owned cancellation could close it without selecting lambda or covariance. Physical member selection has not been proved necessary.

The [owner receipt](../artifacts/muon_birth_parametric_fermion_seam_20261008/lower_order_owner_receipt.json) records exact action owners, canonical normalization and source spans. Fixed-background LR/Yukawa/HS endomorphisms belong inside `fermion_family`. Higgs kinetic/potential, HS inverse kernels, scalar determinant two-point terms and intrinsic/HS mixing Hessians belong to the separate scalar/`HS_scalar` block; they are not added again as fermion masses. The charged-lepton HS channel and its shared vertices/cross contact exist. Their numerical current-C2 realization is not copied to C1. Unverified fermion-scalar/gauge mixed blocks stay null, not zero.

## CAR decision scope

The frozen projection is `S_alpha=Q E_charge P_Gamma_minus Herm(Delta_alpha) Q`; minimal moment count is `dim_R span{K_mu,alpha}`, not matrix rank of `P_F`. The complete projected kernel and moment-span coefficients remain null because the specific incoming LR term is unenclosed. This is not an interval demonstrated to straddle zero, and no coefficient is declared to require physical member selection.

`[M_f I,T]=0` holds uniformly only for its channel-preserving quadratic Noether commutator. It does not imply zero for every ordered stress/cotangent CAR row: an ordered particle scalar `A=a I` can consume `-Tr(delta C A)`, whereas a genuinely Gamma-even doubled scalar projects to zero. The action readout fixes that embedding. No fixed occupation or charge expectation is imposed.

Tiny returned-load dominance controls size, not exact projected zero or independence. An arbitrarily small surviving contribution can change the verdict or moment rank. A uniform rank claim needs exact independence or a nonvanishing minor bound across the family. Focused examples are CONTROL_ONLY; Green cancellation is not substituted.

| Label | Scope |
|---|---|
| DERIVED | Same-domain response difference; rational family/adjoint norm bounds and conditional completion criterion |
| EVALUATED | Source hashes/spans; rational carrier/seam cotangent factors; exact symbolic contraction |
| CONTROL_ONLY | Supplied exact projection, small-correction and rank examples |
| UNEVALUATED | Incoming LR bridge restriction/projected cotangent, completed parametric P_F and full CAR verdict |
| OWNER_DEFINITION_GAP | No new action or selector requested; a retained action term is not enclosed on the incoming family |

## Reproduction and error scope

```text
python -m pytest --noconftest -q tests/test_muon_birth_parametric_fermion_seam.py
python scripts/replay_muon_birth_parametric_fermion_seam.py --out artifacts/muon_birth_parametric_fermion_seam_20261008/run_1
python scripts/replay_muon_birth_parametric_fermion_seam.py --out artifacts/muon_birth_parametric_fermion_seam_20261008/run_2
```

[verification.json](../artifacts/muon_birth_parametric_fermion_seam_20261008/verification.json) records replay bytes/hashes, exact values, actual test/audit outputs and prior-milestone preservation. New rational/symbolic arithmetic is exact and decimal brackets round outward. Inherited coefficient intervals/edge samples retain their original theorem and numerical scope. No enclosure producer, point KKT solve or continuum tail calculation is rerun. Both prior milestones and frozen predictions remain unchanged.

Focused output: **67 passed in 1.30s**, exit0. The payload is **34,668 bytes**, SHA-256 **`7853ff209669b67cf25807c69cc69ff76c1e49c7d24dc081d47b073e803be753`**. Its symbolic residual is `0`, complete CAR verdict is null, and physical-member and point-KKT flags are false. Source-manifest and receipt hashes are recorded separately to avoid circular report hashes.
