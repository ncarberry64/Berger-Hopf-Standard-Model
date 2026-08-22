# Constraint-reduced energy identity at the N12 child

Let the retained finite-order action be

\[
L_N(q,v,m),
\]

where (m) contains the (N) lapse and (N) shift coefficients.  The
unchanged constraint map implemented by BHSM is

\[
C_N(q,v,m)=\left(\partial_mL_N,\ E_N\right),\qquad
E_N=\partial_vL_N\cdot v-L_N.
\]

This is not an interpretation imposed after the solve.  It is the exact map
returned by `constraint_residual`, and the high-precision N12 evaluator
repeats the same definition.  The unchanged 57-row N12 event-child map puts
one copy of (C_{12}) on the event side and one copy on the child side.
Consequently every exact complete-child root satisfies

\[
E_{12}(Y_{\rm event})=E_{12}(Y_{\rm child})=0.
\]

More generally, on the physical constraint set

\[
\mathcal C_N=C_N^{-1}(0),
\]

the restricted Legendre energy is the constant zero function.  For every
(C^1) curve \(\gamma(s)\subset\mathcal C_N\),

\[
\frac{d}{ds}E_N(\gamma(s))=0.
\]

For every (C^2) curve in the same set,

\[
D^2E_N[\dot\gamma,\dot\gamma]+DE_N[\ddot\gamma]=0.
\]

Thus the intrinsic second variation of the restricted energy is zero.  An
ambient Hessian with the constraint curvature term omitted is not the
Hessian of the reduced energy and cannot be promoted to a coercive physical
form.  Passing to the gauge quotient cannot change the zero function into a
positive norm.

This closes the earlier audit in the negative: the currently implemented
local Legendre energy cannot furnish the missing strong-(S_2) a priori
bound.  The result does **not** show that the retained child dynamics lacks
all a priori estimates, nor does it disprove a boundary-improved Hamiltonian.
It shows only that the exact energy row already used to define the child is a
zero constraint, not a nonzero physical charge, mass, or coercive norm.

The matched-parent route remains unavailable and is not repaired by this
identity.  The shortest action-owned continuation route is therefore to
derive the complete child-only boundary-improved Hamiltonian variation

\[
\delta H_\xi^{\rm child}
=\int_{\partial\Sigma}
  \left(\delta Q_\xi-i_\xi\Theta_{\rm retained}\right)
-\delta B_\xi,
\]

directly from the retained action and test whether its gauge-reduced
quadratic control closes the continuum child flow.  This child-only charge
may be used for an a priori estimate if derived, but it is not the absent
composite-minus-parent \(\Delta H\) and must not be called mass.  If the
boundary-improved variation also fails to control the strong topology, the
remaining honest route is a direct analytic continuation/exit estimate for
the existing retained flow, not numerical trajectory campaigning.
