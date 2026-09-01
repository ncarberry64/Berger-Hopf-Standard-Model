# Gate-7 Arb Magnus-4 affine block composition

The finite Gate-7 Green calculation is an affine recurrence on the retained
73-dimensional physical quotient,

\[
 u_{i+1}=M_i u_i+b_i,\qquad u_0=0.
\]

The 47 homogeneous maps `M_i` are obtained by evolving each retained physical
tangent through the piecewise-affine 98-dimensional graph generator and
projecting at the next macro seam.  At 256-bit Arb precision all 5,908 fixed
Magnus-4 exponentials and the complete 47-map fundamental are outward
evaluated.  The largest macro-map component radius is `3.24001e-57`; the
global fundamental has operator upper bound `5342.55` and Frobenius component
radius `2.64403e-16`.

The signed source blocks `b_i` are evaluated independently from zero.  This is
essential: the frozen numerical center has a maximum off-tangent residue
`1.63099e-21`, which must not be relabelled as an action source.  Each Gauss-8
source uses its retained node-dependent subpartition, exactly matching the
frozen correlation-preserving Green calculation.  Sixteen independent worker
processes change only execution order; each block starts from the same exact
binary dyadic inputs and the results are serialized in seam order.

All 31,019 retained source/fundamental exponentials are evaluated at 256-bit
precision.  The largest source component radius is `9.53448e-76`.  The full
affine composition has maximum Euclidean radius `1.04610e-25` and maximum
outward difference `1.59437e-18` from the frozen quotient center.  Thus finite
matrix construction, exponential roundoff, signed source contraction, and
global correlated block composition are no longer Gate-7 blockers.

An aligned-suffix source partition was explicitly rejected: its local
`1e-19` representation change is amplified by the unstable tail and therefore
does not represent the frozen Green operator globally.  No selector, seam
source, fitted rebase, or new action term is introduced by using the retained
partition.

This certificate is only for the finite discrete operator.  The analytic
Magnus-4 higher-commutator remainder and the outward signed-source quadrature
remainder remain open.  Consequently Gate 7 and `FULL_BHSM_COMPLETE` remain
false.
