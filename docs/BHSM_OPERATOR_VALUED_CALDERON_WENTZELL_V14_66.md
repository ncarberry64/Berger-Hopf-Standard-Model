# BHSM v14.66 — Operator-Valued Calderón/Wentzell Retained-Mode Gate

## Executive result

v14.66 upgrades the exact scalar self-adjoint envelopment diamond of v14.65
into a vector/operator-valued retained-mode theorem class.

The scalar v14.65 realization was rigorous but collapsed to one magnetic
circle because every vertex had degree two.  Its spectrum could depend only on
total metric length and one scalar loop holonomy.  That was too small to
retain independent M8/M5/M4 spectral response.

v14.66 replaces the scalar edge quantity by a positive Hermitian tangential
operator on a retained common boundary mode block:

\[
P_e=-D_x^2+K_e^2,
\qquad K_e=K_e^*>0.
\]

The endpoint connection is represented by a unitary parallel transport
\(U_e\).  This is the smallest exact theorem class in which different strata
can carry genuinely different noncommuting tangential response while still
sharing one attachment Hilbert space.

The result is:

`BHSM_V14_66_OPERATOR_VALUED_RETAINED_MODE_CALDERON_WENTZELL_DOMAIN_CLOSED_CONDITIONALLY`

The qualifier is essential.  The theorem-class operator is exact, but the
physical action-normalized M8/M5/M4 Calderón blocks and the physical
core/wall response Gram-Hessian have not yet been evaluated.

## 1. Exact Berger retained-mode input

The retained geometric witness uses the exact homogeneous Berger Dirac block

\[
D_n
=C I
+2a\,\sigma_z\otimes J_z
+2b\,\sigma_y\otimes J_y
+2c\,\sigma_x\otimes J_x,
\]

with

\[
a=b=R^{-1},\qquad c=(\beta R)^{-1},
\]

\[
C=\frac12\left(\frac{ab}{c}+\frac{bc}{a}+\frac{ca}{b}\right).
\]

For \(n=1\) its eigenvalues reproduce the v14.59 closed form

\[
\frac{\beta-4}{2R},\qquad
\frac{\beta^2+4}{2\beta R}\ \text{(double)},\qquad
\frac{\beta+4}{2R}.
\]

At the frozen diagnostic Berger value

\[
\beta=1.157054135733433,
\]

the computed spectrum is

\[
(-1.4214729321332835,
 2.3070546606852154,
 2.307054660685216,
 2.578527067866717)/R,
\]

with closed-form residual

\[
4.44\times 10^{-16}.
\]

The \(n=2\) blocks at different anisotropies are genuinely noncommuting.  The
diagnostic commutator norm between \(\beta=1.04\) and \(\beta=1.47\) is

\[
\|[D_2(1.04),D_2(1.47)]\|=3.182165524963008.
\]

Thus the retained tangential geometry is not forced into one commuting scalar
response.

A strictly positive edge tangential operator is constructed as

\[
K_e=\sqrt{D_2(\beta_e)^2+\mu^2I},
\]

with \(\mu>0\) used only in the deterministic theorem witness.

No physical M8/M5/M4 operator claim follows from these diagnostic \(\beta_e\)
values.

## 2. Exact operator-valued Calderón/Weyl function

For an edge of length \(\ell\), source-frame positive tangential operator
\(K\), and unitary transport \(U\) from source to target, functional calculus
gives

\[
A=K\coth(\ell K),
\qquad
B=K\operatorname{csch}(\ell K).
\]

The exact endpoint Weyl matrix is

\[
M_e=
\begin{pmatrix}
A & -BU^*\\
-UB & UAU^*
\end{pmatrix}.
\]

It is Hermitian and strictly positive.  Summing the four incidence-edge
contributions produces a \(24\times24\) operator-valued global Weyl map on the
retained \(n=2\) six-dimensional common mode block.

The deterministic witness gives

\[
\|M-M^*\|=0,
\]

\[
\lambda_{\min}(M)=3.7888318321543073>0.
\]

Under independent unitary changes of frame \(G_v\) at every stratum vertex,

\[
K_e\mapsto G_{s(e)}K_eG_{s(e)}^*,
\]

\[
U_e\mapsto G_{t(e)}U_eG_{s(e)}^*,
\]

and the assembled map obeys

\[
M\mapsto G M G^*.
\]

The measured covariance residual is

\[
2.12\times10^{-14}.
\]

## 3. Scalar-circle collapse is lifted at the response level

v14.65 proved that a scalar degree-two Kirchhoff diamond with fixed total
length is exactly one magnetic circle.  v14.66 tests whether that collapse
survives once distinct operator-valued tangential blocks are attached.

Two edge-length partitions are compared:

\[
(1,1,1,1)
\]

and

\[
(0.4,1.6,0.7,1.3),
\]

which have exactly the same total length.

Using the same frozen tangential blocks and the same transports, the global
operator-valued Weyl responses differ by

\[
\max_i|\lambda_i(M_A)-\lambda_i(M_B)|
=1.8317409336991668,
\]

while the trace difference is

\[
|\operatorname{Tr}M_A-\operatorname{Tr}M_B|
=7.233744038844208.
\]

Therefore the scalar-circle partition degeneracy does **not** persist at the
operator-valued boundary-response level.

This is deliberately not promoted to a theorem about the complete continuum
BHSM spectrum.  It proves that operator-valued Calderón data can retain the
stratum information that the scalar graph necessarily erased.

## 4. Non-Abelian envelopment holonomy

The scalar loop phase of v14.65 generalizes naturally once the endpoint
parallel transports are matrix-valued.

For the oriented loop

\[
M_8\to M_{5,+}\to M_4\to M_{5,-}\to M_8,
\]

the Wilson operator is

\[
W_\\diamond
=U_{8-}^*U_{-4}^*U_{+4}U_{8+}.
\]

Under vertex gauge transformations it changes only by conjugation at the base
vertex.  Hence its eigenphases are gauge invariant.

The deterministic six-mode witness gives the eigenphases

\[
(-0.5173312117,
 -0.2811306913,
 -0.0559540771,
  0.0732829527,
  0.2329260597,
  0.5482069678),
\]

with post-gauge maximum eigenphase residual

\[
8.88\times10^{-16}.
\]

This establishes a kinematic route to multiple relative phases without
inserting a flavor matrix.  It does not derive the physical connection or its
holonomy.

## 5. Exact Wentzell self-adjoint domain from a KKT Schur form

The stratified BHSM architecture already identifies the reduced boundary
Hessian as a Schur complement of the form

\[
H_{\rm eff}=H_{bb}-H_{bi}H_{ii,\perp}^{-1}H_{ib}.
\]

v14.66 uses that exact algebraic form to test the dynamic-boundary route.  The
deterministic KKT witness defines

\[
W_v=H_{bb}^{(v)}-H_{bi}^{(v)}(H_{ii}^{(v)})^{-1}H_{ib}^{(v)},
\]

and verifies \(W_v=W_v^*>0\).

The vector-valued boundary conditions are

\[
u_i-u_j=0,
\]

\[
p_i+p_j+W_vu_v=0.
\]

Written as

\[
A\Gamma_0+B\Gamma_1=0,
\]

the full retained-mode boundary dimension is 48 and the exact extension tests
give

\[
\operatorname{rank}(A\;B)=48,
\]

\[
AB^*-BA^*=0.
\]

The sampled boundary Green-form residual is

\[
2.39\times10^{-15}.
\]

Thus a Hermitian dynamic KKT/Wentzell boundary operator is fully compatible
with exact self-adjointness in the retained theorem class.

The physical BHSM core/wall Gram-Hessian has **not** been substituted into
\(W_v\).  That is now the highest-upstream physical blocker.

## 6. Gauge/constraint quotient and response heat gate

To prove the downstream algebra can remain fail closed, two explicitly
labeled diagnostic null directions are removed with an orthogonal quotient
basis \(Q\).

The checks give

\[
\|Q^*Q-I\|=2.43\times10^{-17},
\]

\[
\|Q^*Z\|=1.06\times10^{-16}.
\]

The projected response is Hermitian and positive, with

\[
\lambda_{\min}(H_{\rm phys})=4.424661901299775.
\]

A finite response heat/log-determinant comparison against a round/identity
reference gives diagnostic values

\[
\Delta\Theta_{\rm response}(0.55)
=0.13291051385141295,
\]

\[
\Delta\log\det H_{\rm response}
=-1.1950716816762252.
\]

These are finite-dimensional boundary-response diagnostics only.  They are
**not** the full mixed-dimensional continuum relative heat supertrace.

## 7. Neutrino kill screen remains hard closed

No neutrino prediction is emitted.  Physical execution remains blocked until
all of the following exist simultaneously:

* action-stationary cosmological parent background;
* action-stationary regular child cap;
* actual normalized M8 Calderón/tangential block;
* actual normalized M5 plus/minus blocks;
* complete intrinsic M4 fermion/gauge/scalar block;
* physical core/wall KKT response Gram-Hessian;
* complete Calderón/gauge/ghost/zero-mode projectors;
* continuum relative heat supertrace;
* action-selected non-Abelian connection holonomy;
* action-selected three transverse moving-seam channels;
* physical detector projection map;
* blinded neutrino targets frozen before prediction.

The executable gate therefore returns

`PHYSICAL_EXECUTION_BLOCKED`.

Post-comparison parameter adjustment is forbidden.

## Hindsight ledger

### Validated

1. Exact homogeneous Berger retained-mode blocks reproduce the v14.59 n=1
   closed spectrum.
2. Higher retained Berger blocks can be noncommuting across anisotropy.
3. Positive operator-valued edge Calderón/Weyl functions are exact by
   Hermitian functional calculus.
4. The assembled Weyl map is Hermitian, positive and vertex-gauge covariant.
5. A Hermitian KKT Schur complement defines an exact self-adjoint Wentzell
   boundary extension.
6. The operator-valued Wilson loop carries gauge-invariant eigenphases.
7. Equal-total-length edge partitions are distinguished at the retained
   operator-response level.
8. The quotient/response-heat pipeline can execute without retuning.

### Invalidated

1. The v14.65 scalar-circle collapse must survive after noncommuting
   tangential blocks are inserted.
2. All loop information is exhausted by one scalar phase in an
   operator-valued connection.
3. Dynamic seam/Wentzell terms are incompatible with exact self-adjointness.

### Reclassified

1. The unresolved domain problem is now **physical block provenance**, not
   existence of an operator-valued self-adjoint theorem-class realization.
2. The scalar diamond phase becomes Wilson-loop conjugacy data.
3. The open common-domain response Gram-Hessian is the natural physical source
   for the Wentzell operator.
4. The current heat/logdet calculation is a finite response diagnostic rather
   than the continuum BHSM supertrace.

### Open

* physical action-normalized common-attachment response Gram-Hessian;
* actual M8 Calderón/tangential operator;
* actual M5 plus/minus cap operators;
* complete intrinsic M4 fermion/gauge/scalar block;
* physical non-Abelian connection holonomy;
* complete gauge/ghost/zero-mode and Calderón projectors;
* three action-selected transverse moving-seam channels;
* mixed-dimensional continuum relative heat supertrace;
* global stationary branch exhaustion and gauge-reduced Hessian;
* blinded no-retuning neutrino kill screen.

## Completion status

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

Frozen predictions are unchanged.  Official prediction logic is unchanged.
No physical mass, coupling, CKM/PMNS matrix, CP phase, neutrino splitting, or
cross section is emitted.  USB remains untouched.

## Exact next object

`ACTION_NORMALIZED_PHYSICAL_COMMON_ATTACHMENT_RESPONSE_GRAM_HESSIAN_AND_ACTUAL_M8_M5_PLUS_MINUS_M4_TANGENTIAL_CALDERON_BLOCKS_ON_THE_GLOBAL_STATIONARY_ENVELOPMENT_BACKGROUND_WITH_COMPLETE_GAUGE_GHOST_ZERO_MODE_PROJECTORS_THEN_CONTINUUM_RELATIVE_HEAT_SUPERTRACE_AND_FROZEN_NO_RETUNING_NEUTRINO_KILL_SCREEN`
