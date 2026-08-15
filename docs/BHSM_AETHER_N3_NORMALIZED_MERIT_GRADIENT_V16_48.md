# BHSM N=3 normalized exact-merit-gradient continuation v16.48

This checkpoint removes the redundant spectral-damping/fraction scale by
forming the exact gradient of one half the squared complete KKT residual in
the declared Sobolev-scaled coordinates. A bounded trust-radius bank is then
evaluated after the same constraint projection and eta-domain guard.

This is a solver calculation on the unchanged action-plus-event system. It
adds no field, event, normalization, or particle-sector input.
