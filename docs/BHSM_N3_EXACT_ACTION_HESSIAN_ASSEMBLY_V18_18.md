# BHSM N=3 exact action-Hessian assembly v18.18

The known-inexact v17.58 proposal response is now a demonstrated blocker: the
v18.16 direction and its opposite both fail independent exact-merit descent.
This calculation therefore assembles the response of the unchanged v17.61
action covector directly.

Each node contributes its exact 26-variable local action Hessian.  The global
trapezoid-SBP coordinate/velocity/period chain rule is assembled explicitly,
including the nonlinear period dependence.  The same zero-source heat
operator supplies its log-radius/proper-step force, whose 25-variable Hessian
is differentiated and pushed through the exact reconstruction-radius and
lapse geometry.  The restored boundary term is differentiated analytically.

The result concerns the 375-dimensional action covector only.  It changes no
action, event equation, KKT row, eta condition, or complete-child gate.  Its
directional responses are compared directly with central differences of the
exact v17.61 covector before it can enter the explicit-multiplier square KKT.
