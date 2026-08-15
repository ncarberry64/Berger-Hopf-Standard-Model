# BHSM N=3 seven-constraint child Cauchy match (v17.94)

The complete local child constraint block has seven rows: the six lapse/shift
Euler equations and the Hamiltonian energy constraint. At the inherited
v17.75 terminal configuration, the minimum-distance projection closes all
seven rows to numerical tolerance while retaining finite nonzero child
motion.

That projection is not yet a complete reconstructed child. On the same
rank-two attachment tangent it gives

\[
F_{p}=p_{c,\mathrm{child}}-p_{c,\mathrm{event}},\qquad
F_{\Gamma}=\Gamma_{1,\mathrm{child}}^{\mathrm{actual}}
-\Gamma_{1,\mathrm{child}}^{\mathrm{required}},
\]

with norms approximately `75.35` and `2.8805e4`, respectively. These are
boundary solvability residuals, not defects inferred from nonzero momentum,
force, flux, acceleration, or time dependence.

The next child BVP therefore varies the interior N=3 coordinate, velocity,
and multiplier coefficients while holding the three event Dirichlet traces
fixed and imposing the seven constraints, two momentum matches, and two
dynamic flux matches. Only a solution of that coupled relation is eligible
to close the scalar part of `F_child`.
