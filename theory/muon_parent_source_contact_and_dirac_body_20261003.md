# Evaluated parent source contact and canonical Dirac body

Continuation of PR #465 at `0ec64ea11cd52661b567c2efaf96ebedefc41e4f`;
scientific reference `524ed90689bd5923c249bba2e699abf627e703cd`.
Branch: `codex/muon-parent-maxwell-density-review`. The primary checkout and
its newer unrelated work were preserved. Publication provenance and the
complete new diff are in this packet's receipt. This calculation uses the
adopted effective common-A prescription without precursor reconstruction.

**Result:** actual parent tangential source actions, an unreduced mixed
source contact, the canonical metric/common-A Dirac body, and its actions
on the same connected source images were evaluated. The requested native
heat-weighted contact `-Tr(Q_strat A_ZA)` was **not** evaluated. Neither
`f_Z,A`, an exterior forcing return, nor a physical anomaly follows from
these local body data. No local contribution was refitted or accumulated.

## New numerical object

The source coordinate is **b**, with beta=T_b b and A_Q=sqrt(2) beta.
The saved coefficients already represent delta_b Omega=T_b Y_A(-iQ)
in the transported carrier. We use the saved anti-Hermitian generators
and `i gamma_LR^a Omega_a/r` directly. There is no additional sqrt(2),
action-index 2/3, contact fraction, mode count, family count, or charge
trace inserted into the vertex.

On the actual C2 step1222 past cut, let L be an auxiliary trace lifting:
zero through radial node8, smoothly one from node16 onward. Let z=chi be
the H1 hat supported on nodes24..40, peaking at node32. L is one on that
support. These are computational representations, not a new physical
source continuation or stationary parent extension. The continued photon
kernel is the existing transported n1+n3 source; no time profile b(tau)
is chosen. The test is the central hypercharge component of the supplied
mode, with v_rho=v_tau=0. Its material trace is zero. Its covariant angular
divergence vanishes because the saved modes are coexact and [omega,Y]=0;
the actual gradient residual is `5.063396036227354e-15`.

The parent probe columns are chi(rho) times the 64 Spin4 x SM16 constant
angular coordinates, for one sheet and one family. They are independent
local field coordinates, not the child16 functions, a precursor frame,
Cauchy state, pole, LSZ states, or the whole parent zero-trace space.
Compact support proves local first-order/material admissibility. Temporal
domain closure, the full constraint quotient and the cross-stratum source
jets remain unevaluated; local zeroth order does not prove their absence.

At fixed metric/section the minimal insertion is affine, so its **local**
Xi_ZA is zero and its form contact is

\[
K_{ZA}^{\rm contact}=\Xi_Z^\dagger\Xi_A+\Xi_A^\dagger\Xi_Z,
\quad \Xi_A=(T_bL/r)i\gamma^a S_{A,a}^{\sigma1},
\quad \Xi_Z=(T_bz/r)i\gamma^aY_{B,a}(-iY).
\]

All n1+n3 output coefficients and all 64 spin/carrier rows of Xi_A are
stored. The n3 norm is `6.5319726474218065`; it is not an error estimate.
For this particular central test, angular orthogonality makes its n1/n3
cross zero in the **unweighted** contact. It does not discard n3 from
propagation, the paired heat derivative or the full trace.

The canonical geometric five-dimensional action density per coordinate
time is `2 pi^2 nu C r^3 d_rho`. It is distinct from the Cauchy/CAR
measure, which omits nu. Maxwell's W is not a new Dirac vertex weight.
Under the declared piecewise-affine nodal interpolation,

\[
K_{ZA}^{\rm cut}=\alpha K_{ZA}^{\rm unit},\quad
\alpha=2\pi^2T_b^2\int\nu Crz\chi^2\,d\rho
=0.05931294893274136785376782985278495104\ldots,
\]

\[
M_{\rm probe}^{\rm cut}=0.75907752540381811666537952591600490090\ldots I_{64}.
\]

The radial integrals are evaluated as exact rational polynomials in the
binary64 input nodes, then enclosed with 256-bit Arb pi. Four-point
quadrature agrees independently (contact residual zero in binary64;
Gram residual `6.938893903907228e-18`). The Arb enclosure is rigorous
**only for that nodal interpolation model**. It does not certify the
history, continuum interpolation, temporal integration, physical source
extension or native truncation. The certificates give outward float
radius bounds; the raw stage1 radius floats were rounded to nearest and
are superseded for this purpose. Their original Arb interval strings and
all original arrays remain unchanged.

With the established Haar normalization and primitive Tr16(Y^2)=10/3,
the algebraic identity is

\[
\operatorname{tr}_{64}K_{ZA}^{\rm unit}=(80/3)I_8,
\quad \operatorname{tr}_{64}K_{ZA}^{\rm cut}
=1.58167863820643647610047546274093202777\ldots I_8.
\]

The full matrix is retained; its binary64 trace-identity residual is
`6.531584628124504e-14`. This spin/carrier trace is not a graded native
trace or Pauli coefficient. The matrix contractions have unvalidated
roundoff, distinct from the rigorous scalar nodal enclosure.

## First zero-source body action, also evaluated

The actual coframe is theta0=nu d_tau, theta4=C(d_rho+zeta d_tau),
thetaa=r thetaR_a. Signature is +----; gamma4=i gamma5 points along
outward rho. The right coframe has dtheta1=+2 theta2 wedge theta3.
Cartan's equation, with the inherited Lorentz sign, gives

\[
h_0={[(\partial_\tau-\zeta\partial_\rho)\log(Cr^3)
-\partial_\rho\zeta]}/{(2\nu)},\quad
h_4={\partial_\rho\log(\nu r^3)}/{(2C)},
\]

\[
C_{\rm spin}=i\gamma^0h_0+i\gamma^4h_4
-\frac{3i}{2r}\gamma^1\gamma^2\gamma^3.
\]

The sigma1 common-A coefficient is `(lambda-1)/r`, evaluated in its
regular expression `-B/(A sqrt(A^2+B^2))`. Its generator is
jmath_a=2 sqrt(2) Hweak_a=-i sigma_weak,a, not another action-index
normalization. The implemented canonical bulk summand is

\[
D_{5,0}^{\rm metric,A}=\frac{i\gamma^0}{\nu}
(\partial_\tau-\zeta\partial_\rho)+\frac{i\gamma^4}{C}\partial_\rho
 +\frac{i\gamma^a}{r}E_a+C_{\rm spin}
 +i\gamma^a\frac{\lambda-1}{r}\jmath_a.
\]

The active harmonic coefficient action E_a=+2iJ_a matches the saved curl
convention. The sigma1 background is angularly constant; this representation
preserves n1/n3. No extra angular projection is taken. Source image actions
retain its angular/radial derivatives and the moving kernel
T_b'=-H T_b/2. They are saved as separate b and partial_tau b coefficients,
so no constant physical time continuation is assumed.

These new actions are evaluated at 64 interior radial Gauss points. Metric
time derivatives use the first inherited forward time cell; radial
coefficients use the retained affine cells. D5 is applied to all 64 compact
probes and, on its source image, four spin coordinates of one charged weak
doublet coordinate, retaining every 64-component output. This smaller set
is an evaluated subset, not an exhaustive physical source trace.

The probe K0 and M0 are both saved. `||K0_cut||=4639.038988497706` and
the n1/n3 source-image body action norms are `119.60684614428256` /
`86.29064894176535`. These are intermediate norms, not anomaly bounds.
K0 is Hermitian to recorded binary64 precision; a separate Koszul
connection contraction agrees with C_spin on actual input points. The
parent Clifford residual is `7.953175920042868e-15`; M0 agrees with the
exact nodal Gram to `1.1102230246251565e-16`.

The K0 density is rational, so the earlier polynomial quadrature theorem
does not certify its quadrature. History, parent-H versus affine-logR,
domain/complement and continuum errors remain separate and unenclosed.
Owned additional zero-order/interface contributions are **unevaluated**,
not zero. The localized v14.45 eta normal operator is not substituted into
the whole bulk; its normalized pullback remains supplementary provenance.

## Exact next action required for the native pencil

The inspected `v15.79._dirac_hessian` and `v15.81.dirac_hessian_at_state`
are velocity/lapse/shift **Euler--Dirac constraint Hessians**, not this
fermion D5 or D_strat^dagger D_strat. Their geometry source is not a photon
source. `frechet_second_response`, `generalized_e1_coordinate_jet` and
the archived `HeatPencil` accept supplied operators/jets; they do not
produce the current stratified pencil. The new code supplies actual local
actions, while the full pencil/domain is still not a supplied numerical
input. The chiral mass block and reset first-order domain remain resolved
at their established structural scope.

The first source-connected **domain action** still needed is the exterior
spinor conormal response, on traces generated by the shifted source image:

\[
N_{{\rm out},0}(s)U_Rg=\Gamma_1^{\rm owner}u_s,\qquad
\Gamma_0u_s=U_Rg,
\]

\[
q_{{\rm out},0}^{\rm owner}(v,u_s)+s\langle v,u_s\rangle=0
\quad\forall v:\Gamma_0v=0,\quad s>0.
\]

Its input is the source-reached spinor/family trace in the inherited
H^(1/2) trace space; its output is the exterior-outward conormal in its
H^(-1/2) dual. Use the full trace/traction relation if a graph chart fails.
The core consumes it with opposite outward sign:

\[
\Gamma_{1,e}u_e+
U_R^\dagger N_{{\rm out},0}(s)U_R\Gamma_{0,e}u_e=0.
\]

A compact source initially has zero trace, but its resolvent image need
not. Thus zero material trace of these probes does not justify zero
exterior response. `action_extension_global_spin_reset_ae2.action_definition`
already fixes S_Sigma,F=0 and the transmission graph; it supplies no
adjustable independent spinor contact. That settled zero does not set N_out
to zero. The remaining map is an uncomputed prescribed operator/domain
response, not an unselected new boundary parameter or a precursor problem.

Producer: the same-owner exterior spinor weak form, geometric inner
product and conormal, with the existing reset/past-prefix/canonical-stop
trace conditions. Concrete consumers are the fermion-family coupling
and child response slots of `assemble_stratified_direct_sum`, then the
full shifted-resolvent source application used by `HeatPencil`. The
supplied-block `retarded_child_schur_complement` implements algebra, not
this producer. Only this source-reached trace response is needed next;
an entire kernel/history reconstruction is not required.

The new Lorentz body retains a real characteristic cone. Positive finite
Gram data do not establish its identity with the native stratified heat
realization. The owned form in this weak equation must be used; no Wick
rotation, positive radial-sign replacement or unproved heat matching is
introduced. The inherited step1222 past prefix and future canonical stop
are unchanged; no endpoint load or future tail is added.

Once that response is materialized, use the **full** connected pencil:

\[
A=M^{-1}K,\quad A_{ZA}=M^{-1}(K_{ZA}-M_{ZA}A-M_ZA_A-M_AA_Z),
\]

\[
c^D_{ZA}=-\operatorname{Tr}\{DQ[A_A]A_Z+Q A_{ZA}\},
\quad Q=\tfrac12A^{-1}e^{-\ell_*^2A}.
\]

No heat of the finite cut block was taken. Native ell_* remains its
impedance/surface functional, unevaluated; no arbitrary number is
inserted. Grading, gauge/BRST, length, pairing, domain, completion,
renormalization and strong-within-native terms remain null in the ledger.
The contact and paired derivative must be completed before naming f_Z,A.

## Evidence and replay

New files: `muon_parent_source_contact.py`, two focused replay scripts,
and two targeted test files. Arithmetic heat machinery is reusable;
the supplied muon source, parent geometry, computational probes and
future Pauli projection are realization/readout data. No universal
framework was built, and no muon state or soft-transfer assumptions
were added to a universal module.

The seven **new** tests passed: four new source/sign/contact/domain/integral
checks and three new Cartan/body/pointwise representation checks. The last
check initially failed because its harness read a closed NPZ; that harness
was corrected and only that check was rerun. No operator was recalculated.
They are distinct from the old
precursor checks and earlier normalization/covariance/adjoint replays,
none of which was repeated. Stage1 and stage2 ran once; scalar-only
certificate conversion is saved separately. Zero native heat evaluations,
physical transfer directions or causal exterior returns were executed.

`artifacts/muon_parent_source_contact_20261003` preserves the actual arrays,
stage-specific source identities, input SHA-256 hashes, exact rational
integrals, equations, residuals, targeted validation receipt and checkpoint.
The Downloads handoff includes both original runs, source snapshots and
the publication diff. Stage1/2 module snapshots match the code identities
at their respective calculations; the additive body and outward-radius
changes are recorded without rerunning old calculations.

Reproduce only this new calculation in unused output directories:

```powershell
python scripts/replay_muon_parent_source_contact.py --output <new-contact-directory>
python scripts/replay_muon_parent_dirac_cut.py --contact <new-contact-directory>/parent_source_contact.npz --output <new-body-directory>
python -m pytest -q tests/test_muon_parent_source_contact.py tests/test_muon_parent_dirac_cut.py
```

Frozen conditional locals: a_QED=0.00116550200495813; calibration-only
standard uncertainty 1.79e-13 under alpha_inverse=137.035999084,
standard uncertainty 2.1e-8 with the other original inputs fixed.
The already-combined selected-local interval remains
(0.0011655039493,0.0011655109506); the Higgs interval is not added again.
Neither a_mu nor g_mu=2(1+a_mu) is a complete physical BHSM number here.
No experimental anomaly or discrepancy was consulted or used to tune.
