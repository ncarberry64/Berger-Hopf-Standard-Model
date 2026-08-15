# BHSM v16.12: common-pushforward N=3 KKT covector

This calculation advances the replacement-quantum N=3 event saddle.  It does
not revisit the rejected static finite-chart embedding.

For the anchored 376-variable KKT system, the 375-component action covector is
assembled by the discrete chain rule.  The parent Euler--Dirac jet supplies
the velocity and multiplier derivatives, node-local coordinate derivatives
are evaluated in the same radial action, and the common direct-sum heat
operator supplies both

\[
\frac{\partial\Gamma_{\rm heat}}{\partial\log R_i}
\quad\hbox{and}\quad
\frac{\partial\Gamma_{\rm heat}}{\partial\log\Delta\tau}.
\]

The second term is required because the physical proper-time step depends on
the period and boundary lapse.  Thus the gauge--ghost, rank-16 fermion, and HS
blocks remain one M5-to-M4 pushforward; no separate Yukawa normalization is
introduced.

The complete covector is checked against a finite difference of the full
replacement action.  The next dependency is the nonlinear solution of this
same 376-variable event-constrained KKT system.
