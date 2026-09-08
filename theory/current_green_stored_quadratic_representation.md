# Stored quadratic representation for signed center composition

The completed recovery contains 370 endpoint and 370 midpoint tensors. The
raw aggregate fails its unchanged relative Frobenius skew threshold of
`5e-13` on 82 tensors (40 endpoint, 42 midpoint). All other raw aggregate
checks pass. The raw tensors and failed aggregate remain intact.

For each output slice, interpret the stored binary64 entries as exact real
numbers. If `S = (Q + Q.T)/2`, then

```text
x.T Q x = x.T S x,
(q(x+y) - q(x) - q(y))/2 = x.T S y,
sym(M.T Q M) = M.T S M.
```

Thus S is the unique symmetric bilinear representative of the stored
quadratic form. Linear output maps commute with this replacement. This
identity applies to the Hessian quadratic form and its polarization; it
does not authorize replacing a general ordered bilinear or retarded kernel.

`symmetric_quadratic_center.py` constructs a symmetric binary64 center
`S_hat` without modifying Q. The companion producer bounds
`||S_hat-S||_F` with 512-bit Arb over the exact stored operands, checks all
740 shard hashes, and preserves the original `5e-13` norm tolerance.
The maximum local representation error is `1.3898229584309453e-11`;
the maximum error divided by the largest absolute raw entry is
`2.592623844350777e-16`. Downstream signed quadratic composition consumes
these explicit representatives and requires their current certificate.

This repair encloses only representation rounding. It does not enclose
the physical Hessian error, construction of directions, causal arithmetic,
or variation away from the stored center. A separate diagnostic at the
worst-skew midpoint (149; directions 14 and 60) found overlapping 512-bit
mixed derivative intervals in both orders, but approximately `0.001035`
absolute binary64 error in output 51. That single pair is not a global
Hessian error bound. The center calculation and remaining outward bounds
are still required before Gate 7 can close.

The immediate continuation is the supplemental kernel identity, bounded
pilot, missing midpoint blocks, and complete signed causal center screen.
No physical prediction or full BHSM completion follows from this repair.

## Scalar covector correction

The subsequent supplemental identity exposed a separate implementation
error. `action_bound` evaluates direction coefficients divided by the
metric weights W. Consequently a covector evaluated with `full_lift = W`
is a covector in raw coordinates. Contracting it against a vector already
in metric coordinates requires division by W. The original full tensor
kernel omitted this conversion in `term_D` and `term_G`. The rectangular
kernel evaluates the corresponding directions directly and has no such
covector conversion.

Writing `a = (1/W - I) c` for each affected covector, the correction is
the sum of its contractions against the second eigenvector and bordered
response derivatives, with the existing scalar numerator coefficients.
Two adjoint bordered solves evaluate this scalar correction without
recomputing the complete Hessian tensor. The correction is stored
separately, added only to output 98, and then symmetrized explicitly.
The original field outputs and raw shards remain unchanged.

At midpoint 0, directions 0 and 1, the uncorrected rectangular comparison
has relative Frobenius discrepancy `4.7507735399355114e-7`. Applying the
adjoint correction reduces it to `1.5550816977755345e-12`, below the
unchanged `5e-10` identity tolerance. Direct and adjoint corrections also
agree on the independent polynomial action regression. The adjoint
full-width pilot takes about 18 seconds, versus 517 seconds for explicit
second-response tensors. Its arithmetic error still needs an outward
enclosure before physical authority can be claimed.

The rectangular kernel now directly forms its six required right-leg
Hessian products, instead of every 98-by-98 Hessian entry for every right
direction. This is the same multilinear contraction with a different
evaluation order. The optimized midpoint-0 comparison is
`6.957730366159884e-12`. The widest/narrowest supplemental pilots take
20.1890/17.8936 seconds, compared with 132.2976/106.1959 seconds previously.
The all-740 scalar correction and all-370 supplemental campaigns are
required before the complete causal center can be materialized.
