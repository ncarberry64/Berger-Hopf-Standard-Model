# BHSM v14.54 — Cosmological Parent, Moving Seam, and Dynamic Floquet Mixing

## Primary verdict

`BHSM_V14_54_A_NONUNIFORM_MOVING_SEAM_SHAPE_DERIVATIVE_OF_THE_EXISTING_CHARGED_CURRENT_SUPPLIES_THE_REQUIRED_NONCENTRAL_PETER_WEYL_OPERATOR_BASIS_WITHOUT_AN_ARBITRARY_FLAVOR_MATRIX_BUT_THE_CURRENT_ARCHIVE_DOES_NOT_SELECT_THE_PERIODIC_SEAM_ORBIT_OR_CHANNEL_AMPLITUDES`

## 1. Purpose

v14.53 proved two facts:

1. the nonround Berger child has a negative minimal-Dirac relative Weyl-anomaly component in the positive-gauge convention;
2. every currently owned static family response lies in the same abelian algebra `C[C3]` and therefore cannot generate CKM.

The Norman Works recall changes the target. A particle is not required to be a static minimum. It may be a relative-periodic envelopment orbit with a moving boundary. v14.54 asks whether that moving boundary can source the missing noncentral family operators from the existing action rather than from an arbitrary flavor matrix.

## 2. Cosmological parent branch

The Topographic Dark Energy program supplies a large spatial parent

\[
S^3(R_H).
\]

The archived preprint uses a large-radius benchmark, approximately `25 Gpc`, while explicitly classifying it as illustrative rather than as the output of a full cosmological likelihood. Therefore v14.54 adopts two distinct statuses.

### Effective cosmological-anchor branch

Use a cosmologically inferred parent length `R_H` as the one universal dimensional anchor. Every lower scale must be relational:

\[
R_0=\lambda_0R_H,
\qquad
R_n=\lambda_nR_{n-1}.
\]

No independent particle radius is inserted.

### Zero-input branch

A zero-input completion still requires a coupled cosmology/BHSM action to derive `R_H` and every `lambda_n`. The current Topographic Dark Energy and BHSM actions have not yet been solved as one system.

Thus cosmology does not justify identifying `R_particle=R_H`. It changes the open question from “where does any dimensional unit come from?” to “what action-selected nesting ratios transmit the one parent unit to particle strata?”

## 3. Moving seam

Let the child-parent interface be an embedding

\[
X(\tau,\Omega)
=X_0(\Omega)+\xi(\tau,\Omega)n,
\]

with

\[
\xi(\tau,\Omega)
=\sum_{L,r}q_{Lr}(\tau)M_{Lr}(\Omega).
\]

The interface equation is the shape Euler equation

\[
\Pi_{\rm child}-\Pi_{\rm parent}
-
\frac{\delta}{\delta X}
\left(
S_{\rm GHY}+S_{\rm compatibility}+\Gamma_{\rm nonlocal}
\right)
=0.
\]

For a relative-periodic state,

\[
\Phi(\tau+T)=h\cdot\Phi(\tau),
\]

and the cycle must satisfy the averaged force balance

\[
\frac1T\int_0^T F_X(\tau)d\tau=0.
\]

The phase-closure and Dirichlet-to-Neumann conditions jointly determine, if nondegenerate,

\[
\lambda=R_{\rm child}/R_{\rm parent},
\qquad
T/R_{\rm parent},
\qquad
a.
\]

## 4. Why a moving seam supplies the missing tensor basis

The intrinsic charged-current action on the localized seam is

\[
S_{cc}
=
 g_2\int_{\Sigma_X}d\mu_X
\left[
\bar\Psi_u\gamma^aW_a^+\Psi_d+\mathrm{h.c.}
\right].
\]

Under a normal deformation,

\[
\delta_Xd\mu_X=K\xi\,d\mu_X.
\]

The frame, unit normal, spin connection, projectors and localized profiles also vary. Hence the mixed shape-current vertex is

\[
\Gamma_{+,X}^{Lr}
=
\frac{\delta^4S_{cc}}
{\delta q_{Lr}\,\delta W^+\,\delta\bar\Psi_u\,\delta\Psi_d}.
\]

Projecting onto normalized family embeddings gives

\[
c_{ij}^{Lr}
=
\left\langle
T_ue_i,
P_u\Gamma_{+,X}^{Lr}P_dT_de_j
\right\rangle_{\rm common}.
\]

The raw dynamic kernel is

\[
K_{ud}(\tau)
=
\sum_{L,r}q_{Lr}(\tau)c^{Lr}M_{Lr}.
\]

This is important: multiplication by a nonuniform shape harmonic is not a polynomial in the central `C3` shift. It is a Peter-Weyl tensor operator and can cross distinct `J` blocks according to the already derived Wigner-Eckart rules.

The exact nine-channel table is

\[
\begin{pmatrix}
(0,0)&(3,0)&(4,-2)\\
(3,3)&(3,3)&(1,1)\\
(5,4)&(4,4)&(2,2)
\end{pmatrix}.
\]

All nine entries possess nonzero normalized kinematic witnesses. At least three independent separable channels, or one genuinely nonseparable kernel, are required for rank three.

The basis is therefore available from the shape derivative of the existing current once the seam embedding is dynamical. What remains open is action selection of the periodic shape orbit `q_Lr(tau)` and its amplitudes and phases.

## 5. Dynamic abelian no-go

Time dependence by itself is insufficient. If

\[
H_f(\tau)\in\mathbb C[C_3]
\quad\text{for every }\tau,
\]

then

\[
[H_f(\tau_1),H_f(\tau_2)]=0.
\]

The time-ordered exponential reduces to an ordinary exponential in the common character basis. Up and down monodromies remain simultaneously diagonalizable, and CKM is trivial up to phases and permutations.

Therefore the physical “firestorm” must populate noncentral tensor harmonics. It cannot merely make the existing circulant coefficients fluctuate.

## 6. Floquet mixing and CP capability

For each sector,

\[
U_f(T)
=
\mathcal T\exp\left[-i\int_0^TH_f(\tau)d\tau\right].
\]

Let

\[
U_u=W_uD_uW_u^\dagger,
\qquad
U_d=W_dD_dW_d^\dagger.
\]

The cycle mixing matrix is

\[
V_{\rm cycle}=W_u^\dagger W_d.
\]

v14.54 includes a deterministic capability witness built from normalized `1-2` and `2-3` pair channels with one oriented phase. The resulting relative unitary is exactly unitary to numerical precision and has a nonzero Jarlskog witness. This is not a BHSM prediction; it proves only that the moving-seam tensor architecture is capable of producing full mixing and CP once the action selects the orbit.

In the Magnus expansion,

\[
\Omega_2
=-\frac12\int d\tau_1\int^{\tau_1}d\tau_2
[H(\tau_1),H(\tau_2)],
\]

so noncommuting boundary impulses create effective oriented generators absent from every instantaneous central response.

## 7. Cycle-invariant mass

The mass of a dynamic envelopment state is not an arbitrary instantaneous value. For

\[
\Phi_f(\tau+T_f)=h_f\cdot\Phi_f(\tau),
\]

its Floquet eigenvalues satisfy

\[
U_f(T_f)\psi_{f\alpha}
=e^{-i\theta_{f\alpha}}\psi_{f\alpha},
\]

with quasi-energy

\[
\epsilon_{f\alpha}
=\frac{\hbar\theta_{f\alpha}}{T_f}
\quad
\mathrm{mod}\ \frac{2\pi\hbar}{T_f}.
\]

The covariant mass readout must use the complete composite-minus-parent Hamiltonian charge, including gravitational, gauge, GHY, seam, corner and counterterm pieces. In a rest frame the stable cycle energy defines `m c^2`; on a stationary branch it must agree with the pole/quasi-energy prescription.

## 8. Confinement and neutrinos

The same dynamic architecture applies with different boundary conditions.

- A quark is a color-open sub-envelopment inside a color-neutral hadron orbit. Its monodromy and energy are relational to the enclosing hadron. The nonperturbative Wilson functional and color stress remain required.
- A neutrino is a near-null propagation-supported orbit. Its physical splittings arise from relative cycle phases, not primitive static rest masses.

These sectors are not numerically solved by v14.54.

## 9. Hindsight 20/20

### Validated

- A cosmological parent can serve as the one universal dimensional anchor on an effective branch.
- The remaining particle-scale problem is relational nesting, not creation of a second absolute unit.
- A nonuniform moving seam makes the shape derivative of the existing charged current a source of noncentral Peter-Weyl operators.
- All nine frozen up/down channels are kinematically available.
- Dynamic evolution confined to `C[C3]` remains flavor trivial.
- Noncommuting tensor-channel monodromy is mixing and CP capable.
- Mass belongs to the complete cycle invariant, not an instantaneous core snapshot.

### Invalidated

- Identifying the particle radius directly with `R_H`.
- Calling the illustrative cosmological `R_H` benchmark a zero-input BHSM derivation.
- Expecting time-varying circulant family matrices to generate CKM.
- Treating Casimir pressure or boundary motion as sufficient without noncentral shape harmonics.
- Reading physical mass from one instantaneous point of the orbit.

### Open

- A shared cosmology-particle parent action deriving `R_H`.
- A variable seam embedding in the active repository action.
- The matched parent and child periodic solution.
- Action-selected shape harmonics, amplitudes, phases and period.
- Complete relative determinant and interface stress.
- Gauge-fixed Floquet stability.
- Numerical masses, CKM, CP, PMNS, confinement and widths.

## 10. Completion status

Mark I remains reached and Mark II remains conditionally reached. Mark III is not reached. No physical scale, mass, coupling, CKM matrix, CP phase or PMNS matrix is emitted. Frozen predictions and official prediction logic are unchanged. The USB remains untouched.

## Exact next object

`NUMERICAL_COSMOLOGICAL_PARENT_TO_CHILD_MOVING_SEAM_BVP_AND_FLOQUET_SOLVER_WITH_THREE_ACTION_SELECTED_SHAPE_HARMONICS_COMPLETE_RELATIVE_HEAT_KERNEL_AND_NESTED_COLOR_NEUTRAL_ORBITS`
