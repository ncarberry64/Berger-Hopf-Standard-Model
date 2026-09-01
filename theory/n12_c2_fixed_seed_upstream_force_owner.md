# N12 C2 fixed-seed upstream force owner

Status: `FIXED_C2_SEED_KERNEL_IDENTIFIED_AS_THE_PRECEDING_E1_HISTORY_TANGENT`.

The certified forward swap orders the stored reset product as `(C2,E1)`.  If

`J_R=[J_C2,J_E1]`,

then holding the outgoing C2 seed fixed gives

`K_fixedC2={0}_C2 direct-sum ker(J_E1)`.

The analytic block ranks are `rank(J_C2)=32` and `rank(J_E1)=31`, so this
space has dimension `98-31=67`.  Its projector agrees with the independently
stored fixed-seed lift projector to operator residual below `3.4e-12`, and
its C2 component is below `5.8e-15`.  Thus the 67 directions introduced by
the launch decomposition are exactly the already-known raw fixed-event
tangent, not a new family of local seam degrees of freedom.

This also corrects the force terminology.  A downstream C2 adjoint
annihilates this space, but the remaining covector is not an arbitrary new
surface force.  It is the heat-minus-zeta variation of the complete upstream
`C1 -> E1` history together with retained AE2 interface contacts.  The
independent AE2 fermion surface action is exactly zero; `U_R` carries no
independent Cayley phase; and the fermion `W_phys` block is zero.  These facts
do not make the upstream force vanish.  The existing `M_f` terminal block and
its whole-negative-axis enclosure provide a valid operator-response slot,
but neither its value nor seam invertibility contains the full incoming bulk
heat and zeta variation.  Historical reduced seam determinants do not supply
that full arm functional either.

Constraint-normal terms remain KKT multiplier shifts.  The retained physical
count is 66 after the whole-system time quotient, although its explicit
hybrid generator is still open; an intrinsic quotient formulation avoids
choosing a projected generator by hand.

Consequently the two algebraic pullback blocks should be evaluated as one
joint full-history forward-adjoint KKT problem on `C1 -> E1 -> C2`, including
the retained gauge/scalar contact and moving-endpoint terms.  This introduces
no selector, phase, endpoint, scale, gate, chord, or prediction.
