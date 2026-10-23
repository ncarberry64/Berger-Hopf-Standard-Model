# Moving material response and evaluated normal-action applications at E1+

The retained incoming/outgoing geometry now has an executable moving-normal
weak-action application. On the unit trial on the outgoing E1+ cap, the
retained geometric/eta/FR/local-Casimir action including the moving
EH/GHY/Hayward completion gives

\[
 S_s=3.6864628798657613,\qquad
 S_{ss}=51.802941278218455,\qquad
 S_{\dot s\dot s}=2.735441466130583.
\]

These are evaluated local action coefficients on a response-admissible trial,
not a physical mode, impedance, total inertia or Pauli prediction. The action
and domain are specified below; the saved reset is not promoted to a
stationary interacting base. This advance implements and evaluates the
operator sectors needed before mode selection rather than requiring a
precomputed formation-mode packet.

## Action, chart and normalization

The unchanged retained `aether_n3_exact_full_local_action_jet_v17_60`
Lagrangian is the geometric/eta cap functional (Einstein--ADM plus its locked
spatial GHY, normalized eta localization, odd-FR Routhian and the existing
local M4 Casimir). Its cap is `0 <= chi <= pi/4`; it uses 37 coordinates,
37 rates and 24 lapse/shift parameters. The per-angular-measure and FR
normalizations remain exactly those of that producer. The existing local
Casimir is exposed separately: it is not a newly evaluated native heat
remainder or an additional contribution to the frozen anomaly.

For the literal inherited response of
`aether_eta_sigma_response_constraint_v15_40.response_constraint_action`,

\[
 W=\sin^2f\cos^2f,\quad Z=\int_0^{\pi/2}W\,d\chi,\quad
 \sigma={1\over Z}\int_0^\chi W\,d\chi-\tfrac12,
 \quad S_{\rm response}=\int\lambda_\sigma(\sigma'-W/Z)d\chi.
\]

Both pole anchors, the global normalization and the material join trace
`f|wall=pi/4` are retained. For a prescribed trial normal amplitude v, put
`k=v/C_star(q)`. The relative eta trial

\[
 \chi_w(s)=\pi/4+s k,\qquad
 f_s(\chi)=\chi-{s k\over16}(21\sin2\chi+5\sin6\chi)
\]

solves both `delta f_wall=0` and `delta sigma_wall=0`. This follows from

\[
 a_1-a_3=-k,\qquad {a_1\over3}+{a_3\over5}=-{k\over2}.
\]

It preserves both material traces through second order. Reflection parity
implies `Z_s=0`, but **not** `Z_ss=0`:
`Z_ss=-231*pi*k^2/1024`. The normalized sigma second jet is retained. The
local monotonicity condition `|s k|<2/9` is sufficient, not a proof of a
finite nonlinear branch. On general normal tests these two response rows
and the pole conditions define a linear trial space; the two harmonics above
are one representation of a radial trial in it, not a formation criterion
or a completeness assertion for the physical normal space.

`muon_moving_geometric_action.moving_cap_action_jet` evaluates the original
metric, lapse, shift, eta kinetic and FR terms at the pulled coordinates
`chi=y chi_w(s)` with the moving integration Jacobian. Eulerian geometry is
fixed in the source direction; the join and its response move relative to
it. The trial amplitude includes the q dependence of `C_star`, so its mixed
metric terms are differentiated. The eta time derivative includes the
q-dependent chart amplitude and the independent normal rate. Common
advection of the geometry, eta and embedding is treated separately as
coordinate redundancy and is not called formation.

The spatial material-wall vector is `n_out=+C_star^-1 partial_chi`. It is
not the temporal E1 Cauchy normal `N_star^-1(partial_t-beta partial_chi)`.
Lowering this spacelike vector changes its radial sign in the retained
`(+---)` metric. The current event/cutoff remains
**BHSM-AE4-BRANCH-BIRTH-CUTOFF-2026-10-08**, on the common P-to-muon birth
surface, **MUON_CHILD_PLUS_SIDE_AT_BIRTH**, with no finite time offset.

The earlier saved-center `C_star^-1=0.48439260724886507` used the wrong
endpoint signs for w. The actual u/lapse modes have indices 1..12 and
w/b/shift indices 0..11. Bit-exact binding to the original NPZ on both
incoming and outgoing sides gives

\[
 C_*=1.9180902180140678,\quad C_*^{-1}=0.5213519106704843,
 \quad D_X\sigma/v=4/(\pi C_*)=0.6638058693888946
\]

in this retained coordinate-response chart. This corrects a diagnostic;
it changes no frozen prediction or prior committed receipt.

## Moving gravitational boundary and surface applications

For the material graph `chi=z(t)`, define
`U=C(z_dot+beta)/N`, `theta=atanh(U)`, `rho=A^3 B^3` and
`K_ADM=Hc+3Ha+3Hb`. Direct covariant divergence of the outward wall normal
in the retained ADM metric gives

\[
 \mu_W\operatorname{div}n
 =\rho D_{\rm wall}\theta+N\rho U K_{\rm ADM}
       +(N\rho)'/C.
\]

The moving-domain EH divergences cancel the `U K_ADM` and `N'/C`
contributions, the spatial curvature integration by parts cancels
`rho'/C`, and the coefficient-locked Hayward endpoint cancels
`[rho theta]`. The additional weak density is therefore exactly

\[
 S_{\rm moving\ grav}=-\int\theta D_{\rm wall}\rho\,dt.
\]

It is included once, with the original gravitational coefficient. This is
a gravitational completion, distinct from the membrane. Independent E1+
checks give its first normal derivative `13.982735310865392` and rate
contact `-4.382798885437481`. Omitting it would leave the incorrect
fixed-wall-extension first derivative `-10.296272430999645`. Its mixed
field-source derivatives are nonzero and are retained in the stored blocks.

The minimal interface sector is also applied as the same signed functional,

\[
 S_\Sigma/\gamma=-\int N\rho\sqrt{1-U^2}\,dt,
 \qquad \gamma=\alpha_{\rm FSC}\ell_s^{-7}
\]

on the M8 candidate. All its internal, multiplier and mixed derivatives are
stored per symbolic gamma, rather than placing it only in the normal block.
FSC-P1 does not select an exact numerical alpha; no observed electromagnetic
value is inserted. At this parity wall its first normal and internal-source
mixed derivatives vanish by `rho'=N'=0` and `U_base=0`, with explicit
provenance; its internal Hessian does not vanish. The evaluated coordinate
clock coefficients are

\[
 S_{ss}/\gamma=167.08563845735534,\qquad
 S_{\dot s\dot s}/\gamma=11.076966371789556.
\]

The equivalent proper-time area weak form retains
`(D_tau a-Hc a)^2-|grad a|^2-V_graph a^2`, with
`Hc=4.553410932794558` and `V_graph=-9.992785835914434` on M8.
Temporal integration by parts, its endpoint terms and the nonlinear
embedding contact remain explicit. This local graph form is not by itself
the constrained formation operator or impedance.

The separate unweighted M5 quotient has nonzero mean curvature
`0.020710357299546827`. The identity
`N A^3 B^3=(N R4^3) L_F^3` retains the moving fiber measure. No sum of
these distinct stratum representations is performed and no M4 embedding
is invented.

## Weak source, Hessian and actual base check

The stored arrays are local action coefficients in `(q,qdot,m)`; they are
not 98 independent Euler equations or an algebraic KKT inverse. For
compactly supported real geometric tests the source application is

\[
 B_qv=S_{qs}v-D_t(S_{\dot q s}v),\qquad B_mv=S_{ms}v,
\]

including rate-source coefficients and endpoint momentum contacts. The
same action supplies `H_qq,H_qv,H_vq,H_vv,H_qm,H_vm,H_mm`, to be assembled
as the temporal weak differential operator in the inherited domain and
pairing. The response module separately retains `R_eta,s^dagger Lambda`,
measure/normal motion and multiplier-test contacts. Exact response
elimination in the retained chart is not a claim that the complete
physical response multiplier has been solved.

At the outgoing center the norms of the direct q-source, momentum contact
and multiplier source are respectively `248.3185257720391`,
`94.98446967839416` and `74.61170161878546`. Thus neither the source nor
its constraint reaction is a geometric zero. All entries, including signs,
are retained in the replay files.

| Retained cap/trial | S_s | S_ss | eta/FR rate Hessian component |
| --- | ---: | ---: | ---: |
| Incoming C1 at E1, opposite normal v=-1 | 4.263975632622028 | 83.83948546365498 | 2.970583201714091 |
| Outgoing C2 at E1+, v=+1 | 3.6864628798657613 | 51.802941278218455 | 2.735441466130583 |

These one-sided applications are kept separately. Their action coefficients
are not added to imitate a full event drive or an impedance Schur value.

The recomputed geometric lapse/shift residuals are below `1.72e-13` in
binary64 quadrature. However, the area sector adds the actual lapse rows

\[
 (S_\Sigma)_{n_k}/\gamma=-N_*\rho_* (-1)^k,
 \qquad N_*\rho_*=5.437863897715984.
\]

Consequently the geometric reset alone is not a stationary base for the
area-augmented interacting action. Its additional active-field/drive rows
must be solved together; the saved multipliers cannot simply be reused as
the complete Lambda. We do not force the normal residual to zero by
setting drive equal to resistance or shifting the event. A diagnostic
attempt to invert the local instantaneous rate/multiplier matrix was
rejected: it had condition estimate `2.18e18` and no justified domain or
gauge quotient. Its enormous iterate was not consumed. The valid deliverable
is the weak operator application, not that attempted algebraic response.

## Actual promoted response and port consumer

The later AE3 covariant response uses `dell=C dchi`. It is applied separately
to the actual retained C profile, not silently substituted into the old
coordinate-normalized action. The two weighted trial equations are

\[
 a_1-a_3=-v/C_*,\quad a_1J_1+a_3J_3=-v/4,\qquad
 J_j=\int_0^{\pi/4} C\tfrac12\sin4\chi\sin(j\chi)\,d\chi.
\]

The 32,769-node outgoing evaluation gives
`Z=0.38085195895575363`, `Z_ss=-0.371474717017646`, trial coefficients
`(-0.6754086013443734,-0.15405669067388922)` and Eulerian/embedding wall
responses `-0.6564230381943374` / `+0.6564230381943353`.
The proper-response base/first/second rows cancel within `1.67e-16`;
the material trace rows cancel within `7.6e-15`. Pulled length and normal
operator derivatives include both metric-position and chart-Jacobian motion
and are evaluated on the actual C profile. The candidate proper profile
differs from retained sigma by up to `0.0017452870741877513`; its adjoint
and interacting stationary realization still require the coupled solve.
It is not relabelled as the reset-certified background.

`geometric_trace_jet` applies the actual explicit shape
`v/C_* (0,-1,1)` to the three geometric coordinates with Eulerian state
source zero in this trial. The 37-component canonical source contact is
available. The full material four rows require the complete action-owned
momentum/force/conormal/mixed-momentum/rate-direction projection on the
solved source, using `required_material_jet`. They are not zero padded;
no eighth port is introduced.

## First unexecuted interacting application and downstream accounting

The next reached active scalar application is specifically

\[
 b_H[\varphi]=D_s(\delta_H S_{\rm full})[\varphi].
\]

Its existing producer is
`ae31_c2_intrinsic_m4_lepton_action.first_variation_and_pole_gate`; the
retarded scalar domain is supplied by
`ae4_future_collapse_relative_boundary_domain`. The owned Euler row is

\[
 E_H=-D^2H-2\lambda_H(H^\dagger H-\nu^2)H-J_H,
 \qquad J_H=\bar e_RY_\ell^\dagger L_L.
\]

Its normal application includes
`-(D_s D^2)H-D^2(D_s H)`, the differentiated quartic potential,
`-D_s J_H`, and the actual metric/measure, conormal, source, constraint
and boundary terms. These enter the complete stationary Euler row and
mixed KKT source **before** internal elimination. The supplied q/v/m
center, normalized response, computed geometry/FR/boundary/surface blocks,
family/connection primitives and scalar UV Gram matrices were used or
retained at their declared scopes. The conditional Higgs saddle, homogeneous
HS zero and UV Gram inverse do not evaluate this active retarded pairing.
No active H/D_nH value or equivalent reached scalar response was recovered.

This is an **unexecuted coupled action application**, not proof of a new
independent datum or a new theory-definition gap. A source/dual-restricted
weak solve or action-owned cancellation can suffice. A complete incoming
P_F export, blanket CAR verdict or arbitrary covariance selection has not
been imposed as a prerequisite. Neither a mode packet nor a complete
inverse is demanded in place of implementing that solve.

All same-action sectors must enter one H/h/L_ss before
`H delta=-h`; separate sector Schur contractions cannot be added. No
stationary full-field base or physical psi_mu+ is certified by these sector
applications, so no z_psi, formation zero, F_E, Delta_imp,bulk, total r/i/c
or v/J/vJ jets are asserted. In particular the complete formation zero
would not set impedance or the native contribution to zero. The preferred
`<psi,I psi>=1` normalization is not replaced by unit trial amplitude or
by this partial rate Hessian.

The native chain still requires its actual sourced pencil/response,
relative completion, owned overlap subtraction, physical photon application
and paired electron-muon/LSZ-normalized soft Pauli contraction. Existing
primitive b-source responses are not soft-transfer derivatives. The final
accounting remains

\[
 a_\mu=a_{\mu,\rm frozen\ local}+\Delta a_{\mu,\rm disjoint\ native},
 \qquad g_\mu=2(1+a_\mu).
\]

Strong contributions stay inside the native ledger, once, after the owned
overlap subtraction. No numerical native remainder, final a_mu/g_mu or
complete anomaly enclosure is produced here. The frozen local interval and
all earlier milestone files and point-valued guards remain unchanged.

## Verification and explicit claim ledger

**DERIVED:** anchored W/Z and material traces through second order;
metric/measure/normal pullback; distinct gauge advection; coefficient-locked
moving GHY/Hayward weak term; same signed surface internal/mixed/normal
applications and temporal momentum contacts.

**EVALUATED:** the actual two one-sided N12 center applications and complete
local action coefficient arrays for those retained sectors; symbolic-gamma
area blocks; actual promoted proper-length response candidate; material and
constraint residuals; three-port shape image.

**CONTROL_ONLY:** independent finite differences, continuous quadrature
comparisons and arbitrary nonconstant test multipliers used to validate
mathematics. No control is a physical mode or source datum.

**UNEVALUATED:** the coupled interacting base/response multiplier,
reached b_H pairing, complete covariant action/domain assembly, physical
mode/nonlinear branch/simple crossing, total impedance/inertia/cutoff jets,
and disjoint native soft Pauli result.

**OWNER_DEFINITION_GAP:** none inferred. The missing evaluation has owned
field equations and a causal domain; packet absence proves no gap.

New focused tests: **51 passed**; existing KKT, birth-owner and physical
point-input regressions: **84 passed**. Independent continuous normalized
response and primal-action finite differences validate the source and
second derivative. Both action sides are checked against bit-exact original
NPZ state data and receipt-pinned SHA256. Earlier failed test assertions,
the diagnostic rejected inverse, final commands, outputs, file hashes and
repository audit results are recorded in `verification.json`.

The producer is materialized twice and all five result files must be
byte-identical. The outgoing 128-to-192 Gauss changes are `1.24e-14` in
S_s and `7.69e-12` in S_ss. Proper-response coefficient changes decrease
approximately by four per doubled grid. These are **refinement diagnostics**,
not rounding bounds, continuum/UV/branch-response certificates or Pauli
soft-limit uncertainty. The prior reset root-distance certificate is not
propagated through these new applications. Small residuals and passing
tests therefore do not establish an anomaly enclosure.

The publication record runs `audit_bhsm_status`, `audit_forbidden_claims`,
`audit_frozen_prediction_integrity`, `verify_precision`, and
`audit_public_readiness`. The immutable run receipt and every generated
source/test/result hash are in the verification record; earlier predictions
are not regenerated or refitted.
