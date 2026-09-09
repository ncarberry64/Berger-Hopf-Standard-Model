# Pullback of a supplied physical Hessian error ball

Let `E` be the discrepancy between a physical Hessian in a specified stored
input basis and its stored quadratic representative. Suppose a separate
certificate supplies the entrywise enclosure `|E - E0| <= R`, with `R >= 0`.
Let `L` be the exact stored output map and suppose a coordinate certificate
gives `||X* - X||2 <= d`.

The target of this arithmetic helper is `sym(L E[X*,X*])`. It preserves
signed output-channel cancellation by first evaluating `L E0[X,X]` with the
existing pullback assembly enclosure. The input ball radius is bounded
entrywise by `sym(|L| R[|X|,|X|])`, using an independently enclosed positive
assembly. Symmetrization is an orthogonal projection for the Frobenius norm.

Writing `B = ||L||2 (||E0||F + ||R||F)`, the remaining coordinate perturbation
is bounded by

    B (2 ||X||2 d + d^2).

This includes the radius-coordinate cross term. The helper adds that bound,
the signed assembly rounding, and the positive radius propagation to obtain
a Frobenius ball about the stored correction tensor. Adding the norm of its
center gives a bound on the entire physical-error pullback. All norms and
scalar bound arithmetic are rounded outward; gradual underflow is retained.

The Hessian error ball and coordinate bound are caller-owned inputs. The
helper does not certify their physical origin, coverage, domain, or basis
identity. It uses the exact stored `L`; a separate bound is needed for the
cross term between physical Hessian error and output-map construction error.
It also does not cover physical direction construction, background/domain
uncertainty, a neighborhood remainder, or the final causal transport.

For a completed midpoint contribution acting on two endpoint coordinate
vectors each bounded by `rT`, their concatenated squared norm is at most
`2 rT^2`. A verified tensor Frobenius bound therefore contributes twice that
bound as a local uniform quadratic coefficient. Coverage of one midpoint
cannot be promoted to coverage of all midpoints or endpoints.
