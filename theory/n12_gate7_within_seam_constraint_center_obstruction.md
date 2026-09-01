# N12 Gate-7 within-seam constraint-center obstruction

The normalized action field and its first derivative must be evaluated along
an actual continuous center in the 25-row action constraint manifold.  The
birth macro node satisfies those constraints to numerical precision, but the
exact-affine correction develops a smooth constraint drift at later stored
nodes.  The first-hit midpoint state remains representative-only, and the
audit confirms that it is not itself a constraint-accurate center.  Cubic
Hermite interpolation plus the stored affine fine correction has a still
larger interior defect.

At each of the 47 seam midpoints, evaluate the 24 multiplier Euler--Dirac
constraints and zero Legendre-energy constraint with the retained full action
gradient and Hessian.  Normalize each residual by the action-coordinate norm
of its differential.  A local minimum-norm Newton correction is a diagnostic
of the defect and conditioning, not a replacement for the missing flow.

The midpoint corrections converge numerically to the constraint manifold, but
they are not connected by a certified normalized-action trajectory.  The
nodewise linearized corrections also exceed the certified macro-center radius,
so the drift cannot be hidden inside that radius.  Thus neither the corrected
stored nodes nor their interpolant can own a continuous variational carrier.
The next object is a direct, constraint-preserving normalized-action center
from reset to the certified first-hit interval; only then may `DF` be
propagated.

`FULL_BHSM_COMPLETE = FALSE`.
