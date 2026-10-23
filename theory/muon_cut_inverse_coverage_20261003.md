# Source-directed cut range of the inherited muon collar

Continuation of PR #465, starting at `430093f067fb840bc4bfb006bf43abef37c4c308`, scientific reference `524ed90689bd5923c249bba2e699abf627e703cd`. The previously resolved daughter field, common-A coupling, source-rate repair, pairings, connected outputs and frozen local contributions are retained. No earlier production calculation or its four checks was rerun. This result settles coverage for the declared nodal normal realization; it is not a physical muon anomaly.

## Result and scope

Every inward normal launched at the material wall during the supplied tail interval

\[
0\le y\le 0.00014753362308861907
\]

has its first artificial step1222 cut intersection inside the outward enclosure

\[
1.5622813108230515\le R_{\rm hit}(y)
 \le 1.5707963267951317.
\]

All **64 actual saved Gauss source points**, spanning `0.5907527363892835 .. 0.9800435904056131`, lie outside this enclosure. Their certified separation is at least **0.5822377204174384** in this nodal model. Range rejection precedes root searches; no conclusion is inferred from missed shots or from extrapolating the saved local slope `-35.34587871146189`.

The tail statement is a rigorous coefficient-box/first-exit theorem for the exact binary64 nodal metric and its declared bilinear interpolation. The prefix statement additionally assumes the supplied owned q/v/m hull encloses its realization and continuous same-action gluing. Unsampled prefix-state and continuum metric errors have no new bound. This does not prove nonexistence in every continuum BHSM realization, nor make `B54,F` zero. The two independent physical strata are not identified by reversing the parameter of one curve.

## Whole-family enclosure

In the inherited Lorentz coframe

\[
\vartheta^0=\nu\,d\tau,\qquad
\vartheta^4=C(d\rho+\zeta d\tau),
\]

write the inward normal as `n_hat=(-sinh(theta),-cosh(theta))`, with `theta(0)=0`. The actual coordinate geodesic equations imply

\[
\tau'=-\sinh\theta/\nu,\quad
\rho'=-\cosh\theta/C+\zeta\sinh\theta/\nu,\quad
\theta'=a\sinh\theta+b\cosh\theta,
\]

\[
a=\frac{\nu_\rho}{\nu C},\qquad
b=\frac{C_\tau-\zeta C_\rho-C\zeta_\rho}{\nu C}.
\]

Arb at 192 bits encloses these coefficients on every one of the **47 whole temporal cells**, over the outer radial strip of width `0.02`. Values use convex hulls of bilinear-cell endpoints; derivative intervals are the actual nodal slopes. No corner sampling is used as an extremum theorem.

On the bootstrap `0<=theta<=0.1`, let `A>=|a|`,

\[
B_0=\inf b-A\sinh(0.1)>0,\qquad
B_1=A\sinh(0.1)+\sup b\cosh(0.1).
\]

Then `theta>=B0*s` and

\[
y-\tau(s)\ge B_0s^2/(2\nu_{\max}),\quad
s_0\le S=\sqrt{2\nu_{\max}T/B_0},
\]

\[
|\rho'|\le V=\cosh(0.1)/C_{\min}
 +|\zeta|_{\max}\sinh(0.1)/\nu_{\min}.
\]

The certified bounds are `S<0.008078892553528947`, `VS<0.008515015971609727`, and `B1*S<0.04035905974627974`. Both bootstrap bounds close strictly. The separate inward-wall condition

\[
\rho'\le-1/C_{\max}+|\zeta|_{\max}\sinh(0.1)/\nu_{\min}<0
\]

is certified (tail upper bound `-1.0354751235456157`). Thus no exit through the outer wall is overlooked. The proof covers the grazing `y=0` endpoint implicitly, every intermediate wall time, nodal interfaces and any family focal points: it is an image bound, not a global chart-rank theorem. For `y>0`, `tau` decreases strictly, so there is one transverse first cut hit. No division by small `tau_s` is used in the range proof.

For a transverse event the implemented derivative remains

\[
s_0'=-\tau_y/\tau_s,\qquad
R_{\rm hit}'=\rho_y-\rho_s\tau_y/\tau_s
 =-\Delta_X/\tau_s.
\]

## Inherited prefix and a new numerical endpoint

The old `5.274977187911087e-26` displacement bound applies to the previous already-transverse curve. It was neither recalculated nor used as a bridge to source support. Prefix-born wall normals begin with `n_tau=0`, so they require a different branch sign argument.

The action-owned attachment gives `Rcap=RADIUS0*exp(q0)`, `C_rho=Rcap*exp(u+w)/2`, and

\[
\partial_\tau\log C_\rho
 =(\dot q_0+\dot u+\dot w)/N_{\rm boundary}.
\]

The `/2` converts the inherited chi metric to rho and is not a new normalization. Near-constant rounded prefix configurations do not set this velocity jet to zero. The retained 1,238 state rows give a positive rapidity-rate lower bound `4.428424146035435` and inward radial upper bound `-1.0365561123762863`. With the unchanged prefix duration upper `1.4944995686293672e-27`, the separate wall-family bootstrap closes before E1 (length upper `2.59932700093425e-14`, radial-drop upper `2.7398568256075162e-14`). Prefix-born curves move further into the past and cannot hit the later cut; tail-born curves do not return after their first cut hit. No E1 crossing or new past arm is introduced.

One new endpoint on the physical tail-wall branch was evaluated, at the inherited future stop, using DOP853 and all **46 nodal temporal-face saltations**:

```
y     = 0.00014753362308861907
s0    = 0.008042366136094535
R_hit = 1.5624124111745232
tau_s = -0.03667665103284088
I_partial = 0.004004334035151555
```

This is a numerical branch application with no certified absolute ODE error, not a replacement for the rigorous range proof. Its partial mode integral is not a full normalization. Its arrays were reused when correcting a new prefix factor error found in review; the unaffected endpoint was not reintegrated. The first attempt stopped on a wrong producer filename before any calculation. Run 2's doubled prefix C was corrected to `C_chi/2` in run 3; the inward-wall premise was made explicit in run 4. These attempts remain in Downloads and are not the final certificate. No prior scientific result changed.

## The retained radial route and exact next action

The action supplies a concrete full-cap radial inclusion in v14.45, implemented for the older snapshot by `v15.76.shell_geometry` and `v15.82.regular_einstein_cartan_kernel`:

\[
ds=C_\rho d\rho,\quad J_{\rm rad}=(r/R_b)^3,\quad
I_{\rm rad}=\int_{\rm full\ cap}C_\rho\sin^2(\rho/2)d\rho,\quad
u_{\rm rad}=I_{\rm rad}^{-1/2}J_{\rm rad}^{-1/2}\sin(\rho/2).
\]

It uses the adopted outgoing daughter field, not the incoming static preon profile. Its fixed-time radial image reaches the saved source points. It is not a patch reparameterization of the disjoint Gaussian image.

For AE4's geometric L2 pairing, the calculable density conversion is

\[
J_{\rm vol}=(\nu/\nu_b)J_{\rm rad},\quad
u_{\rm vol}=\sqrt{\nu_b/\nu}\,u_{\rm rad},\quad
\Delta h_4=(\partial_\rho\log\nu)/(2C_\rho).
\]

The converted scalar radial operator satisfies

\[
(\partial_\rho\log u_{\rm vol})/C_\rho+h_{4,\rm current}
 +m_{\eta,\rm rad}=0.
\]

This density/normal identity was evaluated on the **same 64 source nodes** (normal cancellation residual `6.66e-16`, pairing-density residual `1.11e-16`). It does not substitute a radial mass coefficient for the adopted Gaussian coefficient. The current temporal principal ratio `nu_b/nu` spans `0.7465717774975276 .. 1.3492557328363046`, so a normalization identity alone cannot establish the full Dirac pullback.

The **one next operand** is the current same-owner radial-inclusion action and its domain intertwining:

\[
D_{5,\rm current}W_{\rm rad,current}
 =W_{\rm rad,current}D_4+\mathcal R_{\tau,\zeta,\mathrm{Spin}\times\mathrm{SM}},
\]

with its inherited `Gamma0`/reset graph and `Wsharp M5 W=M4`. The first action requiring application is the temporal/shift/Spin remainder, retaining the measured rho-dependent temporal coefficient and both chiral/connected outputs. Producers are the retained full radial recipe, current metric/common-A Dirac body and AE2/AE4 trace equations; consumer is `T=<W e,p>5`, then `M4 B_required=T` and the coupled exterior K/M solve. This is a concrete current implementation/matching task. No new eta selection, physical arm, independent normalization or boundary law is supplied or requested. Until that action is applied, neither the full normalized overlap nor stationary exterior response is evaluated.

## Evidence and reproduction

New files: `src/bhsm/interface/muon_cut_inverse_coverage.py`, `scripts/replay_muon_cut_inverse_coverage.py`, `tests/test_muon_cut_inverse_coverage.py`. Artifacts and input/output SHA-256 identities are in `artifacts/muon_cut_inverse_coverage_20261003`. The workspace receipt records the actual branch, HEAD and changes; the publication receipt records the final commit and reviewed diff. Parent metric hash remains `34ab3500a98197aa3db35f5f3d2e6e7234145e7bd819477e81efcbda3bebd95c`.

Reproduce new work only into a fresh directory:

```powershell
C:\Python314\python.exe scripts/replay_muon_cut_inverse_coverage.py --output C:\Users\carbe\Downloads\BHSM_muon_cut_inverse_replay_new --resume-endpoint artifacts/muon_cut_inverse_coverage_20261003/replay_reference
C:\Python314\python.exe -m pytest -q tests/test_muon_cut_inverse_coverage.py
```

Omitting `--resume-endpoint` recomputes the new endpoint only. It never replays the earlier production calculations. Four new targeted checks cover the rapidity/geodesic identity on actual metric arrays, the whole-family rejection, endpoint saltations/implicit derivative and actual-node density conversion. The first test's four-field unpacking error was corrected and that test alone rerun; the other three already passed. The range test then gained an independent inherited-array check of the chi-to-rho factor and was rerun once successfully.

The tail nodal bounds, prefix owned-jet premise, continuum errors, numerical endpoint error, saved source scope and unknown full-normalization remainder remain separate in `result.json`. All six physical native ledger entries remain unevaluated. Frozen QED/Higgs/selected-local values and their original calibration convention are copied unchanged. No native physical transfer direction, physical `a_mu`, `g_mu`, or magnetic moment has been obtained or compared with experiment.
