# BHSM N=3 scalar complete-child boundary solution (v17.96)

The event-to-child gravity/eta scalar boundary problem now closes on one
admissible moving child germ. The solution simultaneously matches the three
event traces, seven local constraints, two attachment momenta, and two
dynamic Wentzell/Calderon flux rows while maintaining a positive refined
eta-Legendre margin.

The flux balance is evaluated with four neighboring resolved central-
difference steps. The resulting residual envelope is below `2e-5`; this is
the derivative-resolution tolerance of the present exact-action calculation,
not a requirement that any individual momentum, force, flux, acceleration,
or time derivative vanish.

This closes the gravity/eta scalar component of `F_child`. It does not yet
close the event-core pregeometric generator block, the gauge/spinor/ghost
Calderon projector, or a positive-duration persistence interval. Those remain
direct dependencies before the result can be inserted as the complete child
selection condition in the nonlinear N=3 closure.
