# Linear splitting of uncertain HS chain directions

The direct interval-direction pilot retains its complete paired results,
including midpoint bounds wider than the ambient-matrix alternative. This
variant uses the same endpoint direction bounds, old actual midpoint domain,
paired primal boxes, and frozen trial/preconditioner geometry.

Write the interval HS chain direction W as the exact center w0 plus delta.
At each point z of the certified domain, the derivative is linear in its input:

    DF(z) W = DF(z) w0 + DF(z) delta.

Evaluate the complete original variation graph directly on w0. Enclose the tail
using the already paired full 99-column derivative matrix on the identical
domain. This is an algebraic enclosure, not a neglected remainder, small-tail
assumption, or statistical independence assumption. It retains any correlation
conservatively by interval relaxation. The original D3/D4 and coupled-variation
proofs stored under center_* describe w0; they must not be relabeled as complete
variation solves on W. The summed derivative action encloses W.

Independent paired endpoint evidence is reused; midpoint and local outputs must
reproduce in fresh processes. Scope remains one frozen trial column of one
local operator. No physical quotient, full-path contraction, or BHSM completion
is asserted, and no measured data or fitting is introduced.
