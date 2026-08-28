# Selected DOP853 nonlinear-cone projector and bordered inverse

The product-cone spectrum supplies a cell-local hard gap `g_product` and an
incremental halo Hessian motion `eta`.  Davis--Kahan gives a conservative
halo projector displacement `2 eta/g_product`.  Adding it to the already
certified path-projector graph motion transfers the same center chart to the
candidate nonlinear cone.

The bordered inverse is not transferred by multiplying that projector motion
by the old inverse.  For the local normalized selected vector, its exact
singular values remain

`{1,1,|lambda_j-lambda_24| : j != 24}`.

Thus the instantaneous inverse is `max(1,1/g_product)` and only the certified
chart condition multiplies it.  No kinetic, Dirac, or history operator is
inverted.  The candidate radius remains unpromoted until correlated
`Y,Z1,Z2` close.
