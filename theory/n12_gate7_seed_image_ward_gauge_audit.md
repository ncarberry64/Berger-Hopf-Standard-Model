# Gate-7 reset-seed Ward/gauge audit

Status: `WARD_GAUGE_SHORTCUT_EXHAUSTED_RANK72_TAIL_RETAINED`.

Let `J_R` be the certified 57 by 196 reset Jacobian in the forward-swapped
ordering and let `B` be the stored 98 by 72 outgoing C2 seed-image basis.  The
first 25 rows of the outgoing block are the retained single-child
Euler--Dirac constraints and row 26 is the ordered-event equation.  Direct
nullspace comparison gives

`range(B) = ker(J_R[0:26,0:98])`,

up to the recorded numerical projector residual.  In particular, the 72
directions are the complete constraint-and-event tangent at the C2 birth
section.  The launch archive contains no additional gauge generator or gauge
quotient basis.

The tracked boundary-compatible gauge audit cannot be used to subtract a
dimension from this image.  It derives a principal `delta w=delta beta=0`
slice for a different weak Calderon problem and explicitly states that the
slice is not a global gauge theorem.  It supplies neither a 98-state Cauchy
gauge generator nor its membership in `range(B)`.

Ward/BRST also supplies no blanket annihilation.  The retained BRST ledger
cancels the longitudinal gauge/complex-ghost pair mode by mode, but leaves the
physical transverse-gauge/HS/Weyl leading heat coefficient `-5 sqrt(pi)`.
That identity acts on the quantum field grading; it does not make geometric
background seed variations invisible to the complete closed-system
functional.

Exact coupled time invariance remains useful only after a covector exists: it
makes the replacement covector basic and makes the raw bordered force-root
test equivalent to the quotient test.  It does not prove that the finite-core
covector net is Cauchy, and the explicit 196-state hybrid generator remains
unavailable for a separate image-membership calculation.

Therefore no Ward, BRST, principal-gauge, or time-quotient shortcut currently
reduces the remaining noncompact support.  Its exact coordinate form is the
72-vector net

`B^dagger (p_T(0)-p_S(0))`

together with the already-owned direct replacement increment.  The next
valid route is a source-contracted Cauchy estimate for this vector, a
quantitative reset-to-controlled-asymptotic connection with Jacobi bounds, or
a certified finite later event/canonical stop.  Dimension counting alone is
not a proof.

Only the external Cauchy/birth datum is zero.  No internal response is zeroed,
no gauge slice is inserted, and no selector, endpoint, recurrence condition,
scale, fit, gate, or chord is added.
