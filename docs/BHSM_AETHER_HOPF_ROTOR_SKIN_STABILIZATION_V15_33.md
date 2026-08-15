# BHSM v15.33: Hopf/FR rotor stabilization test

## Result

The retained nonlinear system does **not** produce a stable encapsulated
child.  v15.32's material skin remains a physical saddle after the available
topological, FR, and fixed-charge mechanisms are inserted consistently.

The integer event flux

\[
Q_\Gamma=N_+-N_-
\]

is a topology-change label, not a canonical rotor momentum.  It cannot be
placed in a Routhian without a cyclic coordinate and a positive collective
inertia.

The historical odd-degree M8 sector conditionally has the FR sign
\((-1)^N\) and hence a half-odd rotor sector after identifying a physical
rotation loop.  The repository still lacks that loop identification, its
self-adjoint collective domain, and the M8-to-M4 transgression.  More
importantly, this claim boundary is not what decides the present stability
test.

## Fixed-eta obstruction

For any charge whose inertia depends only on eta, metric, and gauge data,

\[
V_C[\sigma]=\frac{C^2}{2I[\eta,g,A]},
\]

the admissible material variation with
\(\delta\eta=\delta g=\delta A=0\) gives

\[
\delta_\sigma V_C=0,
\qquad
\delta_\sigma^2V_C=0.
\]

The eta knot can therefore remain topologically stable while the independent
sigma enclosure collapses or de-envelops.

## The retained sigma-dependent inertia has the wrong sign

The only retained eta-inertia dependence on the material field is

\[
I_g(\ell)=I_\eta\left[1+gS(\ell)\right],
\qquad
S(\ell)=\langle\sigma_\ell^2\rangle_{S^3*S^3}.
\]

Along the exact pole-preserving wall translation of v15.32, reflection gives
\(S'(0)=0\), and direct quadrature gives \(S''(0)>0\).  Thus the seam is a
strict minimum of the retained inertia for \(g>0\).  At fixed nonzero charge,

\[
V_C''(0)=
-\frac{C^2gS''(0)}{2I_\eta[1+gS(0)]^2}<0.
\]

The fixed-charge correction softens the seam instead of stabilizing it.  For
\(g=0\) it has no effect.  A negative \(g\) is neither selected nor the
positive formation-inertia branch established in the v15.18--v15.20 chain.

## What a genuine stabilizer must do

A fixed charge can obstruct both pole limits only if its cyclic inertia is
localized on the material skin:

\[
I_{\rm skin}>0\quad\text{on the wall},
\qquad
I_{\rm skin}\to0\quad\text{in both material vacua}.
\]

Then \(C^2/(2I_{\rm skin})\) diverges at both collapse poles and can force an
interior minimum.  The coefficient-free density
\(1/4-\sigma^2\) has the required zeros, but coupling a cyclic Hopf rotor to
it is a new action completion.  No retained parent variation or uniqueness
theorem selects that term, so it is not inserted.

The exact next object is:

`ACTION_OWNED_SKIN_LOCALIZED_HOPF_FIBER_CYCLIC_INERTIA_WITH_ODD_DEGREE_FR_ANTIPERIODIC_SELF_ADJOINT_DOMAIN_AND_POSITIVE_COUPLED_CONSTRAINT_HESSIAN`

`FULL_BHSM_COMPLETE = FALSE`.
