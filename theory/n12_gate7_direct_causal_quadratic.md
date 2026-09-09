# Signed direct physical quadratic causal composition

For each LL, LT or TT input family, the local source from the physical
Hermite-Simpson second chain rule has four endpoint blocks Q00, Q01, Q10,
Q11. It already includes the Newton sign and Taylor factor one half.
The fixed initial input and response are zero. The frozen recurrence is

    z[i+1] = P[i] z[i] + Q_i[(u[i],u[i+1]),(v[i],v[i+1])].

The approximation P is the unchanged stored binary64 causal map. Its
certified global perturbation gain is applied once after center composition.

## Sparse input terms and cancellation

Only diagonal input-node terms and adjacent input-node pairs occur. A
diagonal term for node j receives Q_(j-1),11 at output node j, and Q_j,00
at node j+1. Propagate the first signed tensor by P[j], add the second,
then continue with that sum. Taking norms of the two injections separately
would lose a cancellation belonging to the same input term.

For LL, the adjacent term joins Q01+Q10. For TT, transpose both Cartesian
input indices in Q10 before joining Q01+transpose_inputs(Q10). LT retains
two distinct ordered terms: l_j t_(j+1) and l_(j+1) t_j. The TL family is
supplied by symmetry of the complete physical Hessian. Thus the final
two-radius quadratic majorant is LL*rL^2 + 2*LT*rL*rT + TT*rT^2.
LL and TT evaluate quadratic forms on a single input history; LT evaluates
the bilinear cross term between the longitudinal and transverse histories.

The algorithm streams one input term through all later output nodes. Only
two consecutive local interval records and one transported tensor are
retained, avoiding a full history tensor. Signed products and additions
precede output norms. Different input terms are combined by triangle bounds.
This bounds independently varying longitudinal amplitudes at every node;
it is not merely a single shared scalar-line calculation. Transverse input
uses the complete coordinate-space superset provided by the local consumer.

## Arithmetic and norm bounds

At each propagation step, retain the exact dyadic Arb midpoint and bound
the fresh radius separately. An n-by-q coefficient tensor with maximum
entry radius r has Frobenius error at most sqrt(n*q)*r. For a unit pair of
input blocks, the flattened Cartesian input has norm at most one. Therefore
this bounds the response error for that input term. Sum fresh errors over
terms at each output node and transport them once through the existing
signed block error recurrence. This includes local source uncertainty and
current multiplication/addition rounding without propagating wide interval
boxes repeatedly. All computations use at least 64 bits (512 by default).

For output axis e and coefficient matrix B, use ||e^T B||_F and

    ||(I-ee^T)B||_F^2 = ||B||_F^2 + (||e||^2-2)||e^T B||_F^2.

No exact unit-axis assumption is made. Sum input-term bounds before taking
the maximum over output nodes. Let those two maxima be CL, CT and let E
be the transported source error. With the verified projection norms aL,aT
and global frozen-map perturbation gain k<1, add the response error

    (k*(aL*CL+CT)+E)/(1-k)

using the retained stored-causal-error helper. L axes are already included
in the local tensors, so E receives no additional input-axis factor.

## Scope

Every interval is required by default. An explicit subset computes only
that subset's additive causal contribution and advertises incomplete
coverage. Missing active source blocks fail; they are never filled with
zeros. The method is conditional on matching physical source certificates,
frozen maps, axes and map gain. It supplies no neighborhood Hessian bound,
moving-frame derivative, physical quotient, contraction or Gate-7 closure.

## Scientific consumer

`scripts/certify_n12_gate7_direct_causal_quadratic.py` requires all 370 local
paired source manifests by default. Each contains exactly the 24 JSON/NPZ
files for its twelve blocks. Records must match the source producer's
complete schema, implementation fingerprints, physical Hessian pair
dependencies and the unchanged map/axis foundation. Within an interval all
source bindings must agree; across intervals every shared hash must agree.
Code fingerprints are captured before computation and all raw and normalized
input fingerprints are rechecked afterward.
Shared source files are verified when first encountered and must retain the
same declared hash in every interval. They are rechecked together on entry
to arithmetic and on exit, avoiding repeated reads of the entire common DF
campaign for each local interval.

The explicit `--intervals 13` option computes only interval 13's additive
contribution, still transported over the entire remaining history. It does
not replace the missing intervals with a purported full physical bound.
Run the same command with `--recompute` for an independent full recomputation;
only identical bytes receive a reproduction receipt. Failed candidates and
prior results are preserved. The default output is
`BHSM_N12_GATE7_FULL_DIRECT_CAUSAL_QUADRATIC.json`; the interval-13 output is
`BHSM_N12_GATE7_SELECTED_013_DIRECT_CAUSAL_QUADRATIC.json`.
