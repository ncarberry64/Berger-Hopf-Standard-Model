# BHSM N=3 matrix-free square-KKT Newton audit v18.30

The exact action Hessian and directional event Hessian-vector product define a
locally validated matrix-free KKT response at v18.29.  The maximum audited
directional response error is `3.48e-4`.

The bounded right-mapped GMRES run does not solve the Newton equation: its
exact relative linear residual is `56.93`.  Apparent merit changes below the
validated response displacement are not promoted.  The response operator is
retained; the Newton-solve claim is reclassified.
