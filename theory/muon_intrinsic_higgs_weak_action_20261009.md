# Intrinsic M4 Higgs weak application at the common muon birth

The retained child-plus geometry gives an evaluated mechanical Sp1
contribution to the intrinsic scalar action:

\[
 S_{H,AA}=-3w_S\kappa^2 H^\dagger H,
 \qquad w_S=0.6970926057096961,\quad\kappa=\lambda_{geom}
 \quad\text{on the owned child sigma0 section}.
\]

Its coefficient is **-0.5367568929392891**, its increasing-normal derivative
is **1.100829548404858**, and its second derivative is
**13.042486939849447**. The real weak linear coefficient from this term is
**-1.0735137858785782 I4**. These are local coefficients of an actual
retained action term, per coordinate time and unit-S3 measure. They are
not an evaluated field residual, impedance, formation eigenvalue, Higgs
mass, or Pauli contribution. The scalar fields multiplying these
coefficients remain the interacting primal unknowns.

This result accompanies executable nonlinear scalar residual, realified
Jacobian, metric and mechanical-connection cross applications, and their
insertion into the existing temporal geometry equations. It advances the
action application beyond string equations. The physical boundary-value
solve and magnetic-moment calculation remain incomplete.

## Domain, normalization and inherited owners

The baseline is PR465 commit
`181c869d1547c03c3661bf0072363eb9119e0aad`. Initial Git status was clean;
local HEAD and the remote branch agreed. The current cutoff is
`BHSM-AE4-BRANCH-BIRTH-CUTOFF-2026-10-08`, with
`MUON_CHILD_PLUS_SIDE_AT_BIRTH` on the common precursor-to-muon E1 surface,
without a finite time offset. No later support-loss surface was introduced.

The retained q/qdot/m values are bound bit-for-bit to the reset receipt
and original NPZ by `muon_moving_geometric_action.retained_state`.
The old geometric/eta/FR/local-Casimir, moving GHY/Hayward and surface arrays
are consumed from the preceding replay, without changing or rerunning that
producer. Coordinate-normalized historical response and the promoted
proper-length candidate keep their preceding separate scopes.

The intrinsic scalar domain is **M4=R_t x S3_boundary**, with
`R4=A B/sqrt(A^2+B^2)`, owned by
`aether_diagonal_sp1_m4_attachment_v15_50`. The scalar/lepton action is
`ae31_c2_intrinsic_m4_lepton_action.action_composition_contract`. The active
Higgs is an intrinsic complex doublet, not the historical auxiliary HS
zero graph. The normalization is the literal unscaled complex field, with
real pairing `2 Re`; real coordinates are `(Re H1,Re H2,Im H1,Im H2)`.
The reference angular quadrature integrates the unit round S3 measure
(volume `2 pi^2`), once. The ambient M8 orbit area is not this measure.

`Cstar=1.9180902180140678`, `1/Cstar=0.5213519106704843`. These are retained
center values, not a numerical enclosure. The preceding inverse-C
diagnostic is superseded.

## Evaluated induced metric and active action coefficients

For the radial trial chart, `z_s=v/Cstar`,
`z_s,t=(v_dot-log(Cstar)_dot*v)/Cstar`. With material graph shift,
`U=C*(z_dot+beta)/N`, the induced lapse is `ell=N sqrt(1-U^2)`.
The three scalar weights are

\[
 w_T=R_4^3/\ell,\qquad w_S=\ell R_4,\qquad w_V=\ell R_4^3.
\]

At the actual child-plus center, with unit increasing normal amplitude:

| Coefficient | Base | First normal | Second normal |
|---|---:|---:|---:|
| wT | 1.4055828045268468 | 0.02911012209585093 | 29.50367837437703 |
| wS | 0.6970926057096961 | 0.004812345645039621 | -18.661512408616424 |
| wV | 0.6900235796917099 | 0.01429063488052732 | -20.46638894956415 |

The first weights agree with `(3 a_v wT,a_v wS,3 a_v wV)`, where
`a_v/v=0.006903452433182276`; the measure logarithmic derivative is
`0.020710357299546827`. The source-rate second coefficients are
`(2.863181894833574,-1.419982459419906,-1.4055828045268464)`.
The first-jet parity result does not remove these rate contacts.

The incoming side uses its own lapse and the inherited opposite normal:
weights `(0.8804442014318333,1.1128716370156284,1.1015863092237304)`,
normal first `(-0.018234313993967795,-0.007682656410374992,-0.022814246060312616)`.
Its owned parent sigma1 coefficient `kappa=lambda_geom-1` gives
`S_H,AA/HdaggerH=-0.8126960303227466` and the oriented first/second
coefficients `1.722854554752173`, `19.357533590598578`.

`muon_intrinsic_m4_normal_pullback` implements both a 100-coordinate Jet
and an independent dense metric/inverse/determinant normal two-jet.
The latter retains angular graph gradients, time/space off-diagonal
contacts, shift, and supplied second embedding contacts. The two normal
applications differ by at most `3.552713678800501e-14` at these centers.
That agreement is a numerical diagnostic, not an interval bound.

The whole 100-variable coefficient arrays use the unchanged layout
`(q[37],qdot[37],m[24],s,sdot)`. They populate the existing action rows;
shape does not add an eighth boundary port.

The retained common LR gamma matrices and Higgs SU2/hypercharge
representations are now evaluated through their existing owners.
`gamma0_LR=[[0,I2],[I2,0]]`, Hermitian weak generators are `sigma/2`, and
Higgs hypercharge is `I2/2`. These are computational representations of
the admitted bundle ledger, with no state/covariance selection.

The actual background action uses `jmath=-i sigma`, as recorded by
`muon_owned_connection_application.mechanical_background_action`.
Its physical-orthonormal coefficient is `(lambda_geom-1)/R4` on parent
sigma1 and `lambda_geom/R4` on the specifically owned child sigma0 patch.
The unit-S3 coefficient is therefore `kappa`, before multiplication by
`wS`; inserting another radius would be an error. Explicit SO3 coframe
jets are supported. Fixed body coordinates with identity rotation are a
representation convention for this radial coefficient application.

The implemented action decomposition is

\[
 D_iH=D_{0,i}H+\kappa\tau_iH,\quad\tau_i=R_{id}(-i\sigma_d),
\]
\[
 S_{H,mechanical}=-w_S\sum_i\{2\operatorname{Re}
 (D_{0,i}H)^\dagger\kappa\tau_iH+|\kappa\tau_iH|^2\}.
\]

`sum tau_i^dagger tau_i=3 I2` gives the evaluated AA coefficient above.
The cross term and all internal/shape derivatives are retained. D0
contains the remaining connection and time derivative; no temporal,
Abelian or sourced gauge-fluctuation value was inferred. This Higgs
kinetic contribution does not add the already included classical
mechanical gauge energy to R8 again.

The fixed-family source kernel is also evaluated:

\[
 Y_l=\operatorname{diag}(0.010104825496118923,
 0.0006070420455456903,3.0040743289839823\,10^{-6}).
\]

Its six family off-diagonals are action-derived zeros of the frozen
diagonal T_l. This does not set spin/angular source contractions to zero.
The source routine contracts the actual common-frame fields as
`J_H=bar(e_R) Y_l^dagger L_L`; it supplies matter/frame cross applications.
The matrices alone do not determine the field value of J_H.

## Executable weak equations and common coupled insertion

The scalar backend now evaluates

\[
 S_H=\int\!d\hat\mu\,[ (DH)^\dagger G(DH)
 -w_V\{\lambda_H(H^\dagger H-\nu^2)^2+2\operatorname{Re}H^\dagger J_H\}],
\]
\[
 E_H[\phi]=2\operatorname{Re}\int\!d\hat\mu\,
 [(D\phi)^\dagger G(DH)-w_V\phi^\dagger
 \{2\lambda_H(H^\dagger H-\nu^2)H+J_H\}],
\]

where `G=sqrt|h| h^-1` in the specified `+---` convention and
`dhatmu` contains reference quadrature only. The potential coefficient
lambda_H and nu remain explicit, without a conditional constant vacuum.
The Higgs Jacobian retains

\[
 2\lambda_H[(H^\dagger H-\nu^2)h+2\operatorname{Re}(H^\dagger h)H].
\]

The h/conjugate-h dependence is realified. Gauge, source, metric,
boundary/conormal, supplied constraint and transported-test applications
are executable. A measure/domain Jacobian is assigned to the density
jets or reference quadrature jets once. The fixed-field action two-jet
keeps all DH/J/measure product contacts; an induced unknown h is a
coupled response variable rather than an explicit source.

The metric part of b_H reproduces the handoff's formula

\[
 2\operatorname{Re}\int d\mu_4\,a_v[
 3N^{-2}(D_t\phi)^\dagger D_tH-R_4^{-2}(D_i\phi)^\dagger D_iH
 -3\phi^\dagger\{2\lambda_H(H^\dagger H-\nu^2)H+J_H\}].
\]

The owned Sp1 part additionally differentiates both DH and Dphi at
fixed H/phi. The coupled implementation includes those connection
derivatives in geometric rows, the geometry/H mixed blocks, and the
normal source. Remaining connection/frame/source applications are
explicit additional inputs; their absence is not a physical zero.

The scalar stress cotangent enters the same existing lapse rows. At the
parity-symmetric center, the fixed-covariant part is

\[
 (S_H)_{n_k}=-(-1)^k\int d\hat\mu\,[w_T K_t+w_S K_{S^3}+w_V V_H].
\]

The implemented connection correction belongs to these same rows.
The preceding surface rows `-gamma N rho (-1)^k`, with
`N rho=5.437863897715984`, remain present. Nothing assumes their sum with
active matter and event drive is zero. No extra ADM lapse/shift reaction
is added.

The geometry operator is assembled in temporal weak form:
`F_q=L_q-D_t L_qdot`, `F_m=L_m`. On a supplied test history, the action
residual is the integral of `phi_q L_q+D_t(phi_q) L_qdot+phi_m L_m`.
Its Euler volume pairing subtracts the explicitly oriented endpoint
momentum. The normal source uses both direct and rate blocks and
their momentum contact. Bulk test transport against the off-shell
gradient is kept along with its endpoint lift. The local Hessian is
transformed by the actual temporal test/derivative maps; it is never
inverted as an instantaneous `(q,qdot,m)` KKT matrix.

The common scalar/geometry application returns nonlinear rows, their
real Jacobian and shape source before elimination, including the owned
mechanical background. Same-action sectors are added before reduction.
The source/H mixed transpose is justified for this closed real partial
action on the same tests/trials. A reduced retarded response is not
declared Hermitian.

## Boundary application and the remaining physical solve

At a temporal slice `Pi_H=wT D_tH` in the real `2 Re` pairing.
Endpoint orientation and measure factors enter once. The derivative-form
bulk residual already includes its boundary contact: the displayed
Stokes term is its decomposition and is not appended a second time.

For an actual supplied scalar trace transport T, the implemented event
row is the covector
`epsilon_p Gp Pi_p+epsilon_c T^dagger Gc Pi_c+J_boundary+R_H^dagger Lambda`,
with trace equation `Gamma0_c-T Gamma0_p=0`. The Riesz dual return is
`Gp^-1 T^dagger Gc`, not an unweighted dagger. Shape differentiation
keeps T_s, pairing, flux, boundary-source and fixed-Lambda adjoint
contacts. Volume J_H and event boundary J_boundary remain distinct.

The conditional scalar spatial return law in
`full_field_moving_reset_graph_decision.field_by_field_attachment_rules`
is `B_H=rho_H(G_R)^-1 F_B*`, with its full Lie/vertical lift derivative.
This is the child-to-event return, while the parent-to-child T above
is its inverse on the represented image. The source explicitly labels
this naturality formula conditional. It supplies no evaluated current
intrinsic-H retarded Poisson/trace application. The fermion AE2 U_R and
the old geometric q trace matrix are not substituted for this scalar
spatial map. The scalar trace basis consists of S3 scalar sections times
C2, rather than the spin carrier's eight labels.

The first unevaluated field contraction in the physical scalar residual is

\[
 2\operatorname{Re}\int (R_4^3/N)(D_t\phi)^\dagger D_tH_*.
\]

Its weight, charge/spin representation and mechanical covariant
subapplication have now been implemented and evaluated. Its **actual
primal D_tH_star** must be produced by the coupled sourced scalar/lepton
retarded boundary-value calculation:

\[
 E_H=0,\qquad i\slashed D L_L-Y_lHe_R=0,\qquad
 i\slashed D e_R-Y_l^\dagger H^\dagger L_L=0,
\]

with the applicable intrinsic connection, scalar trace/conormal and
lepton matching applications. The new backend applies these reached
scalar rows and derivatives to supplied fields; no current implementation
yet produces their interacting H/L/e solution on that domain. The saved
geometric extractor gives q/qdot/m and geometric/eta traces. A historical
reset H_SM=Psi=0 policy and homogeneous auxiliary-HS graph do not supply
the requested sourced incoming C1 solution.

The production computation executed both receipt-bound sides, all new
coefficient applications, unreduced weak insertion slots, and nonlinear
Jacobian/source consistency checks. A physical Newton step was not
formed: an actual active scalar/lepton trace/covariant boundary-value
producer has yet to be implemented, so there is no justified physical
load/domain on which to apply that step. This is a remaining action
application, **not a proof of an independently free Higgs datum or a new
theory-definition gap**. This report makes no physical stationarity claim.

Without that coupled solution the physical normal formation section,
complete KKT response, r/i/c and the sourced native Pauli chain are not
numerically instantiated. The evaluated AA term or a formation zero
cannot stand in for impedance. Independently reduced sector impedances
are not added. The separate birth energy and bulk/impedance difference
tests remain required at a solved section.

The final accounting remains `a_mu=frozen selected local+disjoint native
remainder after overlap`, `g_mu=2(1+a_mu)`. The native strong contribution
is counted once in that ledger. Frozen local inputs, earlier milestones,
and the point-valued E1 input guard are unchanged; no complete anomaly
value or enclosure is claimed.

## Claim classes and verification

**DERIVED:** executable nonlinear weak equations and realification;
partial metric/connection/source/constraint/test/boundary derivatives;
same-action geometric/H cross insertion; temporal differential weak
assembly; correctly paired scalar flux return and moving product rule.

**EVALUATED:** both actual geometric M4 weight two-jets, dense normal
metric/measure contacts, real nonlinear coefficient tensor, scalar lapse
coefficient rows, fixed Yukawa and charge/spin matrices, owned Sp1
background and the nonzero scalar AA/cross action coefficients.

**CONTROL_ONLY:** manufactured off-shell fields and polynomial time
histories used to verify nonlinear derivatives, real factors, paired
trace covariance and integration by parts. Their residuals are not
physical stationary residuals.

**UNEVALUATED:** interacting scalar/lepton retarded primal solve,
full stationary KKT base, selected physical mode and total inertia,
impedance and physical native Pauli remainder, final a_mu/g_mu.

**OWNER_DEFINITION_GAP:** none newly established. The remaining producer
has not been executed; absence of its saved output is not a proof of
physical underdetermination.

The exact publication commands, stdout/stderr, exit codes, output hashes,
replay comparison and error scope are in
`artifacts/muon_intrinsic_higgs_weak_action_20261009/verification.json`.
The following verification record is filled from that executed receipt.

The material-response constraint `C_sigma` alone has direct
`R_sigma,H=R_sigma,Hs=0` at fixed independent f/sigma/g coordinates and
fixed normal trial. Its owner ledger depends only on `W_J[f]`, `Z_J[f]`,
sigma and the metric normal. This action-derived zero does not remove
induced f/geometry response or the Higgs charge/Gauss and event constraints.

Executed verification (working directory: the primary worktree):

```powershell
C:\Python314\python.exe scripts/evaluate_muon_intrinsic_higgs_weak_action.py --output artifacts/muon_intrinsic_higgs_weak_action_20261009/run_1
C:\Python314\python.exe scripts/evaluate_muon_intrinsic_higgs_weak_action.py --output artifacts/muon_intrinsic_higgs_weak_action_20261009/run_2
# PYTHONPATH=src supplied in the command environment
C:\Python314\python.exe -m pytest -q tests/test_muon_intrinsic_higgs_weak_action.py tests/test_muon_intrinsic_m4_normal_pullback.py tests/test_muon_coupled_temporal_weak_action.py tests/test_muon_intrinsic_higgs_connection.py
C:\Python314\python.exe tools/audit_bhsm_status.py --format json
C:\Python314\python.exe tools/audit_forbidden_claims.py --format json
C:\Python314\python.exe tools/audit_frozen_prediction_integrity.py --format json
C:\Python314\python.exe tools/verify_precision.py
C:\Python314\python.exe tools/audit_public_readiness.py --format json
```

All commands exited 0. The 69 new focused tests passed in 5.42 s.
The retained regression command

```powershell
$env:PYTHONPATH='src'
C:\Python314\python.exe -m pytest -q tests/test_muon_moving_material_response.py tests/test_muon_moving_geometric_action.py tests/test_muon_birth_candidate_geometry_action.py tests/test_muon_native_kkt_interface_source.py tests/test_muon_birth_fermion_event_kkt_inputs.py tests/test_ae4_branch_relative_support_transition.py
```

returned **135 passed in 13.71 s**. All five repository audits passed;
precision gate: `1.066e-14 <= 1.000e-13`.
Three replay files are byte-identical across run_1/run_2:

| Output | SHA256 |
|---|---|
| control_checks.json | `3d0c6ea1f62f29f6cc7da5b77782274fee340511c7cff216d00c0ad2f11426b9` |
| intrinsic_m4_action_coefficients.json | `dc8e958c8336d1e2a966e06a98d6335a4cc9032eefd88b7e5ad7fc8d4e55fd7c` |
| result.json | `92460fe52eed6f01619e2c09fd2315f3d02ebcf4a96f3431a25cab00fe990f43` |

Source/test hashes and complete command outputs are retained in the
verification receipt. 3,951 inherited tracked files were checked bytewise
without changes; frozen prediction integrity also passed. New coefficient
arrays are stored once, with signed monomial bindings and hash references
to reused geometric arrays.

The independent checks cover nonlinear weak-action differentiation,
conjugate-h response, paired geometry/H cross blocks including Sp1
connection motion, off-shell measure/domain/test transport, normal second
contacts, temporal integration by parts, inherited flux pairing and
frame-invariant Yukawa source contraction. Their manufactured fields are
CONTROL_ONLY. An initial second-order finite-difference first-derivative
check exceeded its diagnostic tolerance by truncation error; a fourth-order
stencil resolved it, without changing the action implementation. This
error history is recorded in verification.json. No continuum, stationary,
response, truncation or soft-limit error bound for a physical anomaly is
established by these checks.
