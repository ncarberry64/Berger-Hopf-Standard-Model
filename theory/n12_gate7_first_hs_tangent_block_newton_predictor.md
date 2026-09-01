# Intrinsic first-HS tangent block predictor

Let `A_i` and `B_i` be the ambient 98-dimensional left and right
Hermite--Simpson linearization blocks and let `Q_i` be the orthonormal
73-dimensional endpoint constraint tangent.  Starting from zero reset
correction, the recurrence solves

`(Q_(i+1)^T B_i Q_(i+1)) y_(i+1) = -Q_(i+1)^T(r_i + A_i delta_i)`

and sets `delta_(i+1)=Q_(i+1)y_(i+1)`.  Thus the tangent projection of each
linearized shooting residual closes.  The ambient normal remainder is retained
as a diagnostic and is not asserted to vanish.  Only an exact nonlinear replay
after endpoint constraint projection can adjudicate whether this is the
missing derivative of the projected/recentered Newton map.
