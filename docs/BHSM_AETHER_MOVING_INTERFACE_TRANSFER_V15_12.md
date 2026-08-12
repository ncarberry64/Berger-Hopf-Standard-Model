# BHSM v15.12 moving-interface transfer theorem

The moving-interface assumption supplies the two-face geometry that was absent
in v6.10. Consequently the minimal gravitational action now necessarily
contains the coefficient-locked Hayward joint term

\[
S_J=\kappa_1\int_J\sqrt{|\gamma|}\,\vartheta.
\]

No new tension or transfer coefficient is introduced. In the reduced corner
coordinates \((A_J,\vartheta)\),

\[
\delta S_J=\kappa_1(\vartheta\,\delta A_J+A_J\,\delta\vartheta),
\qquad
\frac{\partial^2S_J}{\partial A_J\partial\vartheta}=\kappa_1,
\]

and the corner symplectic form is

\[
\Omega_J=\kappa_1\,\delta A_J\wedge\delta\vartheta.
\]

This is a coefficient-locked, nonzero geometric cross variation and the
smallest valid moving-interface advance beyond v15.11. Like GHY, however, the
Hayward term is first a variational completion; the corner term alone is not a
physical transfer Hamiltonian. Its complete constraint-reduced Hessian would
also include the adjoining bulk and compatibility responses.

Variation and distributional conservation give the structural interface
equations

\[
\Pi_p+\Pi_c+\frac{\delta(S_{\rm compat}+S_J)}{\delta\gamma}=0,
\qquad
[J\!\cdot n]-V_J[Q]=0.
\]

They become a physical traction/flux law only after the two traces, transported
charge, and post-contact domain have been identified.

## Contact capacity and action scaling

On a seven-dimensional spatial slice, a contact ball of radius \(\epsilon\)
has

\[
\operatorname{Cap}(B_\epsilon)
=5|S^6|\epsilon^5
=\frac{16\pi^3}{3}\epsilon^5.
\]

The local Einstein--Hilbert, GHY, and corner power counts are all
\(O(\epsilon^5)\), so geometric neck shrinking is not excluded by the fixed
positive-capacity theorem. It bypasses v15.11 without setting \(\upsilon=0\).

The retained eta action is more restrictive. If an eta mismatch across the
neck is \(\Delta\eta=O(\epsilon^a)\), its quadratic and eighth-order gradient
pieces scale as

\[
E_{\eta,2}=O(\epsilon^{5+2a}),\qquad
E_{\eta,8}=O(\epsilon^{-1+8a}).
\]

An order-one eta jump therefore diverges. Finite action requires at least
\(\Delta\eta=O(\epsilon^{1/8})\); the eta trace must become continuous at the
neck.

## What remains unselected

A smooth moving cut through one solution is pure repartition: complementary
bulk variations and internal GHY terms cancel, and the cut has zero physical
inertia. A genuine passage must instead change topology or operator domain.

The corner action does not select that surgery. For a two-side trace problem,
self-adjoint domains are maximal-isotropic graphs. Even the reduced family

\[
\psi_-=U\psi_+,
\qquad U\in U(1),

conserves flux for every \(U\). Likewise every matrix

\[
\mathcal K=
\begin{pmatrix}
K_R&T^\dagger\\
T&K_A
\end{pmatrix}
\]

is conservative when the diagonal blocks are self-adjoint, for continuously
many inequivalent magnitudes and phases of \(T\). The Hayward term acts on the
gravitational corner variables and selects none of these matter/core trace
identifications.

The full nonlinear v15.9 profiles are strictly monotone, so they possess
unique radial levels, but those levels are \(S^6\), not the required
\(S^3\times S^3\) Hopf seam. They do not provide the parent contact embedding,
relative normal angle, or post-contact gluing. The v15.10 A/B/C witnesses also
share the same coefficient-locked corner term, whose direct selector
Jacobian with respect to \((\alpha,r,\gamma)\) is zero.

## New foundational obstruction

Moving-interface geometry closes the gravitational corner mechanics but not
the reconnection law. BHSM still requires an action-selected cobordism/trace
functor specifying which sides are sewn and how geometric, eta, sigma, gauge,
and fermion traces are transported through the topology/domain change:

`ACTION_SELECTED_RECONNECTION_COBORDISM_AND_CORE_INTERFACE_TRACE_FUNCTOR_FIXING_THE_POST_CONTACT_GLUING_UNITARY_MATTER_DOMAIN_TOPOLOGY_CHANGE_AND_CONSERVATIVE_STATE_TRANSFER_WITH_HAYWARD_CORNER_SYMPLECTIC_MATCHING`

In plain language, the water/bubble assumption says that reconnection occurs,
but it does not yet say which mathematical reconnection occurs or how the
state crosses it. That missing rule is foundational. Until it is supplied or
derived, formation, persistence, de-envelopment, and downstream Standard Model
evaluation cannot be defined, and `FULL_BHSM_COMPLETE` remains false.
