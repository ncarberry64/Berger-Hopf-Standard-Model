# N12 C2 complete suppressed-R operator

For the fixed positive descriptor,

\[
\Delta=c\,b+sR,\qquad R=D^3S[W,\Psi,\Psi],
\qquad W=\dot Q+E V_{\rm hard}.
\]

The complete second derivative of `R` has the ten product-rule terms recorded
verbatim in the certificate.  This proof bounds the resulting bilinear form on
the full action tangent space and therefore also on the remaining non-scale
quotient.

The committed terminal-parent event action ball has radius `2e-10`.  Its center
is the event half of the reset-stratum candidate.  The action distance from
that center to node 1214 plus the node tube radius is strictly below `2e-10`,
so its full `D3`, `D4`, and `D5` retained-action majorants apply to every state
used here.  This containment check is performed from the stored state vectors;
it is not inferred from filenames.

The large first-response motion is not inserted into a generic `D4` or `D3`
bound.  Its center selected-selected contribution uses `D4_XCPP`, and its
center complement-selected contribution uses `D3_CCP` (with the selected
leakage retained explicitly).  Direction-box corrections use the full parent
majorants.  The two second-Jacobi terms

\[
D^3S[W_{ih},\Psi,\Psi],\qquad
2D^3S[W,\Psi_{ih},\Psi]
\]

reuse the already interval-evaluated global contractions.  Although first
used in the decisive-row certificate, these two bounds do not depend on that
row: the response and eigenline second-variation parents are bilinear operator
bounds, and the retained-action factors are full covector norms.  Hence their
composition bounds every pair of unit tangent directions.

Multiplication by the action-owned positive descriptor `s` gives the complete
global suppressed operator bound.  Common-scale covariance remains exact and
is not numerically reclassified; restricting this full bound to the non-scale
quotient can only decrease its operator norm.

This certificate closes only the one-time `s D2R` contribution.  Gate 7 stays
open until the independently fingerprinted complete non-scale `D2(cb)` row
sweep is merged, the two bounds exclude zero after transport, and the exact
segment transpose is applied.
