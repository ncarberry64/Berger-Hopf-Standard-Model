# Full-cap radial inclusion action and source interface

This continuation evaluates a distinct retained radial construction after the
whole-family Gaussian coverage obstruction. It does not change that theorem or
its prefix premises. The radial candidate now has a full-cap normalization,
its declared temporal derivative, actual local Dirac actions, saved-source bulk
and Cauchy-trace overlaps, and a consumed local weak interface contraction.
The inherited global exterior response and physical muon anomaly remain
unevaluated.

Starting branch: `codex/muon-parent-maxwell-density-review`, commit
`ebe53e9037b88fce5885934f7424d4f7801270b6`; scientific reference
`524ed90689bd5923c249bba2e699abf627e703cd`. Only this continuation's files
and its line-ending declarations are changed. The primary repository, live
caches, frozen local results and earlier production outputs are preserved.

## Full-cap mode and pairings

The adopted effective action is
`completion/foundational_dirac_spin_glue_v14_45.py`. Its proper-radial
application is retained in
`aether_cartan_shell_crossing_v15_76.py::shell_geometry` and
`aether_invariant_sobolev_schur_pushforward_v15_82.py::regular_einstein_cartan_kernel`.
Those historical production routines were inspected, not rerun. Their radial
prescription is used with the resolved current daughter field `f=rho/2`:

\[
ds=C_\rho d\rho,\quad I=\int_0^{\rho_b}C_\rho\sin^2(\rho/2)d\rho,\quad
J_{\rm vol}={\nu\over\nu_b}(r/R_b)^3,\quad
u_{\rm vol}=I^{-1/2}J_{\rm vol}^{-1/2}\sin(\rho/2).
\]

All 64 saved radial cells, from zero to the saved pi/2 endpoint, contribute to
`I` and `I_dot`. The norm is not the saved source-support integral. Arb at
192 bits evaluates the affine-cell primitive

\[
\int(a+b\rho)\sin^2(\rho/2)d\rho
={1\over2}\{a\rho+b\rho^2/2-a\sin\rho
-b(\rho\sin\rho+\cos\rho)\}.
\]

| Quantity | Outward binary64 enclosure in the declared nodal model |
|---|---|
| Full-cap `I_rad` | `[0.2763605005239409, 0.276360500523941]` |
| Full-cap `I_rad_dot` | `[1.3810262615005096, 1.3810262615005100]` |
| Bulk source overlap scalar | `[0.4851697335636422, 0.4851697335636423]` |
| Cauchy-trace source overlap scalar | `[0.5521811994475890, 0.5521811994475893]` |

The saved volume pairing is `mu5=2*pi^2 nu C r^3` and the wall volume
pairing is `M4=2*pi^2 nu_b R_b^3` with the retained normalized Haar convention.
Thus `W_vol^sharp W_vol=I` in that pairing. The normalization remainder is
zero for this explicitly declared finite nodal cap. No bound on the difference
from a continuum/history realization is claimed.

## Declared temporal jets and current local action

Interior metric derivatives are the unchanged right first proper-time cell
at fixed rho, used by the saved current Dirac-body implementation. `I_dot`
integrates exactly the same affine `C_tau` over the entire cap. Boundary
`nu_b_dot=0` follows its proper-clock normalization. The owned cut rate is
`H=0.08877816767234145`, with inherited interval
`[0.08877816713689007, 0.08877816820779219]`. Neither the historical H=0
placeholder nor the affine-logR slope is used.

\[
\partial_\tau\log u=-{\dot I\over2I}
 +{\dot\nu_b\over2\nu_b}-{\nu_\tau\over2\nu}
 -{3r_\tau\over2r}+{3\dot R_b\over2R_b}.
\]

The nodal wall rate `0.09356155343602983` and nodal boundary lapse derivative
`3.849540591256996e-10` are recorded separately. The resulting material
log-jet defect `log_u_tau,b + I_dot/(2I)=-0.007175078838009596` is explicit;
these reconstructions are not identified. The full volume norm derivative
still gives the declared `M4_tau=3 H M4`, because the interior density terms
cancel algebraically. This identity does not resolve the material temporal
attachment or certify a physical temporal jet.

In the saved `+----` coframe
`theta0=nu d tau`, `theta4=C(d rho+zeta d tau)`, `thetaa=r thetaR_a`,
`Gamma4=i gamma5`, the implemented geometric/common-A operator is

\[
D_{5,\mathrm{geom}+A}=i\Gamma^0[(\partial_\tau-\zeta\partial_\rho)/\nu+h_0]
 +i\Gamma^4[\partial_\rho/C+h_4]
 +\sum_a i\Gamma^a E_a/r+S_{S^3}/r+b_g\,\mathrm{GaugeUnit},
\]

\[
h_0={C_\tau/C+3r_\tau/r-\zeta(C_\rho/C+3r_\rho/r)-\zeta_\rho\over2\nu},
\quad h_4={\nu_\rho/\nu+3r_\rho/r\over2C},\quad
b_g=-{B\over A\sqrt{A^2+B^2}}.
\]

Here `C_rho` in a derivative denotes `partial_rho C`; the metric coefficient
`C` is the saved `C_rho` array. `S_S3=-1.5 i Gamma1 Gamma2 Gamma3`, tensored
with `I16`. `GaugeUnit=sum_a i Gammaa tensor jmath_a`, with
`jmath=2 sqrt(2)*unit_trace_carrier_basis[:3]` from the resolved common-A
attachment. No new connection coefficient is introduced.

The v14.45 eta bulk term is `i epsilon Gamma_perp m_eta`, not a scalar
physical LR mass. For this retained proper-radial prescription the principal
direction is `Gamma4` and `m_rad=-cot(rho/2)/(2C)`. The normal geometric
action and eta insertion are stored separately. Reversing orientation
reverses the derivative, normal connection and eta action together. This is
not a substitution into the excluded Gaussian realization. Physical Higgs
LR coupling remains the separate v14.45 seam `S_H`.

The coefficients of `D5 W` are saved independently:

\[
C_\tau=u\,i\Gamma^0/\nu,\quad C_a=u\,i\Gamma^a/r,\quad
C_0=u[i\Gamma^0 a_0+S_{S^3}/r+b_g\,\mathrm{GaugeUnit}],
\]

\[
a_0={1\over\nu}\left[-{\dot I\over2I}-{\nu_\tau\over2\nu}
 +{3H\over2}+{C_\tau\over2C}-{\zeta C_\rho\over2C}
 -{\zeta_\rho\over2}+{\zeta\nu_\rho\over2\nu}
 -{\zeta\over2}\cot(\rho/2)\right].
\]

The scalar normal cancellation does not discard these temporal, angular,
spin or common-A terms. `W=u I` is expressed in the retained common frame;
it is not asserted to be a radial parallel frame. No Spin boost was inserted.
Any future parallel transport must solve its owned spin/carrier equation and
use `S^dagger gamma0 S=gamma0`, rather than Euclidean unitarity.

Full-cap projected coefficients are approximately
`<1/nu>=1.109223936100664`, `<1/r>=1.228682508172811`,
`<a0>=-110.99091970564468`, `<b_g>=-0.3347472162883327`.
Their Arb enclosures are saved. `DeltaD4` compares the current
geometric/common-A wall symbol; no correction is absorbed into a changed
wall action or physical LR mass. The four radial coefficient deviations
forming `R_perp` are retained with their full Clifford/angular/carrier action.

## Actual saved-source overlap and consumed local interface

The unchanged b-source is `p_A=(T_b hat/r) Xi_A`. Both n1 and n3 source
sets and all 64 spin/carrier output rows are retained, with the family
identity kept symbolic. `beta=T_b b` is applied once. Neither the index-8
quadratic factor 2/3 nor the n2 contact fraction is a vertex multiplier.

Validated acb integration over the original support cells 24..39 gives

\[
T_{\rm bulk}=t\,\Xi_A,\quad M_4 B_{\rm required}=T_{\rm bulk},\quad
t=2\pi^2T_bR_b^{3/2}\sqrt{\nu_b/I}
\int C\sqrt{\nu r}\,\hat\chi\sin(\rho/2)d\rho.
\]

The wall measure appears exactly once. The original 64 Gauss-source
evaluation is preserved and compared with this scalar enclosure. Source
columns are not treated as an independent basis for a generalized inverse.

The local interface contraction already consumes these same functions:
`q_local(W wall,p)=<D5_geom+A+eta W,D5_geom+A+eta p>5`. The right source
action is the saved H-corrected current action plus the retained radial eta
term. Full angular derivatives use the saved `E_a=2i J_a` action before
projection; the adjoint pairing retains both angular indices.

| Intermediate array norm | n1 | n3 |
|---|---:|---:|
| Bulk `T` | 1.5845577144973177 | 1.120451505102511 |
| `B_required` | 0.08151135965067531 | 0.05763723515272805 |
| Local `K54_zero` | 2730.3361514420562 | 2579.733950544088 |
| Local `K54_tau` | 19.246794280822627 | 14.928468481248068 |
| Connected subset of `K54_zero` | 1507.363296363395 | 1541.057737395817 |

These norms describe intermediate arrays, not anomaly contributions or
uncertainties. Projected plus connected actions reconstruct the total;
the connected subset is not an extra addend. Signed shared H derivatives
are saved: `dH D5W=1.5 C_tau`, `dH D5p=-0.5 D5p_tau`, including both
cross terms and the second derivative. Unevaluated physical source,
pairing and domain derivatives are not assigned zero.

## Endpoint and reset scope

At the center, the declared nodal realization has `r~rho`,
`u~rho^(-1/2)`, volume density times `|u|^2~rho^2` and finite first-order
graph norm. Its limiting radial Green flux is zero. This is a local graph
closure statement, not smoothness or membership in the strong squared
domain. At the material wall the trace is `1.3450765982938255*psi`, not
`psi`. Opposite Green forms cancel when the full oriented traces match;
the global material extension is not yet evaluated.

The temporal Cauchy pairing is different from the bulk volume pairing:
`mu_Sigma=2*pi^2 C r^3`. Thus
`G_Sigma=M4 <1/nu>` and the evaluated trace overlap uses `sqrt(r/nu)`.
Both its projection `B_Sigma=G_Sigma^-1 T_Sigma` and the full radial trace
complement are saved. The latter restores the original compact source's
zero material trace even though its projected component has nonzero trace.
The inherited reset equation is imposed on full fields:

\[
\Gamma_{0,c}(W_c\psi_c+\chi_c)
=U_R\Gamma_{0,e}(W_e\psi_e+\chi_e).
\]

No invariant reduced range or zero connected trace is required. Both K and M
must use the appropriate full pairings. Canonical future stop and past prefix
remain unchanged. The corrected trial conormal is not a stationary exterior
response, and no isolated wall/probe heat has been evaluated.

## Recovered action-owned temporal coefficient and next operand

The cached `BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1221.npz` supplies
`exact_center_field_action`, `state_weights`, and `center_state` (also the
step1222 center). Its report supplies the signed descriptor sigma and Delta.
The producer's weighted field and inherited proper-clock equations give

\[
Y_\tau={\Delta\over N_b\sigma}\,{F_\sigma\over W_Y},\quad
\partial_\tau\log\nu=\sum_{k=1}^{12}m_{\tau,k}
[\cos(2k\rho)-(-1)^k].
\]

Sigma is a signed descriptor, distinct from radial distance and the
resolvent variable. The clock factor is enclosed by
`[7178468.554214995,7178468.554214997]`; the configuration rate agrees with
`v/N_b` to `1.7763568394002505e-15`. On the saved source points the direct
Fourier `partial_tau log nu` ranges from approximately `4.222208493546341e12`
to `9.6363855729708e12`. Nodal and direct reconstructions are saved separately;
their maximum difference is `2.429693438279297e9`. Neither is identified with
the earlier right-cell temporal reconstruction.

The isolated owned lapse-time summand
`-(i Gamma0 u/(2nu))*partial_tau log nu` has been applied to the actual
n1/n3 source directions at that supplied proof center. The complete center
action was not evaluated, and the center jet was not substituted at the
step1222 endpoint. This new recovered coefficient shows why the nodal
candidate action alone cannot be promoted to the current global forcing.

The first remaining operand is the same action-owned lapse jet at
`endpoint_predictor_center`, or a controlled enclosure on its inherited
tube:

\[
(\partial_\tau\log\nu)_{\rm cut}
={\Delta_{\rm cut}\over N_{b,\rm cut}\sigma_{\rm cut}}
\sum_k{F_\sigma(Y_{\rm endpoint})_{74+k}\over W_{74+k}}
[\cos(2k\rho)-(-1)^k].
\]

Producer: the cancellation-preserving field underlying
`audit_n12_c2_exact_center_fixed_s_field_matrix.py::build_payload`, with the
proper-clock conversion in
`certify_n12_c2_cancelled_field_lohner_step.py::build_payload`.
Consumer: the half-density temporal action and coupled exterior K/M on the
full source-reached trace plus complement. The smallest next calculation
contracts its lapse rows 74:86 at the endpoint or on the retained tube.
This is an uncomputed action coefficient, not an unspecified physical
profile, coupling, state or new boundary law. Center-to-endpoint control is
required; the supplied center value alone does not provide it.

## Error scope and reproduction

Arb/acb certificates cover the declared fixed binary64 nodal scalar operands.
Matrix roundoff and four-point weak-interface quadrature are not certified.
Inherited H uncertainty, spatial interpolation, center-to-endpoint error,
continuum/history reconstruction, global domain, connected propagation and
native heat/completion errors remain separate. The six native contribution
ledger entries, physical `a_mu`, `g_mu`, and total native uncertainty remain
null. Frozen selected-local terms are copied unchanged and never added again.

Executed new work: one full-cap scalar calculation, two subsequent small
source/trace extensions reusing valid scalars, one cached owned-center
coefficient extraction, six new scientific checks and one replay-metadata
input-rejection check. Old productions, old
checks, Gaussian searches, physical transfer evaluations and native heat
applications executed: zero. The six scientific checks test actual
nodal/operator arrays and their stated scope; they are not physical anomaly
evaluations. The seventh check consumes the cached owned result and rejects a
changed operand without a scientific rerun.

Run these from the publication worktree, choosing fresh output directories:

```powershell
C:\Python314\python.exe scripts/replay_muon_owned_prefix_lapse_jet.py --output C:\Users\carbe\Downloads\BHSM_owned_prefix_jet_new
C:\Python314\python.exe scripts/replay_muon_radial_inclusion_action.py --output C:\Users\carbe\Downloads\BHSM_radial_action_new --resume-scalars artifacts/muon_radial_inclusion_action_20261004/replay_reference --owned-prefix-jet C:\Users\carbe\Downloads\BHSM_owned_prefix_jet_new
C:\Python314\python.exe -m pytest -q tests/test_muon_radial_inclusion_action.py
```

Omitting `--resume-scalars` recomputes only this continuation's scalar
integrals. Input hashes are checked before cache reuse. The preserved
`replay_reference` and `owned_prefix_reference` record what actually ran;
the final checkpoint links them without repeating scientific calculations.
Publication metadata distinguishes the executed source hashes from the
later replay-metadata additions. Input/output hashes, targeted-check receipt,
equations, frozen ledger and the compact Downloads handoff permit resumption.
