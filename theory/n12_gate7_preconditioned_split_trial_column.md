# Preconditioned uncertainty tails in one frozen HS column

Reuse the paired center-split directional pilot on the same physical domains.
Let P = R_frozen^-1 T_frozen and Q = P DF_M, evaluated by signed Arb matrix
multiplication before multiplying any interval direction tail.

For endpoint action A, fixed trial column E, exact center direction w0, and
paired center action B0 enclosing DF_M w0, the local column equals

    fixed + h P A/6 + 2h (P B0 + Q deltaW)/3,

where fixed = P(L_frozen+I)E on the left, unit_j-P E on the right, and
deltaW encloses E/2 +/- h A/8-w0. Moving the fixed preconditioner inside the
tail product preserves cancellations lost by enclosing DF_M deltaW first.

A second equivalent association writes A = a0+deltaA, where a0 is exact, and
rho = E/2 +/- h a0/8-w0. It uses

    fixed + h P a0/6 + 2h P B0/3
      + (h P/6 +/- h^2 Q/12) deltaA + 2h Q rho/3.

The rho term includes every center-rounding discrepancy; it is not discarded.
The same deltaA occurs in the endpoint term and midpoint chain, hence combining
its coefficient is valid before interval multiplication. Both formulas rely
only on derivative linearity at each point, the original HS chain rule, and
already paired physical enclosures. They require no new action derivatives.

Check overlap with the existing paired column, retain the narrowest valid
coordinate bounds, and independently reproduce the resulting record/data.
This remains a fixed-frame, single-column local enclosure. Physical quotient,
frame derivatives, full-path contraction, and BHSM completion remain open.
