# Stored midpoint construction and physical-error aggregation

This calculation addresses the exact supplied binary64 operands. It does not
identify them with the physical first derivatives or physical frame. In
particular, the cached first derivatives were formed using the original
partition-axis normalization, while the complete center normalizes its axes
again. A common physical projector/derivative bridge remains required.

For endpoint frames F, supplied axes a, supplied first derivatives D, and the
stored positive step h, the mathematical midpoint target is the concatenation
of F(I-aa^T/(a^T a))/2 +/- hD/8. The initial fixed endpoint contributes zero.
The normalized projector is evaluated in Arb at 512 bits; its rational form
avoids unnecessary square roots without changing the exact expression.

The helper encloses both S^-1(M*-Mhat) and S^-1 M*-Xhat using the signed inverse
of the exact stored full basis S. The second quantity includes construction and
coordinate-solve arithmetic and REPLACES the earlier S^-1 Mhat-Xhat bound.
Adding it to that earlier bound would double count the solve contribution.
All exported midpoint/radius pairs are checked for Arb containment.

For the exact stored symmetric tensor Q, form LQ before bounding its UU, CU,
and CC block Frobenius norms. The output multiplication error is enclosed from
absolute products, including gradual underflow. With approximate coordinate
operator norms aU,aC and certified error norms eU,eC, the pullback difference is
bounded by

    ||(LQ)UU|| (2 aU eU + eU^2)
  + 2 ||(LQ)CU|| (aU eC + aC eU + eU eC)
  + ||(LQ)CC|| (2 aC eC + eC^2).

The concatenated endpoint input contributes the usual factor two for the
uniform quadratic coefficient. This bound excludes errors in Q and L; their
cross terms must be included before changing the full causal envelope. The
construction-only diagnostic is centered on Xhat and is not an independently
additive replacement certificate.

Reproduce selected points with:

    python scripts/certify_n12_gate7_stored_midpoint_kinematic_construction.py --midpoints 0,175,126,1,9,369

Use --all-midpoints explicitly for all 370 points. Each report retains exact
operand hashes, derivative-file hashes, and producer/helper source bindings.

The separate physical aggregation producer requires all 99 hash-bound upper
rows at each explicitly selected midpoint, reconstructs the full symmetric
error tensor, and applies the certified stored-output pullback helper. It does
not rerun the physical kernel or fill missing nodes with zero. Its coordinate
target remains the stored Mhat; using M* requires the new combined coordinate
bound and the corresponding physical-error cross terms.

    python scripts/certify_n12_gate7_selected_physical_hessian_pullbacks.py --midpoints 0

Materialize deterministic point artifacts twice and require byte identity.
Neither producer closes Gate 7, establishes a neighborhood contraction, or
promotes a physical spectrum, Museum exhibit, or manuscript claim.
