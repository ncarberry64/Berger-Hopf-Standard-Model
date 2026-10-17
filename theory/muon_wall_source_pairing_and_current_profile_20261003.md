# Source-reached pairings and the current wall-profile coefficient

Start: `e983e4cfd98de81679d74106d181325e7b618935`, PR #465,
`codex/muon-parent-maxwell-density-review`. Scientific reference remains
`524ed90689bd5923c249bba2e699abf627e703cd`. Checkpoint:
`BHSM_MUON_SOURCE_PAIRING_CURRENT_PROFILE_COEFFICIENT_20261003`.

This continuation evaluates the actual source functions, their geometric
pairing, the geometric wall mass density and the initial proper-normal
coordinate jet. It does **not** evaluate the requested wall overlap T or
B54,F. The first remaining coefficient is the restriction of the adopted
eta normal-mass/profile field to the current collar. The retained static
eta solution exists; its attachment to this C2 join is not established by
the inspected action equations. No static-profile solve was repeated.

The H-rate repair, explicit rate contract, old/new n1/n3 derivative arrays,
all 17 unaffected body arrays, contact certificate and trial conormal remain
unchanged. Their five checks were not rerun. The common-A effective action,
chiral mass-block structural assembly, reset graph and frozen local results
were not reopened.

## Four distinct maps

The geometric pointwise trace gamma0 restricts a section to a surface.
B54,F is a normalized wall-mode projection W_eta^sharp in the owned
pairings. The reset transition transports the traces already identified
by the domain. The temporal conormal is the boundary form action of the
operator. Neither a point trace nor the previously evaluated temporal
conormal is the wall projection. In particular a compact radial probe
with zero material endpoint value can have a nonzero wall-mode overlap.

In finite notation the required object is

\[
 T_{ij}=\langle W_\eta e_i,p_j\rangle_5,\qquad
 M_4 B_{\rm required}=T,\qquad
 W_\eta^\dagger M_5 W_\eta=M_4.
\]

The last equation defines the realized isometry to verify, not permission
to choose W by rescaling an arbitrary inclusion. Its actual verification
and B54,F W_eta=I remain unevaluated. Pairing/source/trace derivatives of
W and B are likewise unevaluated, not zero.

## Evaluated source functions and pairings

The source-reached radial trial columns used in the completed body action
are retained exactly as

\[
 p_{A,k}(\rho,w)=\frac{T_b\widehat\chi(\rho)}{r(\rho)}
       \Xi_{A,\mathrm{unit}}(w)e_k.
\]

Here widehat-chi is the saved compact probe hat, **not** a wall mode.
The inherited auxiliary photon lifting is one on this support. T_b and
the eight source arrays are reused, and the four input spin columns are
read from the corrected archive. Every 64-component Spin/carrier output
and both n1/n3 angular ranges are retained. They are computational trial
functions, not external normalized physical muon states. The family
identity is retained symbolically without a family-count multiplier.

The implemented geometric volume density per boundary proper time and
normalized S3 Haar measure is

\[
 \mu_5=2\pi^2\nu C r^3.
\]

Thus the actual source Gram **density per unit d_tau at the saved cut** is

\[
 G^{\rm src}_{A k,B l}
  =\left(2\pi^2 T_b^2\int\nu C r\widehat\chi^2\,d\rho\right)
       \sum_{n=1,3}\langle\Xi_A e_k,\Xi_B e_l\rangle_{\rm Haar}.
\]

The radial scalar has an exact-rational integration and 256-bit Arb
enclosure for the declared binary64 piecewise-affine nodal model.
This is a new source-image pairing, distinct from the preserved compact
probe Gram and the earlier Z/A contact. The angular Gram and complete
source Gram are binary64 evaluations. Their Hermitian residual is zero;
the smallest floating eigenvalue is -4.841272740089613e-17. This small
rounding value is not a physical negative mode. The matrix is mathematically
a Gram; no eigenvalue enclosure or continuum bound is claimed.

The 32 source/input-spin columns have diagnostic numerical rank 12 at
tolerance 1e-10. No inverse or regularizer of this redundant Gram was
used, and that tolerance is not a rank theorem. A later solve must use
the appropriate independent frame or quotient with its own error control.
The n1/n3 source-array norms are 4.906795658328385 / 3.4696284839007108.
These are intermediate finite-array norms, not Pauli coefficients.

The complete known factor mu5*p_j at that cut is materialized
as `known_T_integrand_factor_mu5_p_n1/n3`. It can be contracted directly
with a justified current W_eta. If the proper collar chart changes time,
the same inherited source continuation must also be pulled through that
chart; the saved cut arrays do not supply that full temporal pullback.
No projection back to the old angular mode indices is justified.

At the true material wall, the induced time metric is
h_tau_tau=nu_wall^2-C_wall^2 zeta_wall^2>0. The evaluated geometric wall
mass density is

\[
 M_{4,\rm geom}=2\pi^2\sqrt{h_{\tau\tau}}r_{\rm wall}^3I_{64}
              =19.439716393985954 I_{64}.
\]

This is a four-dimensional geometric volume density, not a Cauchy/CAR
measure, a pole residue, or an independently normalized action term.
Both LR projectors are saved in the existing Clifford convention. They
sum to the full spin space; their sum does not introduce another density
factor. Tensor with normalized angular modes and the family identity as
required, without multiplying the scalar by mode or family counts.
No Q-index factor 2/3 is inserted.

Using only the already recovered boundary-proper-time rate,
partial_tau M4=3 H_f M4, with scalar value 5.17746720458415.
This is the temporal geometric derivative under the inherited clock
convention; it does not set photon-source or induced pairing derivatives
to zero. The tiny cached endpoint-shift roundoff and boundary-radius
matching residual 2.220446049250313e-16 are recorded explicitly.

These evaluated M4/source-M5 data are saved in the partial exterior K/M
operand ledger. T, B and the required interface form action remain null.
No local M4 expansion is added as a second determinant or owner, and no
stationary solve is claimed from these partial mass operands.

## The current normal coordinate cannot be replaced by rho

The retained Lorentz coframe is

\[
 \theta^0=\nu d\tau,\qquad
 \theta^4=C(d\rho+\zeta d\tau),\qquad
 ds^2=(\theta^0)^2-(\theta^4)^2-r^2d\Omega_3^2.
\]

On the actual radial source support the induced metric of a fixed-rho
surface has h_tau_tau=nu^2-C^2 zeta^2. A quartic Bernstein certificate
encloses it on **every full one of the 16 affine support cells**:

\[
 -4.7898766492221645\leq h_{\tau\tau}\leq-2.5060428744284664<0.
\]

Scope is the exact binary64 affine nodal model, excluding unknown
continuum/history reconstruction error. In that model these interior
fixed-rho surfaces are spacelike, while the true material wall is
timelike. Consequently its spacelike collar normal cannot be continued
by treating the entire fixed-rho foliation as the same spacelike-normal
chart. This does not invalidate the time-ADM metric or prove the absence
of a proper wall collar. It identifies a concrete failure of the shortcut
s=rho or ds=C d_rho at fixed time across this support.

The proper Gaussian normal chart X(s,y) starts from the actual material
wall, with opposite initial normals, and satisfies

\[
 \partial_s^2 X^a+\Gamma^a{}_{bc}(X)
             \partial_sX^b\partial_sX^c=0.
\]

At the inherited seam zeta=0 its outgoing initial jet has
tau_s=0, rho_s=1/C. The evaluated right-first-time-cell model gives

\[
 \rho_s=1.0427038213409683,\quad
 \tau_{ss}=-4.960206147770707,\quad
 \rho_{ss}=0.00040074957908572446.
\]

The incoming rho_s reverses sign; the second derivatives are unchanged.
The time term is
tau_ss=-(C_tau-C zeta_rho)/(C nu^2), retaining the shift derivative.
It is not the inherited H_f or the affine-logR slope. This initial jet
was checked independently with the metric Christoffels. It is not an
evaluated finite collar chart, and its right-cell reconstruction error
is separate from the preserved H interval. Actual continuation uses the
already inherited physical past prefix; no new past arm or future tail
is justified by a local Taylor expansion.

Spin/carrier transport along a realized chart must obey its same-connection
parallel equation in the inherited section and preserve the geometric
pairings. The common-A angular one-form has no direct tau/rho component
on angular-fixed normal curves. That observation does not remove spin
frame transport, the full one-form conversion, or induced variations.
No new U54, Euclidean-adjoint convention, endpoint condition or normal
sign replacement was selected here.

## Exact first unavailable profile coefficient

The adopted v14.45 action has

\[
 A_\eta=\partial_s+\tfrac12\partial_s\log J_\eta+m_\eta,
 \quad m_\eta=-\partial_s\log\sin f_\eta,
 \quad u_0=N J_\eta^{-1/2}\sin f_\eta.
\]

It fixes the zero mode and normalization **given its current eta profile**.
The displayed normal equation is an identity with this m_eta; it does
not select f_eta from unit normalization alone.

A genuine retained solved profile is present in the lineage:
v13.1 `eta_static_texture_v13_1` solves the degree-one radial problem

\[
 \partial_r[r^6(\kappa_1+X^3)F_r]
       -6r^4(\kappa_1+X^3)\sin F\cos F=0,
 \quad X=F_r^2+6\sin^2F/r^2,\quad F:0\longrightarrow\pi.
\]

v15.26 `retained_eta_profile_response` uses this solution in r=exp(x)
and constructs N^2 sin^2F dr. Its saved response artifact is retained;
the BVP and probability calculation were not rerun. The analytic sech
function in v14.45 is explicitly a witness and was not substituted.

The current C2 action instead has the join map
eta=(cos(f)u,sin(f)v), f=chi, and angular energy
3 cos^2f/A^2+3 sin^2f/B^2. Its material probability density is proportional
to sin^2f cos^2f. v15.32 expressly rejects transplanting the S6 radial
sin^2f trace onto the Hopf join; current v15.46/v15.81 use this join
density. v15.75's fermion wall kernel retains the separate u0 formula.
These are concrete equations, not decisions based on an old status label.

The first coefficient still to supply is therefore

\[
 \boxed{\ m_{\eta,\rm current}(s,y)
          =-\partial_s\log\sin f_{\eta,\rm current}(s,y)\ }
\]

on the collar points overlapping the saved radial trial support. A minimal
equivalent datum is its normalized normal probability pullback
J_current|u0_current|^2 ds=N^2 sin^2 f_eta,current ds, together with the
adopted same-section mode identification. This is a particular normal
Dirac coefficient / overlap density, not a demand for the whole B54 kernel.
If the retained static F is the applicable solution, its necessary current
restriction would give

\[
 m_{\eta,\rm current}
  =-F_r(r_{\rm tex}(s,y))\partial_s r_{\rm tex}(s,y)
                        \cot F(r_{\rm tex}(s,y)).
\]

The inspected producers supply neither that current-to-texture profile
identity nor an equality fixing the Dirac wall probability from the
current material join probability. Geometric transport equations can be
implemented from the retained metric/connection once a valid chart is
realized, but they do not establish that scalar profile identity. The
two reductions have different geometry and angle ranges. Calling both
fields eta, or equating their normalized endpoint integrals, is insufficient.
No claim is made that the full BHSM equations admit alternative physical
backgrounds; this is an unresolved **same-action current-profile
attachment**, beyond an absent array-building routine. It is not a new
freely adjustable profile, localization coefficient or boundary law.

Producers: v14.45 `foundational_action_payload`, v13.1 `log_profile_ode`,
v15.26 `normalized_eta_probability_response`, v15.32's join restriction,
and the current v15.81 eta realization. Immediate consumer: u0_current in
the known T_ij integrand, then M4 B_required=T and the M5/M4 interface
actions of the inherited exterior K/M solve. This normal profile term is
distinct from the already-assembled chiral family mass block M_l.

## Checks, execution and restart

One new focused replay ran once; four new targeted checks now pass.
The first run had three passes and one failure in a floating 2x2 inverse
comparison at tolerance 2e-15. Its maximum relative difference was
3.02515669e-15. That comparison now uses 16 epsilon times the actual
metric condition number; only that failed check was rerun and passed.
The exact polynomial sign certificate did not change. All source arrays
and scalar evaluations from the single production run were preserved.
No original production, H repair, contact, body, conormal, precursor,
static eta BVP, full suite or old five-check replay was executed.

```powershell
python scripts/replay_muon_wall_source_pairing.py --output <fresh-output-directory>
python -m pytest -q tests/test_muon_wall_source_pairing.py
```

Resume from `artifacts/muon_wall_source_pairing_20261003`: actual p_j,
mu5*p_j, source Gram, M4 density/time derivative, chiral projectors,
normal jets, nodal certificate, input hashes, partial exterior ledger and
missing coefficient are retained. Source/geometry/interpolation errors,
profile and transport matching, complement, native length and
renormalization remain separate. The source Gram and wall volume are
neither a wall-overlap result nor a physical anomaly/uncertainty.

The inherited reset graph, past prefix and canonical stop are unchanged.
The earlier trial conormal must be applied to a solved exterior field
before it becomes a stationary N_out response; none was solved here.
No full K/M action or heat of an isolated finite block is substituted.
All frozen local values and their calibration convention are unchanged;
physical a_mu and g_mu remain null.

**One next operand:** derive/evaluate the boxed current eta normal-profile
coefficient (or its equivalent normalized probability pullback) from the
adopted same-action current-background restriction, then contract the
saved source integrands and use B_required in the exterior solve.
