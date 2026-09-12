# Reduced action Hessian on a correlated affine endpoint tube

The frozen trial domain is z0+E(e*l+t), with |l|<=rL and ||t||2<=rT.
The axis need not be normalized. The full transverse coordinate ball is a
superset of an axis-orthogonal ball. Both radii retain their existing conditional
trial status. The initial endpoint is fixed.

After dividing state coordinates by exact positive stored weights, write the
domain as a subset of B+u*l. B encloses only the transverse displacement and
center arithmetic; u retains the signed product E*e. Let X enclose all segments
b+s*u*l for b in B, 0<=s<=1. The ordinary mean-value identity gives

    H(B+u*l) subset H(B)+[-rL,rL]*D3S(X)[.,.,u].

Here H is the retained action Hessian, not the Hessian of the physical field.
The signed direction u is contracted inside the action before interval hulls.
The parent mixed-action evaluator includes every retained quadrature node,
the global inertia reciprocal, and the boundary term. Existing factored and
exact-zero mixed-jet contexts change the arithmetic expression only and are
explicitly source-bound. All uncertain state coordinates remain Arb balls.

The pilot computes the full 61-by-61 reduced action Hessian at one endpoint.
It attempts independent normalized-eigenpair inclusion, positive stored-reference
orientation, and zero-based index 24 isolation on the resulting matrix family.
Failure is retained in the matrix record and does not imply physical singularity.
The complete matrix calculation is repeated in another invocation and must
reproduce its bytes. A reproducible failed eigenpair attempt is still a failure.

This enclosure covers the correlated affine tube, not its larger coordinate
box. It cannot replace a whole-box certificate under that label. It does not
yet enclose the physical rate, its DF or Hessian, actual HS midpoint domains,
frame derivatives, a physical quotient, or a contraction. Gate7 remains open.

Run `python scripts/certify_n12_gate7_affine_action_hessian_pilot.py --endpoint 13
--preflight`, followed by the first numerical invocation without `--preflight`
and then a separate `--recompute` invocation when numerical capacity is free.
