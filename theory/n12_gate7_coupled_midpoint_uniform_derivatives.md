# Uniform first derivatives on a paired actual HS midpoint domain

Require the independently reproduced actual midpoint field and eigenpair.
They refer to the same raw state domain, descriptor hull and simple normalized
selected eigenline. The paired contraction gives weighted row bounds V_i for
I-R J, weights r_i, and q=max(V_i/r_i)<1, with K=J diag(I,-1).

Every column of K u=b may therefore be enclosed by applying the weighted
Neumann estimate to z=diag(I,-1)u with zero center and residual R b. This is a
bound on the same coupled family, even if an independent-entry K hull is not
invertible. Sign reversal of the final coordinate returns u. No newly fitted
preconditioner, empirical data or reduced physical domain is introduced.

The retained physical rate producer supplies its complete first variation:
selected-line variation, physical-response variation, the derivative of the
configuration source, both third-action descriptor terms and their fourth-action
variations, and the normalization derivative. Its first bordered solve is the
paired uniform response; subsequent solves use the same coupled inverse bound.

Evaluate all 99 standard directions in the weighted augmented physical state,
including the descriptor direction. The original producer unweights only the
98 state directions. Separate direction batches bound the full basis on the
same domain and cannot be mistaken for evaluation at isolated centers.

These estimates may be broad. Finite uniform first derivatives alone do not
establish a useful radii polynomial, uniform Hessian bounds, the required
higher remainders, physical quotient, Gate 7 or full BHSM completion. Successful
numerical evidence must be independently reproduced before it is accepted.
