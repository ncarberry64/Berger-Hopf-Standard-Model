# BHSM N=3 congruent matrix-free square-KKT audit v18.31

The action-owned invertible map is applied congruently to the numerical linear
equation as `P J P dx = -P F`.  This does not left-scale or change the physical
376 residual rows.

MINRES does not converge within the bounded run, and the resulting direction
fails the exact nonlinear response check with maximum relative error `0.365`.
The Newton model is invalidated.  Its line trial remains only a physical-state
proposal subject to independent exact merit, eta and complete-child gates.
