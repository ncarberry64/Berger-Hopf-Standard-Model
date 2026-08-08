# BHSM v14.55 — Moving-Seam BVP and Pair-Wake Neutrino Action

## Primary verdict

`BHSM_V14_55_THE_MOVING_SEAM_NUMERICAL_BASIS_AND_PAIR_WAKE_ACTION_ARE_NOW_FAIL_CLOSED_AND_COMPUTABLE_AS_CONTRACTS_BUT_NO_ACTION_DERIVED_COEFFICIENT_SET_PERIODIC_PARTICLE_SOLUTION_OR_PHYSICAL_NEUTRINO_OBSERVABLE_HAS_BEEN_OBTAINED`

v14.55 turns the latest Norman Works physical explanation into a mathematical
contract and a deterministic numerical harness. It does **not** claim that the
hypothesis has been derived from the current BHSM action or validated against
neutrino data.

## 1. Three-harmonic moving-seam basis

The v14.54 Peter–Weyl channel table already contains many nonzero shape-current
channels. v14.55 predeclares three of them as a reduced numerical basis:

\[
M_{(0,0)}\leftrightarrow U_0D_0,
\qquad
M_{(3,0)}\leftrightarrow U_0D_1,
\qquad
M_{(1,1)}\leftrightarrow U_1D_2.
\]

A normalized matrix witness uses

\[
M_{(0,0)}=|0\rangle\langle0|,
\]

\[
M_{(3,0)}=\frac{|0\rangle\langle1|+|1\rangle\langle0|}{\sqrt2},
\]

\[
M_{(1,1)}=\frac{|1\rangle\langle2|+|2\rangle\langle1|}{\sqrt2}.
\]

Their Gram matrix has rank three, and the off-diagonal channels do not commute
with all other channels. This is enough to build a rank-three Galerkin/Floquet
solver. It does not select any physical amplitude, phase, ordering, or period.

## 2. Periodic BVP residual contract

The full state remains

\[
Y=(G,\eta,\sigma,A_{\rm YM},\Psi,X;\dot X)
\]

on matched parent and child domains. The seam is expanded as

\[
\xi(\tau,\Omega)
 =\sum_{k=1}^{3}q_k(\tau)M_k(\Omega)+\text{higher modes}.
\]

A physical solve must simultaneously satisfy:

\[
\mathcal E_{\rm bulk}^{\rm parent}=0,
\qquad
\mathcal E_{\rm bulk}^{\rm child}=0,
\]

\[
\Pi_{\rm child}-\Pi_{\rm parent}
 -\frac{\delta}{\delta X}
 \left(S_{\rm GHY}+S_{\rm corner}+S_{\rm compat}+\Gamma_{\rm rel}\right)=0,
\]

\[
Y(T)=h\cdot Y(0),
\qquad
\dot Y(T)=h\cdot\dot Y(0),
\]

\[
\partial_\lambda\Gamma_{\rm rel}=0,
\qquad
\partial_a\Gamma_{\rm rel}=0,
\]

plus gauge fixing, parent subtraction, relative heat-kernel regularization and
positive reduced Floquet stability.

v14.55 implements a deterministic residual evaluator for the reduced equations

\[
\ddot q_i+\Omega_i^2q_i
 =s_i\cos(n_i\omega\tau+\phi_i).
\]

The included exact witness chooses synthetic `s_i` so the residual vanishes.
This checks the solver harness only. The `s_i` must ultimately be replaced by
the action-derived Dirichlet-to-Neumann, determinant, matter and seam-current
sources.

## 3. Fixed-pair neutrino hypothesis

The hypothesis supplied in the lay-action interview is:

1. A neutrino-like object is one recognizable, inception-selected, unbalanced
   pair `Xi_AB`.
2. Its pair identity does not exchange during propagation.
3. The pair carries an internal cycle driven by its inherited inertia.
4. The universal three-dimensional surface permits three recognizable wake
   responses of that single pair.
5. A detector responds primarily to the pair-generated disturbance and
   perceives the three wake responses as electron, muon and tau flavor.
6. The background may contain more pair microstates than three; the number
   three belongs to the wake/detector projection.

A schematic action is

\[
S_\nu=
\int d\tau\left[
-\mathcal E_{\rm pair}(\Xi)
+\frac{I_\phi}{2}(\dot\phi-\omega_0)^2
+\frac{M_X}{2}g_{\mu\nu}\dot X^\mu\dot X^\nu
-V_3(\phi)
\right]
+S_{\rm wake}[g;\Xi,\phi,X]
+S_{\rm common}[X,\phi;J_{\rm matter}].
\]

The fixed identity condition is

\[
D_\tau\Xi_{AB}=0.
\]

Between interactions,

\[
\dot\phi=\omega_0.
\]

The wake is decomposed as

\[
\delta g_{\mu\nu}^{(\nu)}
 =\sum_{\alpha=1}^{3}
 w_\alpha(\phi,\dot X,\mathcal E)
 \mathcal W_{\mu\nu}^{(\alpha)}[\Xi_{AB}].
\]

The detector map is

\[
P_\alpha
\propto
\left|
\left\langle D_\alpha,
\delta g_{\mu\nu}^{(\nu)}
\right\rangle
\right|^2.
\]

Thus the model statement is not `Xi_AB -> Xi_BC`. It is

\[
\text{one fixed pair}
\longrightarrow
\text{changing threefold wake}
\longrightarrow
\text{changing detected flavor response}.
\]

## 4. Direct matter push and phase jumps

Matter acts on the intact pair as a common-mode impulse. It can redirect the
collective momentum and also advance, delay, or reset the internal cycle:

\[
P_X^+-P_X^-=\mathcal I_k,
\]

\[
\phi^+=\mathcal R_k(\phi^-,\mathcal I_k,\mathcal E_k),
\]

where `R_k` has advance, delay and reset branches. The pair identity and the
recognizable internal relation remain unchanged.

This separates free propagation from matter response:

\[
\text{free}:\quad
\phi(\tau+\Delta\tau)=\phi(\tau)+\omega_0\Delta\tau,
\]

\[
\text{matter}:\quad
(P_X,\phi,\omega)^-\mapsto(P_X,\phi,\omega)^+.
\]

Because an ultrarelativistic flight normally has elapsed time proportional to
baseline, a baseline pattern can emerge. The proportionality and the observed
phase laws must be derived rather than assumed.

## 5. Orbit-correlated mass response

The hypothesis allows an instantaneous inertial or wake response to vary with
orbital phase and environment. The physical mass candidate remains the
complete parent-relative cycle invariant:

\[
U_\nu(T)\psi_\alpha=e^{-i\theta_\alpha}\psi_\alpha,
\qquad
\epsilon_\alpha=\frac{\hbar\theta_\alpha}{T}
\quad \mathrm{mod}\ \frac{2\pi\hbar}{T}.
\]

Therefore v14.55 does not insert three primitive neutrino masses. It records the
required distinction between an instantaneous wake response and a full-cycle
quasi-energy.

## 6. Proposed matter-formation channel

The formation picture is

\[
(A,B)+(A',C)
\longrightarrow
[(A,B)+A'_{\rm outer}]+C^*,
\]

followed by

\[
C^*\longrightarrow\text{radiation}
\]

promptly or after a brief unstable excursion.

The captured `A'` is a **separate copy** of `A`, stripped from a donor pair. It
needs only to be the same basic kind. Its phase, orientation and motion adjust
as it locks to the collective disturbance of the recognizable inner pair.
The three members do not exchange core/outer roles during the normal cycle.
The collision chooses the initial phase on that cycle rather than a permanently
new continuous species.

At the stated energy regime, the one-body radiation loses detailed pair
identity. The stable three-body system stores which member was duplicated and
the resulting locked geometry, while radiation carries away energy, momentum,
angular momentum and all exact conserved charges.

This is a formation hypothesis, not an action-derived reaction amplitude.

## 7. Confinement contract retained

A color-open sub-envelopment must remain relative to an enclosing color-neutral
hadron orbit. A physical solution requires more than global color charge zero:

\[
D_iE^i=\rho
\]

locally, a singlet state globally, moving-seam traction balance, and

\[
-\log\langle W(C)\rangle
 =\sigma A(C)+\mu P(C)+\cdots.
\]

No hadron solution or string tension is derived in v14.55.

## 8. Empirical kill screens for the neutrino hypothesis

The pair-wake picture remains viable only if one action-derived coefficient set
can:

- derive the relativistic time/baseline phase law;
- generate two independent oscillation splittings;
- generate a unitary three-response detector map and CP behavior;
- reproduce vacuum and matter-dependent oscillation probabilities across all
  major neutrino source classes;
- distinguish coherent common-mode phase response from ordinary scattering;
- derive cycle quasi-energies without fitting measured masses;
- remain compatible with weak-interaction rates and null searches.

Failure of any mandatory gate invalidates the physical neutrino branch even if
the geometric picture remains suggestive.

## 9. Hindsight 20/20

### Validated

- Three independent noncommuting shape channels form a usable reduced solver
  basis.
- The periodic residual, position closure and tangent closure are deterministic.
- The fixed-pair/common-mode impulse model can represent free elapsed-time
  cycling and advance/delay/reset matter phase jumps without swapping pair
  identity.
- The pair-wake, duplicate-capture and radiation information-flow ideas are now
  explicit enough to vary and test.
- The nested color-neutral local-Gauss/Wilson requirements remain fail closed.

### Invalidated or forbidden

- Calling the synthetic residual witness a particle solution.
- Equating the three flavors with three underlying pair exchanges.
- Requiring matter to split the pair in order to alter flavor response.
- Treating one instantaneous wake phase as a primitive physical mass.
- Claiming the `2+2 -> 3+1*` process without an action-derived amplitude and
  exact conservation proof.
- Claiming confinement from global color neutrality alone.

### Open

- The complete parent-child backgrounds and DtN map.
- The relative trace-class heat kernel and nonlocal determinant.
- Action-selected seam harmonics, amplitudes, phases and period.
- A physical pair-wake source and detector functional.
- Neutrino splittings, PMNS, CP, matter response and cycle quasi-energies.
- Duplicate-capture amplitudes, radiation spectrum and stable matter spectrum.
- Nested color-neutral periodic solutions and the Wilson area law.
- Full gauge-fixed Floquet stability.

## 10. Completion status

Mark I remains reached. Mark II remains conditional. Mark III is not reached.
BHSM physical completion remains false. Frozen predictions and official
prediction logic are unchanged. No physical mass, mass splitting, PMNS matrix,
CKM matrix, coupling, lifetime, cross section or spectrum is emitted. The USB
remains untouched.

## Exact next object

`ACTION_DERIVED_PARENT_CHILD_DTN_COEFFICIENTS_AND_RELATIVE_HEAT_KERNEL_INSERTED_INTO_THE_THREE_HARMONIC_PERIODIC_BVP_FOLLOWED_BY_A_SIMULTANEOUS_FIT_FREE_DERIVATION_OF_NEUTRINO_PHASE_SPLITTINGS_MATTER_PHASE_KICKS_AND_NESTED_COLOR_NEUTRAL_ORBITS`
