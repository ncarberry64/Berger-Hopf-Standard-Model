# BHSM electromagnetic-carrier continuation: a physical mode construction and its full-equation test

Norman Carberry research continuation — 16 October 2026

## Result and scope

Norman's hypothesis is that the electromagnetic carrier, in his broader BHSM
sense, carries spacetime differentials, boundaries and encapsulations. This work
does not replace that hypothesis with ordinary Maxwell theory. It constructs an
exact ordinary-Maxwell **seed and compatibility test** on the round three-sphere,
then identifies what a physical BHSM reduction must add or derive.

**Executed results:** four global, transverse electromagnetic modes; their exact
volume normalization and first-order curl operator; a two-coordinate embedding
that reproduces the retained scalar **homogeneous kinetic matrix**; its two
omitted normal equations; an exact family of source-free rotating solutions; an
explicit failure of generic projected solutions to solve the full field; the
second-map term that cancels a spurious phase stiffness; and bosonic reference
and energy-bound controls.

These are not actual collider packets, an interacting Berger/collar solution,
a reduction of the full M8 action, a fermionic muon construction, or a magnetic
moment prediction. The four radiation modes are not four newly introduced
particle species. No action coefficient, statistical multiplicity, physical
radius, inherited state or native cutoff is fitted or selected.

Source anchor: PR #465 was read at
`b6cb15f5ab6f6b44057f13895c5fd498ce928d83`. Its source term registry still describes
the M8-to-M5 and M5-to-M4 arrows as unconstructed [S1]. The two preceding attached
derivations remain partial constructions [S2,S3]. No repository writes were made.

## 1. Begin with actual electromagnetic fields and the gauge quotient

Consider the **fixed, round, source-free control**

\[
M=\mathbb R_t\times S^3_R,\qquad ds^2=-dt^2+R^2d\Omega_3^2.
\]

Use units with wave speed one. In temporal gauge, impose the source-free Gauss
constraint and Coulomb representative:

\[
A_0=0,\quad \delta_\Sigma A=0,\quad\delta_\Sigma\dot A=0.
\]

This is not the gauge/field preparation of charged incoming collider beams.
Their longitudinal constraint fields and source data cannot be set to zero by
importing this radiation-only control. The standard Maxwell action, gauge
constraint and physical transverse modes are reviewed in [S4].

On the real transverse one-form space use the first-order operator

\[
\mathcal C=*_{\Sigma}d_\Sigma.
\]

For the smooth closed sphere it has a self-adjoint realization on
\(H^1\cap\ker\delta_\Sigma\). The physical positive spatial square is

\[
P_{\rm rad}=\mathcal C^2=\delta_\Sigma d_\Sigma,
\qquad\mathcal D(P_{\rm rad})=H^2\cap\ker\delta_\Sigma.
\]

There is no boundary term in integration by parts on this closed control, and
\(H^1(S^3)=0\), so the transverse harmonic zero sector is absent. These facts do
not give an outgoing self-adjoint boundary condition on an open interacting
collar. The latter must retain its own traces, canonical flux and domain.

This operator acts on electromagnetic fields, not on arbitrarily added internal
Clifford matrices. It is also **not** identified with the complete generating
native operator or the physical fermion Dirac operator. No alternating form-degree
trace is substituted for statistical grading.

For the radiation fields, with \(\partial_tE=\mathcal C B\) and
\(\partial_tB=-\mathcal C E\), the complex combination obeys

\[
i\partial_t(E+iB)=\mathcal C(E+iB).
\]

This provides an actual first-order classical Maxwell evolution at the tested
scope. A scalar heat operator or a classical response alone does not select its
quantum state.

## 2. Four explicit global modes on S3

Let \(x=(x_0,x_1,x_2,x_3)\) be unit-sphere embedding coordinates. Define

\[
\begin{aligned}
\alpha_1={}&x_0dx_1-x_1dx_0+x_2dx_3-x_3dx_2,\\
\alpha_2={}&x_0dx_2-x_2dx_0+x_3dx_1-x_1dx_3,\\
\alpha_3={}&x_0dx_1-x_1dx_0-x_2dx_3+x_3dx_2,\\
\alpha_4={}&x_0dx_2-x_2dx_0-x_3dx_1+x_1dx_3.
\end{aligned}
\]

These are globally smooth one-forms. In the Hopf chart

\[
x=(\cos\eta\cos\alpha,\cos\eta\sin\alpha,
\sin\eta\cos\beta,\sin\eta\sin\beta)
\]

the executable checks directly differentiate all four forms with the round
metric. With the chart orientation \(d\eta\wedge d\alpha\wedge d\beta\),

\[
\delta\alpha_a=0,\qquad
\mathcal C\alpha_a=\frac{2\epsilon_a}{R}\alpha_a,
\quad(\epsilon_1,\epsilon_2,\epsilon_3,\epsilon_4)=(-1,-1,1,1).
\]

Their signs label curl helicity, **not** opposite boson/fermion statistics.
The existence and spectrum of vector harmonics on S3 have established treatments
[S5,S6]; the explicit identities here are independently checked symbolically.
They are a subset of the lowest six-dimensional transverse eigenspace, not the
whole spectrum.

Writing \(\alpha_a=(M_ax)\cdot dx\), the matrices are antisymmetric and
\(M_a^TM_a=I\). The exact Haar identity
\(\langle x_ix_j\rangle=\delta_{ij}/4\) gives

\[
\int_{S^3_R}\langle\alpha_a,\alpha_b\rangle\,dV
=2\pi^2R\,\delta_{ab}.
\]

For canonical Maxwell normalization set

\[
f_a=\frac{\alpha_a}{\sqrt{2\pi^2R}}.
\]

If the original electromagnetic action has coefficient \(1/e^2\), the mode
normalization is instead taken in that actual kinetic pairing (equivalently,
include the corresponding factor in \(f_a\)). This is a change of normalization,
not selection of a new physical coupling.

For

\[
A(t,y)=\sum_{a=1}^4Q_a(t)f_a(y),\qquad\Omega=2/R,
\]

the Maxwell action and the **full** equations within this invariant linear
four-mode subspace are exactly

\[
L=\frac12\sum_a(\dot Q_a^2-\Omega^2Q_a^2),
\qquad \ddot Q_a+\Omega^2Q_a=0.
\]

Other round-sphere modes decouple in this source-free fixed-geometry control.
This decoupling is not retained automatically under Berger deformation, moving
walls, metric variation or physical sources.

The modes are physical with respect to the electromagnetic gauge quotient:
\(df_a\ne0\). A nonzero combination cannot be a pure gradient, since its positive
square eigenvalue is \(4/R^2\). The full gravitational/diffeomorphism quotient and
anchoring of mode orientation remain separate requirements.

## 3. A scalar chart built from those physical modes

Assume the same local sign branch as the preceding trial:
\(b=Z_\sigma>0\), \(Z_\chi>0\), \(g>0\). Let

\[
r=g^{-1/2},\qquad k^2=Z_\chi g/b,\qquad\theta=k\chi.
\]

Define the four **real electromagnetic mode amplitudes** by

\[
\boxed{
Q(\sigma,\theta)=\sqrt b\,
(\sigma\cos\theta,\sigma\sin\theta,
r\cos\theta,r\sin\theta)^T.
}
\]

This is a map into the physical transverse mode space. In contrast to the
previous endomorphism trial, it does not require a new internal Clifford factor.
It is still an **inverse kinematic construction using the retained coefficients**,
not derivation of those coefficient values.

Its exact amplitude metric is

\[
dQ\cdot dQ=b\,d\sigma^2+b(\sigma^2+r^2)d\theta^2
=b\,d\sigma^2+Z_\chi(1+g\sigma^2)d\chi^2.
\]

Consequently, the complete homogeneous two-velocity kinetic matrix agrees with
the scalar target in [S1,S2]. The cross term vanishes for all \(\sigma,\theta\),
not just at one point.

**Important dimensional scope:** these are time-dependent collective coordinates
of a spatial Maxwell configuration. Recovering the entire local M8 density, its
spatial derivatives and reduction to M5/M4 requires an actual geometric
separation and normalization. Replacing every dot by a spacetime derivative is
not a demonstrated dimension-changing reduction. The radius is not set by this
kinetic match.

The phase rotates transverse fields, not the electromagnetic gauge phase of a
charged scalar. Its Maxwell field-strength variation is nonzero. Nevertheless,
its status after the full diffeomorphism/anchored-boundary quotient must be
checked. Its global period is a property of this trial chart, not an imposed
periodicity of the retained BHSM chi field.

## 4. The hidden restrictions of that scalar chart

The image is two-dimensional inside the four-dimensional amplitude space:

\[
Q_3^2+Q_4^2=br^2,
\qquad Q_1Q_4-Q_2Q_3=0.
\]

The first fixes one mode-pair amplitude. The second locks the two phases.
Ordinary source-free Maxwell theory does not impose these restrictions.

Let \(d=\sigma^2+r^2\) and \(J=\partial Q/\partial(\sigma,\theta)\). An orthonormal
normal frame is

\[
n_1=(0,0,\cos\theta,\sin\theta)^T,
\]

\[
n_2=\frac1{\sqrt d}
(-r\sin\theta,r\cos\theta,\sigma\sin\theta,-\sigma\cos\theta)^T.
\]

The checked identities are

\[
J^TJ=\operatorname{diag}(b,bd),\quad N^TN=I,
\quad N^TJ=0,
\]

\[
J(J^TJ)^{-1}J^T+NN^T=I_4,\qquad N=(n_1,n_2).
\]

Its extrinsic second derivatives give the exact Gaussian curvature

\[
\mathcal K=-\frac{r^2}{b(\sigma^2+r^2)^2}
=-\frac{g}{b(1+g\sigma^2)^2}.
\]

Thus the previous curved scalar kinetic geometry can indeed appear as a
nonlinear surface in a flat, physically normalized electromagnetic mode space.
That fact alone does not make the surface dynamically invariant.

## 5. Full field equations expose the required normal reaction

For the original Maxwell residual

\[
\mathcal E_Q=\ddot Q+\Omega^2Q,
\]

the two equations obtained by varying only the scalar chart are

\[
J^T\mathcal E_Q=
\begin{pmatrix}
b[\ddot\sigma+\sigma(\Omega^2-\dot\theta^2)]\\
b[(\sigma^2+r^2)\ddot\theta+2\sigma\dot\sigma\dot\theta]
\end{pmatrix}=0.
\]

The two omitted, independently evaluated normal components are

\[
\boxed{n_1\cdot\mathcal E_Q=\sqrt b\,r(\Omega^2-\dot\theta^2),}
\]

\[
\boxed{n_2\cdot\mathcal E_Q=
\frac{2\sqrt b\,r\dot\sigma\dot\theta}{\sqrt{\sigma^2+r^2}}.}
\]

These formulas give the **required** normal forcing in the convention
\(\ddot Q+\Omega^2Q=f\). They have not been supplied by a physical BHSM boundary
or source action, and are not inserted as fitted forces.

There is an exact source-free subset:

\[
\boxed{\sigma=\sigma_0,\quad\theta=\pm\Omega t+\theta_0.}
\]

It solves every original mode equation. These are rotating electromagnetic
configurations on a prescribed compact sphere, not proof of charged particle
encapsulation, formation, stability, or a muon lifetime.

For \(r>0\) and \(\Omega>0\), generic sigma motion cannot stay on this fixed-radius,
phase-locked surface without a normal response. Indeed, the first normal equation
forces \(\dot\theta^2=\Omega^2\), and the second then forces \(\dot\sigma=0\).

### Exact counterexample to projected admission

In deliberately chosen dimensionless **control** units, take

\[
b=r=\Omega=1,\quad \sigma=1,\quad\theta=0,
\quad\dot\sigma=1/3,\quad\dot\theta=1/2.
\]

The reduced equations give \(\ddot\sigma=-3/4\), \(\ddot\theta=-1/6\).
Their residual is exactly zero, but

\[
\|\mathcal E_Q\|^2=89/144,\qquad
\|\mathcal E_Q\|=\sqrt{89}/12\simeq0.7861650943.
\]

Moreover the original four-mode energy obeys

\[
\frac{d}{dt}\left(\tfrac12\dot Q^2+\tfrac12\Omega^2Q^2\right)
=\dot Q\cdot\mathcal E_Q=0
\]

along the projected equations. The residual is normal to the allowed velocity.
**Both projected equations and energy conservation can pass while the full
Maxwell equations fail.** This is a checkable logical distinction, not an
identification of the cause of the historical muon residuals.

Releasing the fixed amplitude and locked relative phase restores the full
four-mode Maxwell variables. Alternatively an actual geometric/interface action
could supply the needed normal reaction. The latter must be derived, not assumed.

## 6. Potential matching remains independent of the kinetic match

The actual magnetic mode energy on this fixed background is

\[
U_M=\tfrac12b\Omega^2(\sigma^2+r^2).
\]

It produces no quartic \(\sigma^4\) term. To match the retained field-dependent
potential, the actual additional coupled response would have to contribute

\[
\boxed{
\Delta V=\tfrac12(A_0-b\Omega^2)\sigma^2+	frac14G_0\sigma^4,
}
\]

as well as a separately accounted constant. The constant mode energy is not
silently removed from the gravitational or reference ledger.

This is a residual matching target, not a new term added to the action. A moving
geometry, nonlinear constitutive response, or the existing interface/quantum
terms could change the magnetic energy and normal equations. Their evaluation
has not been performed here. Ordinary linear Maxwell theory on this fixed round
sphere has not been substituted for Norman's broader carrier dynamics.

This result also does not cancel the previous trial Dirac heat expansion's
\(b\sigma^2R/12\) discrepancy. That was a different incomplete generating-operator
construction. Neither calculation currently replaces the microscopic native
functional, its statistical measure or relative completion.

## 7. Exact off-shell derivative correction

For any nonlinear field map \(Q(y)\),

\[
D^2(S\circ Q)[u,v]
=D^2S[J u,J v]+DS[D^2Q(u,v)].
\]

The second-map term is not generally zero on an unmatched background.
For the **actual mode potential** \(S(Q)=\Omega^2Q^2/2\), the true theta curvature
is zero because the potential does not depend on theta. But a pullback of only
the ambient Hessian gives

\[
(J^T\Omega^2I J)_{\theta\theta}=b\Omega^2(\sigma^2+r^2).
\]

The omitted contact is exactly

\[
(\Omega^2Q)\cdot Q_{,\theta\theta}
=-b\Omega^2(\sigma^2+r^2).
\]

Their sum is zero, as independent differentiation of the original restricted
potential requires. Thus forgetting the second-map term creates a fictitious
phase restoring force. This is an exact actionable derivative control, not a
claim to have repaired the saved 1.05–6.21% physical matching discrepancy.

Independent finite differences of the two normal-load formulas in section 5
show the expected second-order convergence; the reported errors are control
errors at chosen dimensionless inputs, not outgoing physical derivative bounds.

## 8. What must move in the actual electromagnetic-carrier map

On a regular fixed-domain source-free Cauchy slice, the transverse projector is
schematically

\[
\Pi_T=I-d\Delta_0^{-1}\delta,
\]

with the scalar zero sector removed and the inverse domain specified. In a
charged or bounded setting this must be adapted to the actual Gauss data and
boundary equations. The projector, inner product, normal, and trace maps depend
on the geometry.

For a field-coordinate map \(A(\phi)\), physical tangent modes are obtained after
solving those constraints, not merely by differentiating coefficients in a
fixed basis. The induced metric has the form

\[
\mathcal G_{IJ}=\langle W_I,W_J\rangle_{\rm physical},
\]

where the constraint-corrected \(W_I\), pairing, and domain all have their own
variations. With a moving positive pairing matrix/operator \(M\), even the
finite expression \(\mathcal G_{IJ}=W_I^*MW_J\) differentiates into three terms,
including \(W_I^*(\delta M)W_J\).

The same-action physical reduction must check both tangential equations and
normal/complement equations. Adding normal coordinates and solving their true
source problem is legitimate; suppressing them because the restricted action
looks correct is not. For a common linearized domain the retarded elimination
has the familiar Schur form, retaining the source-defect return. It remains a
history solve and is not replaced here by a static matrix inverse.

## 9. Geometry inferred from electromagnetic response does not automatically fix scale

For an ordinary Maxwell two-form in spacetime dimension d,

\[
*_{\Omega^2g}|_{\Lambda^2}=\Omega^{d-4}*_{g}|_{\Lambda^2}.
\]

In four dimensions the metric constitutive Hodge map is conformally invariant.
The classical source-free action is consequently unchanged by a local conformal
rescaling. This is a property of the classical field equations, not a statement
that quantum trace anomalies or massive charged matter are absent [S7].

Under suitable constitutive symmetry/closure assumptions electromagnetic
propagation can determine a conformal light-cone geometry, but identifying a
metric constitutive map is itself an additional condition [S8]. A single field
strength at one point does not supply the entire response law.

Thus a route from the ordinary four-dimensional electromagnetic response to
Norman's complete compression geometry must retain the additional scale-setting
information in the action, boundary, material/source or inherited-volume sector.
In eight dimensions the same two-form Hodge map has weight \(\Omega^4\), so the
four-dimensional conformal ambiguity is not a no-go theorem for an M8 carrier.
No M8 Maxwell action or arbitrary scale law is introduced by this comparison.

## 10. Inherited radiation uses bosonic, not CAR, covariance

For the four unconstrained radiation-mode oscillators let

\[
X=(Q_1,\ldots,Q_4,P_1,\ldots,P_4)^T,
\quad[X_i,X_j]=i\hbar\mathbb J_{ij},
\quad\mathbb J=\begin{pmatrix}0&I\\-I&0\end{pmatrix}.
\]

For the centered symmetrized covariance \(V\), the uncertainty condition is

\[
\boxed{V+i\hbar\mathbb J/2\succeq0.}
\]

It has no fermionic upper bound \(V\le I\). This standard bosonic structure is
reviewed in [S4,S9]. No Gaussian assumption is required for the necessary
uncertainty inequality or for the expectation of a quadratic observable.
Higher correlation functions are still needed for nonquadratic readouts.

For quadratic evolution, the inherited covariance transport is

\[
V(t)=S(t,t_0)V(t_0)S(t,t_0)^T,\qquad S\mathbb JS^T=\mathbb J,
\]

with derivative

\[
\delta V=(\delta S)V_0S^T+S(\delta V_0)S^T+SV_0(\delta S)^T.
\]

For constant frequency \(\Omega\),

\[
S(t)=\begin{pmatrix}
\cos\Omega t\,I&\sin\Omega t\,I/\Omega\\
-\Omega\sin\Omega t\,I&\cos\Omega t\,I
\end{pmatrix}.
\]

The controls compare a vacuum covariance and a thermal covariance with occupation
three in each mode. Both obey uncertainty and use the same evolution, while
their energies differ. They are test states, not selected primordial references.
Their difference demonstrates that an electromagnetic carrier and its retarded
evolution do not themselves determine its quantum occupations.

Fermionic particle-sector CAR calculations remain valid where their modes and
statistics have actually been identified. The map from this bosonic radiation
seed to charged spin-half encapsulated modes has not been constructed here.

### A state-independent conditional bound

Let an actual finite-mode quadratic response be

\[
\widehat O=\tfrac12X^TKX,\qquad
\widehat H=\tfrac12X^THX,\quad H\succ0,
\]

with real symmetric matrices and Weyl ordering. Define

\[
\kappa=\|H^{-1/2}KH^{-1/2}\|_{\rm op}.
\]

Then \(-\kappa H\preceq K\preceq\kappa H\). A positive quadratic form is a sum
of squares of self-adjoint linear observables, so

\[
-\kappa\widehat H\le\widehat O\le\kappa\widehat H.
\]

Hence, for **any** state with \(\langle\widehat H\rangle\le E_{\max}\),

\[
\boxed{|\langle\widehat O\rangle|\le\kappa E_{\max}.}
\]

This includes coherent means if their contribution to the energy is retained.
For differences between two states, use their combined energy budget. This bound
does not require them to be Gaussian. It needs a genuine positive energy
operator and a genuine budget; vacuum-subtracted energy cannot silently replace
that operator. In the continuum, finite energy, relative subtraction and domain
control need their own proof.

No physical sea budget or complete muon quadratic kernel was supplied here, so
this yields no numerical uncertainty for a_mu. A nonlinear self-consistent
readout still requires the full adjoint and remainder analysis in [S2,S3].

## 11. Executed verification and scientific meaning

`check_carrier_reduction.py` performs ten symbolic check groups and three
numerical check groups. Each of two separate executions writes a deterministic
JSON result. The checks include global-mode smooth representations, transverse
curl identities, exact volume Gram, scalar metric, complete tangent/normal
projectors, potential mismatch, full-equation counterexample, off-shell
second-map cancellation, conformal weights, independent source differences,
bosonic state transport and the quadratic energy bound.

There is no spectral truncation error in the exact round-sphere four-mode
source-free subproblem, because that linear eigenspace is invariant. There is
also **no claim** that four modes approximate the actual interacting BHSM
solution to any specified tolerance. The nonlinear two-coordinate restriction
fails generically even within those four modes.

The actual comparison to BHSM requires its compatible Berger/stratified domain,
full mode normalization, geometry and source response, statistical carrier and
inherited state. Old muon residuals are not imported as residuals of this new
control. No new all-226 or Maxwell physical validation is asserted, and the
physical matching guard remains 2e-10.

## 12. The next mathematical connection

The physically meaningful question is now concrete:

> Does the existing BHSM geometry/interface/induced action supply the normal
> reaction and potential required by an electromagnetic-carrier mode reduction,
> while preserving its complete field equations and quantum statistics?

The two explicit normal projections in section 5 are a seed test, not the
universal answer on a moving wall. The next actual calculation must construct
the corresponding modes on the physical carrier/domain and evaluate the full
normal/complement action there. It must also reproduce the quartic and other
retained sectors. No new confining potential is to be inserted just to keep the
trial surface fixed.

This continuation narrows the correspondence problem from arbitrary matrices
to actual electromagnetic configurations and exposes the exact additional
dynamical conditions. It neither establishes the universal carrier hypothesis
nor dismisses it because the restricted Maxwell seed is insufficient.

## Sources and provenance

[S1] Norman Carberry, BHSM repository, PR #465, pinned commit above:
`src/bhsm/interface/master_action/terms.py`, blob
`9080437c072c507d9c04f7e50b02c3377402eb4f`.
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/b6cb15f5ab6f6b44057f13895c5fd498ce928d83/src/bhsm/interface/master_action/terms.py

[S2] Attached `BHSM_scalar_reference_continuation_20261016/DERIVATION.md`.
This is the preceding trial construction and reference-sensitivity analysis,
not an independent empirical or microscopic validation.

[S3] Attached `BHSM_operator_reference_construction_20261016/DERIVATION.md`.
This is the preceding conditional operator/domain construction and state test.

[S4] David Tong, Quantum Field Theory, section 6, Quantum Electrodynamics.
https://www.damtp.cam.ac.uk/user/tong/qft/qfthtml/S6.html

[S5] J. Ben Achour, E. Huguet, J. Queva and J. Renaud,
Explicit vector spherical harmonics on the 3-sphere, arXiv:1505.03426.
https://arxiv.org/abs/1505.03426

[S6] J. Kopinski and J. Natario, On a remarkable electromagnetic field in the
Einstein Universe, General Relativity and Gravitation 49, 81 (2017).
https://doi.org/10.1007/s10714-017-2242-7
The established electromagnetic S3 construction is not claimed as a new discovery.

[S7] J. Cote, V. Faraoni and A. Giusti, Revisiting the conformal invariance of
Maxwell's equations in curved spacetime, arXiv:1905.09968.
https://arxiv.org/abs/1905.09968

[S8] G. F. Rubilar, Linear pre-metric electrodynamics and deduction of the light
cone, arXiv:0706.2193.
https://arxiv.org/abs/0706.2193

[S9] C. Weedbrook et al., Gaussian Quantum Information, arXiv:1110.3234.
https://arxiv.org/abs/1110.3234
Our displayed covariance convention uses hbar=1 in numerical controls, rather
than silently carrying a different quadrature normalization between sources.
