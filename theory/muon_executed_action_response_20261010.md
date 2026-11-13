# Executed material-chart action and source responses, 10 October 2026

The corrected material-chart action has been applied and its 130 represented
Newton equations solved. The scaled residual is
`1.6792111975002982e-16`. The **total assigned** multiplier density remains
`0.36207908379117937` at the sampled interior nodes. At the retained E1+
endpoint it is `0.06631265484701808`, contributed by the active Higgs sector.
This is an evaluated finite action application, not a stationary full-field
muon realization. Subsequent source applications use this explicitly off-shell
iterate; they do not relabel the saved geometric reset as a complete base.

The retained domain is the outgoing branch-24 E1+ numerical germ, on the
local interval `[-0.001,0]`. Its length is a computational interval, not a
particle lifetime or a physical E0 location. The ambient parent Maxwell
attachment describes the spatial action sector; it does not turn this domain
into an evaluated incoming temporal C1 history.

The independently evaluated transverse two-loop W/Higgs/photon projection
adds `+3.2364905504452555e-11` to the preceding calibrated subtotal. The new
additive **subtotal** is

\[
a_{\mu,\mathrm{evaluated}}=0.0011659186179552334,
\qquad g_{\mu,\mathrm{evaluated}}=2.0023318372359107.
\]

For spin projection `S_z=+hbar/2`, the corresponding subtotal magnetic moment
is `+4.4904461711482596e-26 J/T` for mu+ and its negative for mu-. These
numbers exclude the unfinished disjoint native remainder and the remaining
finite weak matching terms. They are not the final BHSM prediction and their
input uncertainty does not enclose those excluded contributions.

## Material trace application and the coupled action

The independently represented Maxwell one-form components are already
pulled back by `rho_phys=J*rho_ref`. On the material wall,

\[
A_{t,\mathrm{phys}}=A_{t,\mathrm{ref}}
 -\dot\rho_{\mathrm{phys}}A_{\rho,\mathrm{ref}}/J,
\qquad A_{\rho,\mathrm{phys}}=A_{\rho,\mathrm{ref}}/J,
\]

so the intrinsic temporal trace is exactly
`A_t_phys+rho_phys_dot*A_rho_phys=A_t_ref`, including its first and second
derivatives. Adding the Eulerian advection term to `A_t_ref` counts the
same motion twice. `muon_material_higgs_gauge_action.py` applies this exact
conversion while retaining the original metric, measure, lapse, radius,
normal and velocity jets. It leaves the earlier Eulerian backend unchanged.
Its internal zero removes only an extra connection-advection slot; it is
not a zero wall velocity or a vanishing parent radial gauge field.

The corrected common action contains the moving cap action, the independent
five-component Maxwell action minus its already-counted mechanical carrier,
and the intrinsic Higgs action on the same coefficient vector. The material
Higgs potential is retained as `S0+nu_squared*S1+nu_squared**2*S2` with
`nu_squared=4` an explicit action-unit parameter trial. The surface sector is
exported per gamma; its physical coefficient has not been fitted to the
Higgs residual. The common normalization is

\[
c_{\mathrm{Maxwell}}=\frac1{8(2\pi^2)^2},\qquad
c_H=\frac1{(2\pi^2)^2}.
\]

Thus the scalar-to-Maxwell ratio is eight in the Maxwell-normalized coupled
application. The Tr16 mechanical embedding index is included once.
Scalar complex variations use the real action dual `2 Re` once.

`muon_parent_temporal_enrichment.py` uses the same vector for geometry,
velocity, multipliers, all five gauge components, Higgs and normal fields.
The temporal basis is the compact polynomial times a Legendre polynomial;
its analytic rate is differentiated with that same vector. The corrected
one-polynomial run starts from the recorded initial seed, not the solution
of the earlier mixed-chart run. Four actual Newton corrections reach the
stated finite residual. Independent runs are byte-identical:

| Output | SHA256 |
| --- | --- |
| Material action archive | `4a16d56ec64eeb6c2db10000debf9695f24f7bef634e793011066ed88f8b9383` |
| Material action receipt | `3137302eb7b92d7c6b5f999095e82f84f55996ed20b2a47ec35a56c96495539c` |

The two-polynomial 256-row refinement also executes actual Newton
corrections, reaching a finite scaled residual `1.4676269288732884e-13`.
Its sampled total multiplier density has maximum `0.2841154275906492`
and RMS `0.1693992229045556`. This is a refined finite application with a
different temporal quadrature, not a uniform error bound. Its two independent
archives have SHA256
`765b87f3caec88d2a977d79a7590e2e759422ecc24336290c131777d552933ce`.

The old `canonical_wall_mean_run_1/2` used material gauge components in an
Eulerian scalar slot. They are preserved as superseded numerical controls.
The earlier 106-row zero-Higgs/interior-gauge run does not activate that
extra trace term and retains its original scope.

The historical receipt key `unprojected_constraint_density_max` stores
the **cap-sector** density. It was not the total interacting density.
The corrected producer explicitly adds the independent Maxwell and assigned
Higgs contributions. At the compact temporal endpoints, the represented
interior corrections cannot change the affine trace. The past total density
is `0.3975657548896275`; the active-Higgs birth-side density quoted above
also remains. Refining interior test polynomials alone is not a repair of
those endpoint equations. Endpoint and continuation cotangents must come
from the adjacent owned actions, rather than an imposed zero Neumann load
on the computational face.

An actual assigned-sector E1 constraint retraction uses the same-action
multiplier rows and Hessian columns. With the recorded geometry held only
as an initializer, it corrects the 37 velocities and 24 multipliers by
an underdetermined Newton step. The inherited state weights select a
numerical step, not a physical formation branch. The 24-row norm changes
from `0.2297137746722181` to `0.009134127820636072`,
`1.5279899775494767e-5`, and `1.293717898559522e-10`. The final maximum
row is `6.311511036027895e-11`. The velocity and multiplier update norms
are `0.02322293017625843` and `0.01499092358298717`.

No surface coefficient is chosen to cancel that load. This initializer
still must satisfy the actual two-sided canonical/reset/event equations
and scalar/gauge trace images. Those equations use the common birth time,
incoming branch 23 on its negative local arm and outgoing branch 24 on its
positive local arm. The corrected endpoint is not declared stationary or
fed to the native readout as a solved physical base.

## Coupled photon--Higgs response application

The full angular source uses the twenty scalar harmonics in shells `n=1,3`
with all five one-form and four unit-Tr16 internal components: 400 angular
gauge coordinates. Its actual eight wall sources are embedded in this
complete space; they are not an invariant eight-coordinate corner. The
unreduced coupled weak action has 80 algebraic temporal-gauge coordinates,
320 dynamical parent-gauge coordinates, 80 real intrinsic-Higgs coordinates,
and eight prescribed wall-source coordinates. The same action supplies all
Higgs--Higgs, gauge--Higgs, and gauge--gauge seagull blocks, including the
scalar canonical momentum, quartic potential, metric contacts and the
normalization ratio of eight above.

The Gauss elimination occurs on the **single unreduced action**. Its raw
coefficient interpolation is differentiated before the same-time Schur
elimination. Independent interpolation of an already reduced operator
would not preserve those identities. The temporal gauge contact rows and
their nonzero Euler reaction are exported. They are not declared null
directions of the off-shell Hessian.

For this angular-constant background, a homogeneous geometry variation
has Haar-odd mixed rows against `n=1,3`, so those particular linear rows
vanish by antipodal parity. Odd times odd is even and does not vanish;
this proof does not remove scalar backreaction or establish nonlinear
closure. All 80 scalar-response modes are solved together with the 320
parent-gauge modes.

The corrected first application obtains a relative 80-row Gauss residual
`1.6732247e-15`, relative action-boundary defect `2.64525e-14`, and advanced
scalar-current pairing defect `8.53572e-17`. The nonzero Euler reaction is
`20.033485`. The total assigned base density is retained alongside them.
The readout consumes the actual terminal scalar wall-current coefficient,
and the scalar momentum and current pairings are separately exported.

This calculation is a prescribed-wall Dirichlet-to-Neumann application.
An inverse for a free photon wall also consumes the adjoining child,
interface and exterior action response. Prescribed-wall response alone
does not supply that inverse. The retarded physical application and its
advanced adjoint remain distinct from a positive native heat operator.

## Normal response and the finite orientation identity

The evaluated 106-row action supplies an internal 105-row KKT block `K`,
its normal source `B`, and direct second derivative `D`. It includes
internal multiplier and gauge rows. Its floating response solves
`K*delta=-B`; it does not minimize the indefinite KKT matrix. The direct
term is `12945.370805792863` and the floating contraction is
`18026.187894457562`.

`muon_frozen_normal_schur_certificate.py` gives an outward arithmetic bound
for the **exact saved** matrices. For `r=K*delta+B`,

\[
z_*=D-B^T K^{-1}B
 =D+B^T\delta+\delta^T r-r^T K^{-1}r.
\]

Arb verifies `||I-QK||_F<1` and uses
`||K^-1||_2 <= ||Q||_F/(1-||I-QK||_F)` without assuming positivity.
At 192 bits the defect bound is `1.0608069065867608e-7`, the inverse norm
bound is `172385.04056716792`, and the residual quadratic error is at most
`5.590776954256519e-11`. The resulting interval is

\[
z_*\in[18026.18789451219,\ 18026.187894512306].
\]

This interval certifies stored finite arithmetic. It does not bound action
producer rounding, discretization, the nonlinear base defect, mode
selection, inertia, cutoff, or the anomaly. It is not the physical
`z_psi` of a selected birth section.

The homogeneous finite chart also supplies literal symmetry directions
`delta A=[A,eta]+Omega_body*A`, `delta H=-rho_H(eta)H`. The combined rotation
preserves the mechanical carrier. On the corrected material iterate their
image rank is three; the differentiated Ward defect
`H*M*c+M.T*residual` has norm `8.899706029117269e-16`. The exported eigensystem
has two numerical null directions at the chosen threshold. Neither this
threshold nor a finite Newton rank is a physical quotient certificate.
Source projections and residual terms are retained rather than silently
discarded or regularized. The failed Neumann certificate on the old
mixed-chart 129-row block writes no enclosure; its exact rejection is
recorded in the certificate verification file.

## Canonical fermion application

All eighteen retained Weyl entries are represented: left weak doublet times
three families times spin, and right charged singlet times three families
times spin. The density variable `chi=R4**(3/2)*psi` has its proper-clock
current Gram equal to the identity on this fiber. The geometric current
measure is kept separately. The fixed Yukawa operator acts on a general
Higgs doublet; no mean direction is replaced by a measured Yukawa fit.

The canonical Lorentz Hamiltonian includes the spatial spin connection,
the `3*gamma5/(2*R4)` term, `M(Y_l H)`, and `-i*Omega_tau`. Its Euler
application is checked against both Weyl equations, including a nonzero
expansion rate. The four canonical photon vertices and sixteen quadratic
contacts are evaluated on the inherited source geometry. The proper
spatial contact trace for all three families is `2.2233763364987835`.

A further temporal gauge check is essential. A time-dependent frame obeys
`H_can'=U H_can U.dagger+i Udot U.dagger`. Consequently
`partial_tau+H_can` is not a covariant positive factor. The separately
bound factor uses `W=H_can+i*Omega_tau` and its own covariant temporal
connection. The corrected implementation tests this law and preserves the
nonzero counterexample to the naive factor. It does not identify a
canonical Lorentz temporal vertex with a native factor vertex or square a
Lorentz Euler operator to obtain heat. Endpoint holonomy remains part of
the trace graph.

## Executed source-paired product heat component

`muon_native_product_factor_graph.py` applies the actual eight raw-Q source
coefficient maps to the corrected material iterate. A constant-angular
background preserves each Peter--Weyl shell, while these source maps send a
constant test into the complete `n=1,3` spaces. The reached action space is
`(1+4+16)*18=378` angular/fiber coordinates. The one-body inverse does not
preserve the original raw source image: measured outside-image fractions
are about 4.14% and 19.17% in the two shells. Thus its complete complement
solves are needed even for this particular source-directed contraction.

For a fixed two-endpoint form core and negative spectral probe `z=-1`, the
evaluated source contact channel trace is `0.21841277205833182`. Each ordered
response trace is `5.4807870400137585e-8`; contact minus both is
`0.218412662442591`. The complement solve residuals are `8.62e-17` and
`5.82e-17`. These are raw unit-Tr16 beta-source quantities. No extra measured
charge, old seven-port trace factor, or family multiplicity is applied.
They are not themselves an induced photon form or a Pauli coefficient.

The positive-core heat application uses its own FE Gram to realify the
generalized spectral problem. It computes the direct contact and both
ordered Duhamel terms. In the `n=0` projected trace the insertion term is

\[
\sum_{n=1,3}\int_0^s(s-t)\operatorname{Tr}_0
 [e^{-(s-t)P_0}P_v{}_{0n}e^{-tP_n}P_J{}_{n0}]\,dt
 +(v\leftrightarrow J).
\]

The contact is `-s Tr0(exp(-s*P0)*P_vJ_00)`. Integrating from a declared `c`
to infinity uses the positive scalar kernel

\[
\int_0^1(1-x)e^{-cq}(c/q+1/q^2)\,dx,
\qquad q=(1-x)\lambda_0+x\lambda_n,
\]

for the insertions, and `-exp(-c*lambda0)/lambda0` for the contact. The
infinite proper-time tail is therefore evaluated rather than cut off at a
finite numerical time. Independent spectral second variations check the
signs and both orders. The fixed diagonal Yukawa operator and family-identity
gauge maps justify separate middle/light family blocks; they do not choose
a physical fermion covariance.

The fine 17-node core has smallest `n=0` eigenvalue
`2.1168138995640166e7`. The chosen function probes are
`c=(0.25,1,4)/lambda_min`, approximately
`(1.1810202118e-8,4.7240808472e-8,1.8896323389e-7)` in action proper-time
units. They are explicit numerical probes, not the birth-side ratio `i/r`.
At the central probe the middle-family integrated raw heat channel trace
is `-1.1370773145117065e-6`. The 9-to-17-node difference is about 2.14%.
The middle-minus-light subtraction is about `1e-20` and its relative
accuracy is not established. Neither difference is an anomaly enclosure.

These finite Dirichlet-core components exclude the full stratified
supertrace, actual physical endpoint/reset/exterior binding, relative
zeta/eta completion, total coupled source and cutoff jets, and owned overlap
subtraction. No statistic sign or final charge factor is guessed. The
nonzero solved Higgs first response is available from the coupled action
application above and is the next vertex input. A genuinely mixed scalar
and homogeneous-geometry response must be produced by the same nonlinear
action; affine explicit photon coefficients alone do not make it zero.

That available Higgs first response is now consumed by
`muon_native_coupled_source_heat.py`. Its stored H80 value and rate define
the same Hermite interpolation and compact source pulse used by the
coupled retarded action. The physical temporal trace remains `At_ref/N`
once. The full fixed-Y doublet mass vertex is nonzero; its all-family norm
at the sampled point is `1.4813e-10`, compared with raw gauge-source norm
`8.0161`. The scalar-only and gauge--scalar interference terms are computed
separately so they are not lost by subtracting much larger gauge numbers.

At the central explicit cutoff probe on the 17-node core, the middle-family
gauge contact is `-5.642693770103521e-8`; each ordered gauge response is
`+5.1404184106013314e-8`, giving `+4.638143051099141e-8`. This differs from
the preceding constant-profile result because it consumes the evaluated
compact pulse. The scalar-only first-response sum is
`-8.148259860201681e-29`; interference is `-9.368378377099021e-29`.
The 9-to-17-node changes are respectively 10.34%, 1.58%, and 2.63%.
Those are estimates for this component and do not bound a physical native
remainder. The genuine mean `H_vJ` contact and remaining geometry/domain
response are explicitly unevaluated, rather than recorded as zero. The
same-action paired mean forcing is the next consumed producer.

## Additive calibrated projection and uncertainty

The transverse W/Higgs/photon result uses the independently measured GF,
MW, mH and charge with the fixed `g_hmumu=Y_mu/sqrt(2)` and
`g_hWW=2*MW**2/v`. Its primary formula is the gauge-independent transverse
projection in [arXiv:1502.04199v3, equations 21 and 28, section 4.1](https://arxiv.org/pdf/1502.04199v3).
The evaluated kernel is `5.9726031552670233`. Independent 70-digit literal
integration differs by `5.107e-26`; the ordinary quadrature estimate is
`2.7145e-23`. These are numerical checks and estimates, not rigorous
continuum bounds. This piece is disjoint from the previously counted
bosonic leading logarithm. No whole Standard-Model bosonic answer is
rescaled by the fixed-Y diagnostic ratio.

The additive ledger reuses every preceding contribution and sums signed
gradients before shared-input covariance propagation. In particular the
new fixed-Y term has derivative `a/m_mu`, not `2*a/m_mu`, and GF derivative
`a/(2*GF)`. The inherited GF source uncertainty is reused from the published
decay ledger. The unknown light-by-light metrology derivative remains
unknown; it is not recorded as zero. The native remainder is not placed
inside a generic higher-order allowance.

## Classification and reproducibility

* **DERIVED:** exact material trace conversion; same-action internal Schur
  identities; finite orientation Ward law; stored indefinite normal
  arithmetic bound; covariant canonical/factor distinction; signed
  shared-input accounting.
* **EVALUATED:** corrected finite Newton corrections and total assigned
  multiplier density; actual endpoint constraint corrections; coupled parent--Higgs retarded and advanced
  prescribed-wall action response; finite normal action response; canonical all-family
  photon vertices and contacts; actual eight-Q source-paired finite-core
  graph and heat contact with both ordered insertions; solved Higgs first
  response in fixed-Y source vertices and separately evaluated scalar and
  interference heat components; the additional transverse W/Higgs/photon
  projection and updated calibrated subtotal.
* **CONTROL_ONLY:** local temporal/radial trial spaces, action-unit
  `nu_squared=4`, superseded mixed-chart run, and illustrative independent
  primitive covariance.
* **UNEVALUATED:** full interacting birth realization and its physical
  quotient, total coupled source/domain/normal response, owned physical
  cutoff, complete relative native heat and overlap-subtracted Pauli
  remainder, remaining finite weak matching, and final observable error.
* **OWNER_DEFINITION_GAP:** none established by these calculations.

`action_selected=false`, `Gate7_closed=false`, and
`complete_observable=false` retain their existing meanings. The work
continues through the consumed action applications; an unfinished
implementation is not declared an independent physical datum.

Actual commands, stdout/stderr, source and output hashes, independent replay
comparisons, focused tests and publication audits are recorded in
`artifacts/muon_executed_action_response_20261010/verification.json`.
The projection and arithmetic certificate also preserve their own
verification files, including failed commands and the corrected error
scope. Some earlier lengthy terminal stdout was truncated by the tool;
the finite-sector receipt identifies those captures as null and preserves
the actual complete output files and their hashes. Later numerical runs
capture stdout/stderr to separate files. All focused concurrent checks use `--noconftest`: the repository's
global artifact-restoration fixture can otherwise mutate another producer's
active receipt. This option does not suppress the five separately executed
repository publication audits.

The reviewed focused test groups contain 83, 27, 4, and 5 passing tests
(119 total). Earlier verification is reused. Independent final coupled
response archives split the same 39 arrays into response and operator
files without pruning or changing any value, and preserve the initial
unsplit runs locally. The final replay pair is byte-identical; the
response and operator file sizes are 9,510,663 and 4,900,380 bytes. This
packaging preserves the existing publication policy and does not reopen
the already resolved repository artifact-retention issue.
