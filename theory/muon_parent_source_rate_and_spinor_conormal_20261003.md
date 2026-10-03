# Corrected source-time rate and evaluated canonical cut conormal

Starting revision: `c6c4be76609f0f005f2b827a13a16d01f37a5c83`, PR #465,
branch `codex/muon-parent-maxwell-density-review`. Scientific reference:
`524ed90689bd5923c249bba2e699abf627e703cd`. New checkpoint:
`BHSM_MUON_SOURCE_RATE_REPAIR_AND_CANONICAL_CONORMAL_20261003`.

The source-image calculation at the starting revision consumed the cached
placeholder **H=0**, rather than the retained step1222 cut rate. This report
repairs that source-time term without recomputing the contact, Gram, metric
body, angular source transport, or earlier production calculations. It also
evaluates the canonical temporal cut conormal on the corrected connected
source images. No stationary exterior response, full shifted source solve,
native heat contraction, or physical muon anomaly was evaluated.

## Rate reconciliation and provenance

The unchanged historical geometry cache is
`artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz`,
SHA-256 `34ab3500a98197aa3db35f5f3d2e6e7234145e7bd819477e81efcbda3bebd95c`.
Its first `boundary_H` is exactly zero. The old source-image cache is
`artifacts/muon_parent_source_contact_20261003/replay_reference/parent_metric_dirac_actions.npz`,
SHA-256 `1f21ca6d49aa4c6f88f43f64627c7be153fbf267fdc49cc123f0703d7c8b725e`.
The consumed value is independently visible in the saved kernel:

\[
 -2\bigl(\partial_\tau\log(T_b/r)+r_\tau/r\bigr)=H_{\rm used}=0.
\]

The maximum binary64 residual of this inference is
`1.7763568394002505e-15`. The correct existing record is
`artifacts/muon_exterior_face_source_20261002/replay_reference/result.json`:

\[
 H_f=0.08877816767234145,\qquad
 H_f\in[0.08877816713689007,0.08877816820779219].
\]

This is the inherited boundary-proper-time rate
`aether_forward_boundary_radius.proper_time_log_radius_rate`, with
`H=(D_q log R4 . qdot)/N_boundary`, evaluated from the step1222
`endpoint_predictor_center` at order 12. The source frame remains
`T_b=0.22565333970481702`. The prefix NPZ SHA-256 is
`97cc1860028a0f24638823f6ecc4543668f1dcb8de875ca595836318cf1102b0`;
its certificate JSON SHA-256 is
`5ec231ef5d66376be5f39cc95f57b74c9b20bc29f77e5bdbc07d7859f5c8f294`.
The interval is the certificate's `domain.D_tau_log_R4_interval`.
The independent targeted check called this producer once on the retained
state and checked the certificate provenance. No history solve was run.

The affine-logR slope `0.09356155097592357` is a different reconstruction.
It was not substituted. The retained parent metric time slopes and their
errors were not changed or identified with this rate uncertainty.

## Focused additive repair

At fixed remaining inputs the saved split has

\[
 D_5(\Xi_A\chi b)=C_b b+C_{b_\tau}\partial_\tau b,
 \quad f=T_b\chi/r,\quad
 f_\tau=(-H/2-r_\tau/r)f.
\]

For both complete saved n1 and n3 coefficient arrays the executed repair is

\[
 C_{b,\rm new}=C_{b,\rm old}
  -\frac{H_f-H_{\rm used}}2 C_{b_\tau,\rm old},\qquad
 (\log f)_\tau^{\rm new}=(\log f)_\tau^{\rm old}-0.044389083836170726.
\]

| Saved output | Old norm | New norm | Norm of correction |
| --- | ---: | ---: | ---: |
| n1 b coefficient | 119.60684614428256 | 119.61640126545615 | 0.24549897331237316 |
| n3 b coefficient | 86.29064894176535 | 86.29727109445152 | 0.17359398880351434 |

These are finite coefficient-array Frobenius norms, not operator norms,
magnetic moments, Pauli coefficients, or uncertainty estimates for them.
All **17 unaffected arrays** in the old body archive are byte-preserved,
including its compact-probe zero-source body and the b_tau source actions.
The separate parent contact archive and its nodal scalar certificate are
unchanged. Old/new/delta arrays and individual array hashes are saved in
`artifacts/muon_parent_source_rate_20261003/replay_reference`.
The corrected archive SHA-256 is
`a652f6fc4c712fa99e4076d3e701399d2dff24b83bc5e3c38a068913e1e898cc`.

The production function now requires an explicit `cut_rate` record. It
checks the cut identity and source T_b instead of reading the placeholder.
The affected pointwise test now uses the corrected archive and independently
reads the retained rate. Its previous expected expression read the same
placeholder as the calculation, so its earlier pass did not validate this
physical input. The corrected test compares the additive repair with the
pointwise radial/time/angular Dirac expression on the supplied source modes.

## Error scope of the repair

For the stored arrays alone, at fixed other inputs,

\[
 \|\delta_H C_b\|_F\leq
 \frac{\max(|H_- - H_f|,|H_+ - H_f|)}2\|C_{b_\tau}\|_F.
\]

The inherited-H upper bounds are `1.4806879648898538e-9` (n1) and
`1.0470045010691708e-9` (n3). Conservative bounds for the additive repair's
binary64 rounding are respectively less than `5.323e-14` and `3.840e-14`.
The positive sum-of-squares bound checks absence of product underflow and
overflow, uses an IEEE operation-count bound and a 192-bit Arb square root.
Decimal certificate endpoints are compared with the actual binary64 H used.
The exact scope and construction are in `replay_muon_parent_source_rate.py`.

These bounds do not certify interpolation, parent body reconstruction,
quadrature, continuum operator tails, domain matching, physical state,
spectral length, renormalization, or a soft-transfer derivative. Such errors
remain unresolved separately. The older radial contact certificate retains
only its exact binary64 nodal piecewise-affine-model scope.

## New evaluated conormal action

For the implemented canonical M5 metric/common-A summand, the retained
temporal coefficient is `P_tau=i gamma0/nu`. Integration of

\[
 q_{\rm can}(v,u)=\int\nu C r^3(D_5v)^\dagger D_5u\,d\tau\,d\rho\,d\Omega
\]

gives, in the temporal trace pairing of density `2*pi^2 C r^3` per
normalized Haar measure,

\[
 \Gamma_{1,\tau}^{\rm can}u
   =\epsilon_\tau(-i\gamma^0 D_5u).
\]

The lapse cancels between the volume density and P_tau. This is a squared
Dirac-form conormal, distinct from radial/material traction and from the
first-order Dirac current. No Maxwell W or extra action-index factor enters.
At the artificial cut the past core has epsilon=-1 and the future exterior
epsilon=+1. Opposite outward actions have zero residual by construction in
the same local frame; this does not select a new reset lift.

Four actual coefficient actions were evaluated: b and b_tau, for n1 and n3.
All 64 output spin/carrier coordinates, eight sources and four saved input
spin coordinates remain present. The b norms are the corrected norms above;
the b_tau norms are `5.530615910399275` and `3.9107360143815386`.
The saved Clifford trace map has unitarity residual `3.570699413771539e-15`.
An independent test checks the complete rate-change identity

\[
 \Gamma_{1,\rm new}b-\Gamma_{1,\rm old}b
   =-\frac{H_f}{2\nu}\frac{T_b\chi}{r}\Xi_{A,\rm unit}
\]

on the actual n1/n3 arrays. The output is
`conormal_reference/corrected_canonical_trial_conormal.npz`.
It is an evaluated **trial-source cut conormal**, not
`N_out,0(s) U_R g`: no u_s satisfying the exterior weak equation has yet
been constructed. Initial compact-source trace zero does not imply zero
trace after a resolvent or zero N_out.

## First unresolved domain action

The first unevaluated interface action for the coupled exterior solve is
the **normalized wall-spinor trace B54,F on the retained radial trial
sections**, not the temporal principal coefficient. In particular the
needed coefficient actions are

\[
 B_{54,F}[\chi_c(\rho)\phi_{nmk}\otimes e_\alpha],\quad n=1,3,
\]

before connected propagation, for the trial/adjoint directions reached by
the corrected sources. This maps the owned parent H1 spinor sections to
the normalized M4 wall spinor trace (and its completed trace space). The
four input spin coordinates or the child16 test frame do not constitute
that whole space.

The adopted v14.45 collar action already supplies
`u0=N J^(-1/2) sin f_eta`, `A_eta u0=0`, `integral ds J|u0|^2=1`,
and the unit tangential kinetic/Kosmann pullback. In Hilbert-adjoint
notation the needed projection is B54,F=W_eta^dagger, with W_eta the
current-domain isometric collar inclusion and B54,F W_eta=I. The current
radial-chart/carrier realization of W_eta has not been supplied by the
inspected code. In particular the collar coordinate s is not already
identified with the radial nodes rho, and its carrier/spin transport is
not fixed by unit normalization. Writing an integral with arbitrary
rho(s) and U54(s) would introduce an unproved identification. No such
formula or new wall profile was selected here.

Concrete provenance is
`completion/foundational_dirac_spin_glue_v14_45.py`:
`foundational_action_payload` and `zero_mode_pullback_payload`, together
with v15.69 `unified_parent_boundary_functional`, whose single B names
the normalized wall spinor trace. The latter defines a required trace
but accepts no radial sections and generates no current B54 coefficients.
This is an **uninstantiated prescribed identification/pullback**. It is
not a newly free physical parameter; neither its norm nor the local
Dirac body proves the required trace matching. A direct same-action
current-chart identity would suffice instead of constructing an entire
collar kernel or precursor wavefunction.

Its immediate consumer is the M5/M4 interface part of the source-restricted
owned exterior form. If iota_out,F denotes the resulting reset-sewn
exterior inclusion into Dom(q_strat), that form must satisfy

\[
 q_{{\rm out},0}^{\rm owner}(v,u)
  =\langle D_{\rm strat}\iota_{{\rm out},F}v,
              D_{\rm strat}\iota_{{\rm out},F}u\rangle_{\mathcal H},\qquad
 m_{{\rm out},0}(v,u)
  =\langle\iota_{{\rm out},F}v,\iota_{{\rm out},F}u\rangle_{\mathcal H}.
\]

The local cut data evaluate the canonical M5 summand and its temporal
conormal, but not B54,F and its adjoint interface rows. Hence the complete
K_out and M_out action cannot yet be assembled for the coupled solve
without silently equating the local summand with the complete native form.

The AE4 `microscopic_owner_contract` fixes the geometric L2 direct sum
H8/H5+/H5-/H4 and D_strat-adjoint-D_strat quotient.
AE2 `action_definition` supplies the reset trace and opposite conormal
graphs. The current cut producer implements none of the off-stratum
entries of the source-restricted wall inclusion. The effective common-A
connection, adopted v14.45 action, chiral mass block and first-order reset
graph remain resolved at their established scopes.

Its immediate consumer is the exterior zero-trace action
`(K_out+s M_out)u_s`, with Gamma0 u_s=U_R g, then the fermion-family
coupling/retarded-child slots of `assemble_stratified_direct_sum` and the
full shifted source solve. A coupled formulation can use unknown core trace
g; a previously solved physical trace is not required. A scalar product-Dirac
finite-core recurrence does not supply this radial matrix action. The
existing event and Schur routines accept supplied blocks, while the
parametric oracle accepts supplied Hermitian K jets with fixed M=I.
They are not producers of the required current-domain K/M action.

The inherited past-prefix, reset and canonical-stop conditions are retained.
Independent S_Sigma,F=0 does not remove exterior propagation. No endpoint
load, future tail, regularizer, positive radial-sign replacement, heat of
an isolated probe block, or arbitrary spectral length has been introduced.
The attempted continuation stops before a stationary exterior application;
this report does not claim the preferred exterior-response milestone.

## Reproduction and execution record

Two new focused scripts were executed once each, into fresh Downloads run
directories. The old body/contact and earlier symbolic or production
replays were not run. Five affected checks passed: three rate checks, the
corrected pointwise source check, and one conormal check. Reproduction from
the repository, using fresh output directories:

```powershell
python scripts/replay_muon_parent_source_rate.py --output <fresh-repair-directory>
python scripts/replay_muon_corrected_spinor_conormal.py --corrected <fresh-repair-directory>/parent_source_rate_corrected.npz --output <fresh-conormal-directory>
python -m pytest -q tests/test_muon_parent_source_rate.py tests/test_muon_parent_dirac_cut.py::test_same_source_image_against_pointwise_group_directional_derivative tests/test_muon_corrected_spinor_conormal.py
```

Absolute original run receipts, source/input SHA-256 hashes, old/new arrays,
unchanged-array hashes, exact starting revision and working-tree snapshots
are retained in the new artifact directory and standalone Downloads packet.
Cross-platform insignificant last-bit differences are not a physics failure.

Frozen local QED `0.00116550200495813`, calibration-only standard uncertainty
`1.79e-13`, Higgs open bound `(0,3.500331e-9)` and already-combined local
interval `(0.0011655039493,0.0011655109506)` are unchanged. Their original
calibration convention is preserved in `frozen_local.json`. Native ledger
entries remain null where unevaluated; no local term is added again.
There is still no physical a_mu=F2_mu(0) or g_mu=2(1+a_mu) from these actions.

**One next operand:** realize B54,F on the corrected source-reached radial
trial directions by the adopted same-action collar/current-chart matching,
then insert its interface rows into the coupled shifted K/M source solve.
