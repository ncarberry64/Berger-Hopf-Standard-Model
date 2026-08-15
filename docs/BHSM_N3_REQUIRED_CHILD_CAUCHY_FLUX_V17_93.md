# BHSM N=3 required child Cauchy flux (v17.93)

The event-to-child map now determines the child-side Neumann target rather
than imposing static balance. Along the full Euler--Dirac tangent, with the
state-dependent constraint lift differentiated at both sides,

\[
\Gamma_{1,\mathrm{child}}^{\mathrm{required}}
=-D_t p_c+\partial_c L-\Gamma_{1,\mathrm{event}}.
\]

This derives the algebraic scalar boundary form. Its original numerical
evaluation is provisional, however: the momentum rate was taken along the
pre-event terminal local state before that state was reconstructed on the
child's seven-constraint surface. v17.95 performs that reconstruction and
evaluates the form on the admissible child tangent. The scalar solvability
residual is

\[
F_{\mathrm{child}}^{\mathrm{scalar}}
=\Gamma_{1,\mathrm{child}}^{\mathrm{actual}}
-\Gamma_{1,\mathrm{child}}^{\mathrm{required}}.
\]

The actual child flux is not replaced by smooth reflection, zero flux, or zero
motion. Nonzero momentum, force, acceleration, and one-sided flux are balanced
terms in the same dynamic boundary equation. Only their constraint-consistent
combined residual is a child solvability condition.
