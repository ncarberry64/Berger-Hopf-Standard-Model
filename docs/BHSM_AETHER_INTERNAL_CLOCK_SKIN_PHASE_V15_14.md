# BHSM internal clock, skin phase, and contact impulse

## Independent geometric clocks

Once regular parent and child worldtubes exist, their geometries provide
independent proper-time functionals

\[
 d\tau_s=\sqrt{-g_s(v_s,v_s)}\,d\lambda_s,
 \qquad s\in\{p,c\}.
\]

There is no requirement that \(\tau_p=\tau_c\). Given a self-adjoint physical
generator on an already selected domain, Stone transport gives

\[
 U_s(\tau_2,\tau_1)
 =\mathcal P\exp\!\left(-i\int_{\tau_1}^{\tau_2}G_s\,d\tau_s\right).
\]

This validates the child-history part of the new principle conditionally on a
physical child solution, generator, and domain. The current repository has no
physical child worldtube or stable recurring child clock, so it does not yet
provide numerical \(G_c\) or \(\tau_c\).

## Evolution phase is not the normal-domain phase

The v15.13 ambiguity is a normal self-adjoint boundary condition

\[
 \psi_-=U_\alpha\psi_+,
 \qquad
 U_\alpha=\frac{1-i\alpha}{1+i\alpha}.
\]

An internal scalar clock phase evolves both trace polarizations equally:

\[
 (\psi_+,\psi_-)
 \longmapsto
 e^{-iE\Delta\tau}(\psi_+,\psi_-).
\]

Therefore

\[
 \frac{e^{-iE\Delta\tau}\psi_-}
 {e^{-iE\Delta\tau}\psi_+}
 =\frac{\psi_-}{\psi_+}=U_\alpha.
\]

The same child clock preserves every \(\alpha\). This is an exact constructive
witness that worldtube evolution is not a skin-domain selection theorem.
Tangential Levi-Civita, spin, and gauge transport likewise does not determine
the missing normal trace graph without an additional variational relation.

There is also a circularity in the proposed expression
\(G_c=\mathfrak B_c[H_c^{\rm phys}]\): a differential expression becomes a
self-adjoint Hamiltonian only after its domain is supplied. Applying a
boundary representation to that Hamiltonian cannot select the domain already
used to define it.

## Global and relative phases

A common state phase multiplies both normal trace components and leaves
\(U_\alpha\) unchanged. Thus quotienting the wavefunction by global phase does
not quotient the self-adjoint extension parameter.

For scalar generators, independent histories would give

\[
 \Delta\theta
 =(\theta_{c,0}-\theta_{p,0})
 -\int G_c\,d\tau_c
 +\int G_p\,d\tau_p.
\]

The expression is invariant under a common phase shift, but evolution fixes
only phase differences along each history. The relative inception datum
\(\theta_{c,0}-\theta_{p,0}\) remains. BHSM has not derived a skin-formation
regularity or boundary action that selects it. Moreover, v15.2–v15.3 did not
prove that central generator shifts are unconditional gauge when histories
can interfere.

A single endpoint holonomy also has infinitely many self-adjoint logarithms:

\[
 e^{i\phi}=e^{-iG_nT},
 \qquad
 G_n=-\frac{\phi+2\pi n}{T}.
\]

Full continuous transport determines its Stone generator only after the
unitary history and domain are already specified.

## Contact impulse

Projecting the retained Hayward action

\[
 S_J=\kappa_1A_J\vartheta
\]

onto the invariant separation coordinate \(d\) gives the coefficient-locked
canonical jump

\[
 \boxed{
 \Delta P_d^{(H)}
 =-\kappa_1\left(
 \vartheta\frac{\partial A_J}{\partial d}
 +A_J\frac{\partial\vartheta}{\partial d}
 \right).}
\]

This is a genuine advance: no kick coefficient is needed. It is not yet an
evaluated impulse because the constraint-solved contact embedding has not
supplied \(A_J(d)\) or \(\vartheta(d)\). Its sign is consequently unknown.

If the child boundary generator depends on separation, the matter-clock
contribution has the Feynman--Hellmann form

\[
 F_d^{\rm clk}
 =-\langle\Psi_c,(\partial_dG_c)\Psi_c\rangle,
\]

with possible Berry-curvature terms for a moving domain. Phase continuity by
itself gives zero force when \(\partial_dG_c=0\). The retained action contains
no matter skin term and no physical \(\partial_dG_c\), so it supplies neither
a sign-selected outgoing impulse nor an ejection trajectory.

## Sigma and downstream gates

The A/B/C sigma witnesses cannot yet be evaluated on physical child
Hamiltonians, boundary generators, or contact impulses. All three survive.
No Hopf child, ejection, persistence, or downstream Standard Model gate can be
promoted.

## Foundational obstruction

The new principle does not close v15.13:

\[
\boxed{
\text{boundary identity plus internal-clock transport still leaves
continuously many self-adjoint skin domains.}}
\]

It also leaves an unselected relative inception phase. In plain language, an
internal clock tells an already defined state how to evolve; it does not say
how matter reflects or passes normally at the skin, nor how that rule is
initialized when the skin forms.

The required next object is:

`VARIATION_DERIVED_PARENT_AND_CHILD_SKIN_MATTER_BOUNDARY_ACTION_AND_INCEPTION_CONDITION_COUPLING_THE_NORMAL_TRACE_POLARIZATION_TO_THE_INTERNAL_CLOCK_GENERATOR_WITHOUT_A_FREE_PHASE`

`FULL_BHSM_COMPLETE = FALSE`.
