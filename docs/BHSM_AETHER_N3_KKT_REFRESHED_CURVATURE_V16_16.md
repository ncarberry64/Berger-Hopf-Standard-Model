# BHSM v16.16: refreshed nonzero-event KKT curvature

The v16.15 state has a nonzero event multiplier.  Therefore a fresh KKT
Jacobian must include

\[
D^2\Gamma_{\rm replacement}+\rho D^2 E,
\]

not only the action Hessian and event border that suffice at the original
rho-zero seed.  The event Hessian is evaluated on its exact 37-variable
terminal support and inserted into the same 376-variable physical KKT system.
The refreshed Newton direction is then trust-restricted and continued with
symmetric SR1 updates, with full residual and eta-domain checks at every step.
