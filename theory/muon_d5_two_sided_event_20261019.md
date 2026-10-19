# Two-sided D5 event application, 19 October 2026

This continuation from `67c113ea` executes a value-level construction of
the original E1 spatial connection and Higgs bundle correspondence on the
held parent/child backgrounds. It then consumes the resulting field-source
rows in the valid child domain, and transports their constraint curvature
into the normal-stationarity coefficients. It also executes the corrected
parent source on every retained homogeneous coordinate. These are finite
applications of original equations; the full fermionic transmission and
physical formation problem have not yet been solved.

The adopted beams, conditional dressed stationary-past incoming selector,
independent calibration and exact pair statistics are unchanged. Earlier
reports and their hashes remain historical evidence. No identity event
map, vacuum, physical homogeneous state or measured magnetic target has
been selected.

## Value-level connection and Higgs correspondence

On the represented round E1 wall, the metric equation fixes the future
clock differential `kappa = ell_child / ell_parent`, using the **induced**
worldvolume proper clock, and requires `R_child^2-R_parent^2=0`. An angular
isometry has the quaternion form `F_B(q)=a q b`; its right-frame derivative
is represented by `O=Ad(a)`. This does not determine the initial right
translation `b`, an extension through either cap, or the full bundle map.
In particular, the fitted finite child birth curve is not this event map,
and full-cap radial isometry is not imposed as a physical equation.

The original homogeneous weak/central connection rows and Higgs section
row are

\[
 C_A=\left[A_c^{\rm weak}-O^TA_p^{\rm weak}R^T,
                 A_c^Y-O^TA_p^Y\right]=0,
 \qquad C_H=H_c-u_H K H_p=0,\qquad R=\operatorname{Ad}K .
\]

Here `A` is the actual original unit-Tr16 spatial connection, with the
independent wall lift and inherited mechanical connection both present;
`H` is the unnormalized same-action Higgs section in
`[Re H1,Re H2,Im H1,Im H2]` order. Nondegenerate weak curvature justifies
the constant-adjoint reduction for this represented homogeneous wall
component. It does not prove an unrepresented angular/global solution.
The central Higgs factor is a unit factor in the Higgs representation,
not a selected full-SM hypercharge lift.

The previous SVD initializers solved the spatial rows accurately but left
Higgs value residuals. The new application solves all 12 real connection
and four real Higgs rows jointly, using

\[
 O=O_0 e^{\Omega_b},\quad R=e^{\Omega_g}R_0,
 \quad U_H=e^{i\theta_H}e^{-i\omega_g\cdot\sigma/2}U_{H,0}.
\]

Six independent original rows determine six pivot coordinates; the
relative `gauge_z=0` coordinate is a numerical initializer convention.
All 16 rows and all seven tangent columns are retained. The selected
pivot has condition number about `5.57`; one Newton update gives:

| Initial orientation family | Before connection max | Before Higgs max | After all16 max |
| --- | ---: | ---: | ---: |
| 2 | 2.39252e-11 | 1.03704e-7 | 3.16023e-16 |
| 3 | 2.83216e-12 | 1.22761e-8 | 3.43901e-16 |

Both families remain explicit, with the backgrounds held fixed. These
maps were obtained from metric/connection/Higgs equations, not by fitting
a fermionic trace. The small seventh singular value is approximately
`4.46e-11`; the reconstructed free tangent leaves a full-row coefficient
about `9.45e-11`. This ill-conditioned direction is **not** declared zero
or proved gauge. The earlier two central-incompatible families, with
value residual about `2.46e-4`, are retained as historical nonpasses.
Initial right translation, spin-cover sign, the full central/strong
factors, normal transport and physical Cauchy density identification
remain independent obligations.

The owners are
[joint value equations](../src/bhsm/interface/muon_d5_joint_connection_higgs_value.py),
[spatial connection equations](../src/bhsm/interface/muon_d5_spatial_bundle_application.py)
and [original wall incidence](../src/bhsm/interface/muon_d5_event_bundle_incidence.py).

## Executed two-sided source and valid child chart

The old prescribed Xi, born-parent and anchored-reference sources are
retained. The new proper-normal additions use the actual coefficient
`a`, never a unit normal profile:

\[
 \delta q_{98}=a\psi,\qquad
 \delta q_{99}=\dot a\psi+a\dot\psi,\qquad
 \psi(t)=\psi_{E1}+t\nu .
\]

The saved E1 displacement-source coefficients are
`psi_parent=-0.47802575718819384` and
`psi_child=17.98966013686085`. They are provisional response coefficients,
not a selected mechanical formation mode. Both normal-rate coordinates
remain free; the child application explicitly evaluates its additional
`nu_child` column. Additional normal-induced born/reference variations
remain held independent slots; their existing nonzero prescribed jets
have not been deleted.

The child application reuses the finite birth curve, valid endpoints,
normalization and inverse chart. It executes only the new variational
shoots. The moving evaluation enters once:

\[
 \delta L_{\rm chart}=\delta L\big|_{t,r}
       +(\partial_tL)\delta t+(\partial_rL)\delta r,
 \qquad
 \delta\mu_{\rm chart}=\delta\mu\big|_{t,r}
       +\mu_t\delta t+\mu_r\delta r,
\]

followed by the chart Jacobian/density derivative. The boundary-fitted
connection retains the equivalent
`partial_s|q = partial_s|vartheta - q_birth'(s) partial_vartheta`
term throughout. Only child times from `0` to `2.00942e-6` are evaluated.
The two new child normal columns have original birth-source residuals
at most `4.63222e-23`, point-source residuals at most `1.32349e-23`, and
inverse-source residual at most `2.22045e-16`. Cached value identity is
`5.87748e-39`; original principal-source recovery is `2.84218e-14`.
These numbers test finite coefficient/chart equations, not a solved
child D5 section. Saved finite radial-difference, history/domain and
truncation errors remain separate.

At each new joint map the full16 boundary Jacobi source rows determine
12 original child wall-gauge and four intrinsic-Higgs source pivots.
Their pre-correction max is `4.63532e-6`; the reconstructed component
source row is zero in the recorded arithmetic. All seven independent
base/gauge/Higgs-phase source columns are retained. Relative to the
older map applications the newly required raw source increments are
only `4.41204e-13` and `5.22281e-14`, but they are recomputed and consumed
because the physical correspondence changed.

The additional raw spatial gauge coordinates `168:180` and intrinsic
Higgs coordinates `260:264` are extended constantly through the finite
child cell as a **provisional source extension**. Its extra raw time
derivative is explicitly held zero; the physical field evolution is not
thereby solved. Pure gauge source additions have zero direct geometry,
density and chart variation, so the completed birth calculation is
reused. The child value operator is unchanged. Higgs enters its existing
intrinsic seam application once, not as an extra bulk D5 mass.

The local temporal bundle equation and its supplied-direction derivative
are also executed:

\[
 \dot U_H=-A_{c0}U_H+\kappa U_H A_{p0},
\]
\[
 \delta\dot U_H=-\delta A_{c0}U_H-A_{c0}\delta U_H
 +\delta\kappa U_H A_{p0}+\kappa\delta U_H A_{p0}
 +\kappa U_H\delta A_{p0}.
\]

Both reconstructed local matrix rows are zero in the saved arithmetic.
This is an E1 jet; it does not integrate into unavailable parent future
or child past or fix a global bundle phase. The updated saved temporal
source is the particular `delta U_H=0` direction. The generic equation
retains every `delta U_H` placement, but the seven free-map temporal
source matrices have not been materialized at the final maps. This
particular jet is not a complete physical derivative.

The final-map child source append evaluates the small **new** wall-gauge
increment with the original callback: its operator-source component max
is `1.36025e-11`. It reuses the completed normal/rate chart and value
operator. The additional intrinsic-Higgs and Higgs-phase columns have
exactly zero bulk D5 source because the original operator places that
Higgs interaction in the seam; this is not zero physical Higgs response.
The once-only seam source below supplies its actual nonzero application.

The independent total-event-time field-response ports are
`[U_H H_parent,t, -H_child,t]`. At the new maps they are recomputed from
the same original time gradients, rather than copied from the historical
map. Their parent columns change by `6.01417e-14` and `7.11935e-15`;
the child columns are bitwise unchanged. Both total time variations
remain free and are distinct from the already consumed moving child
chart source.

See [child normal chart](../src/bhsm/interface/muon_d5_child_same_direction_application.py),
[child field source](../src/bhsm/interface/muon_d5_child_spatial_source_application.py),
[updated16 source application](../src/bhsm/interface/muon_d5_joint_map_source_application.py)
and [Higgs/time equations](../src/bhsm/interface/muon_d5_higgs_temporal_bundle_application.py).

## Once-only intrinsic Higgs seam source

At both final map families the new child intrinsic-Higgs source is
consumed by the original profile-separated LR and RL seam equations,

\[
 J\,\delta N\,\Gamma=\widehat C\,\rho\,\delta M\,B\Gamma,
 \qquad \delta\overline S\,\Gamma
       =-\Gamma_0\widehat C\,\rho\,\delta M\,B\Gamma.
\]

The exact factor recovery has original `J J^{-1} Chat-Chat` max
`2.08167e-17`; the held seam value identity is at most `6.93914e-18`.
The new lepton coefficient operator has spectral 2-norm
`5.53294e-9`, against background coefficient norm `0.00683116`.
The new Higgs coefficient applied to the saved seed traces has component
max `5.49493e-9`; on the saved plus/minus homogeneous families it reaches
`2.87531e-10` and `6.47463e-10`. The independently computed corrected
parent-state product reaches `0.0146950` on plus homogeneous columns.
The reconstructed original weak source identity is at most `1.14387e-25`.
These are nonzero finite coefficient contractions, not physical
transmission residuals or a reconstructed child section.

The consumed lepton36 carrier consists of all Spin4 particle L6/7 and
conjugate e_c14 entries across three families; it is distinct from the
retained particle/antiparticle36 response carrier. Its phase factors are
integer powers `u_H^-1` on L and `u_H^-2` on e_R. This avoids choosing a
fractional full-SM phase lift. The seam vertex annihilates the other
represented carrier exactly, but that does **not** establish closure of
the full event maps on this lepton block. The unrestricted physical
application must retain the ordered factors

\[
 L_{18\times384}\,D_c^{-1}\,K_{\rm full}\,D_p\,q_{384}.
\]

Both event density/normal maps and their derivatives are unassigned.
The full left kernels and original384 trace/source coefficients are
saved for that application. The numerical `L K q` and known state/map
products are explicitly **formal unnormalized coefficient contractions**;
they do not set either `D` map to identity. The lepton36 restriction is
conditional on subsequently proving that both complete `D` maps preserve
it. Independent LR/RL profile factors
`1/(u_L_plus*u_R_minus)` and `1/(u_L_minus*u_R_plus)` remain unevaluated,
as do total pullback, normal/frame/density and profile derivatives.

The reported coefficient ranks use an absolute singular-value threshold
`1e-12`: the new direction operator has numerical rank six; particular
trace matrices have ranks zero, two, four or six. These are not exact
algebraic ranks, physical mode counts or permission to discard small
columns. Every column remains saved. This application adds no bulk
Higgs mass and makes no second local Maxwell/Higgs subtraction. See
[seam source owner](../src/bhsm/interface/muon_d5_child_higgs_seam_source_application.py)
and its `RANK_INTERPRETATION.json` receipt.

## Constraint curvature in the actual normal-stationarity rows

The evaluated 13-row constraint is radius squared plus the full 12 spatial
connection rows. Its declared 546-coordinate chart contains five
independent geometry100 streams (parent, child, born parent, reference
parent, reference child), parent20/child20 wall one-forms, and six
base/gauge rotation coordinates. Equal array lengths do not identify
these streams. The literal child12 field pivot and independent radius
covector give rank 13 and an explicitly retained 533-dimensional kernel.
This is a constraint kernel, not a proved gauge quotient or a chosen
physical state. The seventh Higgs phase is also retained in the updated
source; it acts trivially only on these13 rows.

Let `B` be the four actual mechanical normal/normal-rate coordinate
columns. The executed contact is

\[
 C_\psi^T\lambda=B^T C_z^T\lambda,\qquad
 \delta(C_\psi^T\lambda)=
 \left[B^T C_{zz}\Xi+(\delta B)^TC_z\right]\lambda
      +C_\psi^T\delta\lambda .
\]

Thus the `sum lambda D2C` curvature and the derivative of the normal
frame are both present; neither multiplier slot has been assigned.
At the new maps the constraint value maxima are `3.16023e-16` and
`3.43901e-16`; the supplied source rows are at most `3.99681e-15`.
The curvature, frame and total multiplier-source coefficient maxima
are respectively `46.6614`, `0.204821` and `46.5955`. The explicit kernel
row max is `2.65126e-16`; all seven free map-source rows are at most
`6.16298e-33`. No normal mode follows from these finite rank checks.
The new Higgs/time constraint Hessians remain uncomputed; they are not
replaced by this 13-row Hessian.

The actual Higgs first derivative is then appended to the 13 rows in a
555-coordinate fixed-E1 chart: the previous546 coordinates plus parent
Higgs4, child Higgs4 and Higgs phase1. The resulting 17-row matrix retains
all parent/child and map-derivative placements. Its literal radius,
child spatial12 and child Higgs4 pivots have rank 17 and condition number
`1.85628`; all 538 free coordinate columns remain explicit. Its kernel
row max is `2.65126e-16`, source max `3.99681e-15`, and value max is the
same `3.16023e-16`/`3.43901e-16`. Its direct `h` constraint rank is zero
by the displayed field equations. All 3660 independent `h` and
`delta h` coordinates remain retained. The rank is at fixed E1; it is
not the complete physical constraint or formation rank. See the
[combined fixed-E1 rows](../src/bhsm/interface/muon_d5_two_sided_constraint_rows.py).

The original known weak geometry action is evaluated at the same E1
background on each history with its pinned 48-point cap rule. The known
sector is geometry/FR/moving GHY-Hayward with the old reference Casimir
absent. The recorded local Maxwell/Higgs functional is not inserted or
subtracted again. Area is returned separately per unassigned gamma.
Its exact raw gradient/Hessian give both weak state and independent
phase-rate placements; the normal coefficient derivatives are retained.
For source columns `[old Xi, normal Xi, normal+field Xi]`, the known
weak contacts are

| History, mechanical test slot | Old Xi | Normal Xi | Normal+field Xi |
| --- | ---: | ---: | ---: |
| Parent, psi | 4.88320 | -9.64443 | -9.64443 |
| Parent, coordinate psi-dot | 9.80929 | 13.9658 | 13.9658 |
| Child, psi | 23.3217 | 221.239 | 221.239 |
| Child, coordinate psi-dot | 8.61452 | -73.9300 | -73.9300 |

The equality of the last two columns follows from this bare sector's
absence of independent A/H arguments and the new sources' exactly zero
geometry components. It says nothing about unknown native/state field
dependence. After the joint map change, the saved geometry two-jets and
action contacts are reused bitwise; only map-dependent constraint
coefficients are transported. There are zero additional cap-action or
geometry-jet evaluations in that append.

The four known weak source rows are assembled affinely with columns
`[1, gamma, delta_gamma, lambda13, delta_lambda13]`:
`b_geometry + gamma*b_area_source + delta_gamma*b_area_value`
plus the two multiplier contacts displayed above. This executes the
available coefficient assembly without solving for gamma, multipliers,
or an unknown native load. The additional Higgs/time multiplier Hessians,
physical outer/time-Euler and full action terms remain explicit unknowns.

These are weak Lagrangian coefficients, not a completed Euler operator,
full constrained formation Hessian, restoring force or physical inertia.
The complete stationarity equation still requires the same-domain
native/reference/state/phase/outer action and all constraints. No old
52-row factorization is transferred to that interacting problem. In the
original signed-action chart its bulk Jacobi rows retain
`L_xx delta x + L_xv delta xdot + L_xy delta y`
minus `D_t(L_vx delta x + L_vv delta xdot + L_vy delta y)`, together with
the algebraic, endpoint, interface and causal outer rows. The constraint
reaction above augments these rows; it does not replace them.

The existing formation prescription remains

\[
 H_{\rm form}\psi=\kappa_{\rm form}M_\Sigma\psi,\qquad
 H_{\rm form}=H_{\rm bulk,constrained}
       +\sum_s\gamma_sJ_{\Sigma_s}-H_{\rm event,drive}.
\]

Its candidate is the first regular future simple oriented zero of the
lowest constrained eigenvalue, with the required nonlinear constrained
branch. That crossing and branch have not been executed here. Cauchy
normalization cannot select them. See the
[retained formation equations](muon_formed_event_domain_application_20261019.md),
[constraint two-jet](../src/bhsm/interface/muon_d5_event_constraint_twojet.py)
and [affected map append](../src/bhsm/interface/muon_d5_event_constraint_twojet_append.py).

## Full parent homogeneous source and retained errors

Every original homogeneous coordinate remains represented: 366 per
time node, 3660 over the saved ten-node representation. For each retained
carrier block, the newly executed source equation is

\[
 L H_\Xi=-L_\Xi H_{\rm saved},\qquad H_\Xi|_{\rm wall}=0,
 \quad LZ=0,\quad Z|_{\rm wall}=I.
\]

Zero fundamental source data define a derivative operator, not physical
boundary data. With actual original wall maps
`W=P a+Q h`, the consumed family is

\[
 V=H_{\rm saved}W,\qquad
 V_\Xi=H_\Xi W+Z W_\Xi,
\quad W_\Xi=P_\Xi a+P\delta a+Q_\Xi h+Q\delta h .
\]

The new source initial-data propagator `Z` is used explicitly. The
finite source solve is **not** the exact derivative of the old discrete
value algorithm; old value defects remain. Original sparse `Q/Q_Xi`
columns, every `h` and independent `delta h` are retained. The free parent
normal-rate source is not included in this particular corrected-Xi
source and remains another independent operand.

Checks after the actual `Q/Q_Xi` application, over both eta collars and
particle/conjugate blocks, give:

| Independent probe set | Value max | Corrected source max | Independent delta-h source max |
| --- | ---: | ---: | ---: |
| Nine independent points | 2.97033e-4 | 1.14690e-2 | 2.97034e-4 |
| Six original times, independent radii | 5.26136e-4 | 2.06661e-2 | 5.26183e-4 |

These are maxima of absolute original strong **matrix components** on
the stated finite sparse/cardinal inputs. They are active nonpasses,
not preparation/Cauchy operator norms, physical-state residuals or
continuum error bounds. In particular,

\[
 L V=R_{\rm part}a+R_h h
\]

is an unevaluated physical combination until its actual amplitudes and
outer/formation data are determined. A bound needs their norms and the
appropriate induced operator bounds, including source, frame and
moving-evaluation errors. Matching implementations or small collar
arithmetic cannot supply that bound. The two eta collars belong to
each history, not to the two beams or successive histories.

See [corrected full family](../src/bhsm/interface/muon_d5_corrected_homogeneous_source.py).

## Remaining physical equations and accounting

The required fermion relation remains

\[
 \Gamma_{0,c}-U_R(\Gamma_{0,p}\circ F_B)=0,
\]

with its complete Jacobi row

\[
 \delta\Gamma_{0,c}-\delta U_R(\Gamma_{0,p}\circ F_B)
 -U_R\left[(\delta\Gamma_{0,p})\circ F_B
 +(d\Gamma_{0,p}\circ F_B)\delta F_B\right]=0 .
\]

The saved parent trace and gradients are evaluated coefficients. The
initial right translation, complete bundle/normal/density transport,
actual child section and physical outer conditions are not yet fixed;
therefore this full matching residual and its effect on a solved
formation mode are not reported. The moving child point must enter the
total pullback exactly once. Fermionic localization `u_eta`, complement
`chi` and mechanical deformation `psi` remain distinct. Independent
left/right normal profiles and their normalization integrals remain
unresolved; the same physical `g` still underlies the separate
`a_R,a_LR,a_RL` slots.

The full constrained formation system must retain both state and vertex
derivatives, endpoints, source momentum, moving geometry/domain and
normalization. The already removed local Maxwell/Higgs functional stays
removed once. Complementary native contributions, phase/boundary and
matched inherited-state differences, full local overlap, physical-unit
and implicit cutoff equations remain explicit. Unknown loads and their
field derivatives are not zero. No residual is used to infer a native
load, no 20 state contractions are fitted, and no occupation is inferred
from `C_plus`.

The unchanged physical admission criterion is `2e-10` in the original
specified physical norms. The finite residuals above do not execute
that test. Full derivative admission, coupled correction, fresh original
Maxwell/all-226-row checks, normalized magnetic readout, native completion,
overlap subtraction and uncertainty remain unexecuted here. No magnetic
moment, decay-based change of moment or physical closure is claimed.

## Reproduction and next operand

The versioned numerical groups are `CHILD_SAME_DIRECTION_v1`,
`JOINT_CONNECTION_HIGGS_v1`, `JOINT_MAP_SOURCE_v1`,
`CONSTRAINT_TWOJET_v1`, `CONSTRAINT_TWOJET_APPEND_v1`,
`CHILD_JOINT_SOURCE_v1`, `CHILD_HIGGS_SEAM_v1`,
`TWO_SIDED_ROWS_v2`, `PARENT_H_SOURCE_v1` and
`PARENT_H_CONSUMER_v1`. Their receipts pin exact
inputs, source owners and numerical hashes; superseded map/source groups
are preserved. Focused tests exercise the source/chart placements,
original connection/Higgs rows and exact constraint-jet transport.

The immutable applications and exact repository input bindings are in
[the versioned cores](../artifacts/muon_d5_two_sided_event_20261019/core).
The consumer only reassembles the new rows; it does not rerun the saved
source/birth/native/value applications:

```powershell
python scripts/evaluate_muon_d5_two_sided_event.py --output artifacts/muon_d5_two_sided_event_20261019/run_1
python scripts/evaluate_muon_d5_two_sided_event.py --output artifacts/muon_d5_two_sided_event_20261019/run_2
python scripts/verify_muon_d5_two_sided_event.py artifacts/muon_d5_two_sided_event_20261019/run_1 artifacts/muon_d5_two_sided_event_20261019/run_2
```

Both materializations are byte identical. The array SHA256 is
`6dfecf6b8ae594fb303352f020eac60dc5c2039769b4e9d3601ca6a7f649258c`;
all rebuilt arrays equal the executed v2 checkpoint exactly. The
[verification receipt](../artifacts/muon_d5_two_sided_event_20261019/checks/deterministic_materialization.json)
does not certify physical closure.

The exact 46-file focused/affected pytest selection, source hashes,
environment, exit status and output are recorded in the
[checks directory](../artifacts/muon_d5_two_sided_event_20261019/checks).
The first run passed all 202 test assertions, but its session guard
rejected concurrent publication metadata writes and restored those
metadata. That receipt is preserved; the isolated v2 run is the
publication test. The required publication commands are:

```powershell
python tools/audit_bhsm_status.py
python tools/audit_forbidden_claims.py
python tools/audit_frozen_prediction_integrity.py
python tools/verify_precision.py
python tools/audit_public_readiness.py --format json
```

Three large new NPZ inputs are retained individually, with exact lengths
and hashes in
[the retention ledger](../data/retained_large_research_artifacts.json):
the corrected homogeneous source (40,141,817 bytes), its independent
original differential rows (16,030,466 bytes), and the consumed sparse
full-h rows (48,119,113 bytes). They preserve the evaluated response and
nonpasses without replaying the solves or dropping high-error columns.
No general size exemption or hygiene threshold is changed.

`NEXT_OPERAND`: consume the new two-sided child operator/seam sources,
full parent `Q/Q_Xi` family and derived connection/Higgs/time map
coefficients in the actual fermion event/outer equations. Determine
their remaining physical boundary variables jointly with formation,
retaining full `h/delta h`, free map/normal-rate and inherited source
columns. Carry the measured finite source/value defects into that
consumed combination before selecting further refinement.
