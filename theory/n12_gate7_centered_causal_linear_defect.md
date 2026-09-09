# Signed-center causal linear defect

Status: conditional arithmetic method for the existing fixed-frame Newton
inverse. This document establishes neither physical quotient identification
nor a neighborhood contraction. It introduces no action parameters.

For caller-certified local blocks, the retained finite-history recurrence is

    v[i+1] = -C[i] v[i] + DL[i] u[i] + DR[i] u[i+1],  v[0] = u[0] = 0.

Let P be the exact stored binary64 approximation of -C. The caller must bind
the local certificates to the same frozen frames, inverse blocks and maps,
and supply a verified global gain k >= ||G deltaP|| < 1. Cache presence alone
does not certify these conditions.

## Center and source error

Maintain an exact dyadic Arb midpoint row B[i] mapping noninitial input
blocks to the response. Multiply P[i] B[i], add DL[i] to the last previous
input block when i > 0, and append DR[i]. Perform these operations in Arb.
Reset each resulting ball to its midpoint and retain its radius separately.
If the largest radius is r and the new row has n*m columns (m input blocks
of dimension n), its fresh operator error in Euclidean block-sup norm is at
most m*n*r, by summing Frobenius bounds for the square blocks. This includes
local coefficient uncertainty and current arithmetic error. Previous errors
are not silently discarded: transport them as additive sources through P
using `transport_local_errors`. Signed products are retained by that helper.
The resulting global E bounds the response error uniformly on the input
block-sup unit ball. No IEEE relative-error or underflow assumption is used.

## Two-radius norm

For every stored axis e, including nonunit axes, the identity

    u = e (e^T u) + (I-e e^T)u

is exact. For each input block B and output axis f, bound its LL, LT, TL, TT
contributions by |f^T B e|, ||f^T B||, ||(I-f f^T)B e||, and
||(I-f f^T)B||_F respectively. These are conservative for unrestricted
transverse input and do not assume orthogonality. Evaluate norms in Arb using

    ||(I-f f^T)X||_F^2 = ||X||_F^2 + (||f||^2-2)||f^T X||^2.

Sum over input blocks, then maximize each coefficient over output nodes.
Outward binary64 conversion rounds a positive underflow to the minimum
positive subnormal and rejects overflow. With aL = max ||e||, the transported
error contributes at most aL*E to the longitudinal input column and E to the
transverse input column. Apply `combine_stored_causal_errors` once per column:

    response_error <= (k*(aL*CL+CT) + E_column)/(1-k).

Project this error using the verified output projection norms. This includes
map/source cross errors without applying k twice. The fixed initial input
is excluded, even if a caller supplies a nonzero DL[0].

## Evidence and limitations

Tests compare exact rational scalar recurrences, noncommuting dyadic vector
responses with nonunit axes, interval-valued source errors, changed maps,
cancellation and subnormal output. They validate the arithmetic method;
they are not full physical-campaign evidence. A scientific consumer
must verify complete independently reproduced local data, source hashes and
the common map perturbation certificate before producing a physical-point
finite-history result. The generic helper deliberately keeps physical Z1,
branch continuation, physical quotient, Gate7 and full BHSM flags false.

## Full-campaign consumer

After the isolated DF campaign and local assembly have both completed their
independent repeats, run:

```text
python scripts/certify_n12_gate7_full_direct_causal_linear_defect.py
python scripts/certify_n12_gate7_full_direct_causal_linear_defect.py --recompute
```

The consumer requires exactly 370 local intervals, 741 independently
reproduced derivative points, matching raw and normalized source bindings,
and the unchanged foundation's maps, axes, frames and inverse blocks.
It captures computation sources before the bound and verifies them again
afterward. The second command recomputes the entire response and requires
byte-identical JSON. A differing candidate is retained beside the original.
The output is `BHSM_N12_GATE7_FULL_DIRECT_CAUSAL_LINEAR_DEFECT.json`, with a
separate `.reproduction.json` receipt after a successful independent repeat.
Its claim is a selected-branch fixed-frame finite-history linear defect;
the broader physical and completion flags remain false.
