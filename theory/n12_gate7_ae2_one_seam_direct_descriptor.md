# Gate-7 AE2 one-seam direct descriptor

Status: `ONE_SEAM_DIRECT_DESCRIPTOR_AND_SCHUR_EQUIVALENCE_DERIVED`.

The owner-authorized zero-source rule fixes the external E0 birth trace to
zero only after the closed action has been differentiated.  On a finite
formation prefix and a finite C2 Friedrichs core, the most direct Galerkin
realization therefore has Dirichlet data at E0 and at the far proof cutoff, but
it retains the E1/C2 trace as one internal degree of freedom.  If the two arm
forms are `K_f` and `K_c`, the direct action form is

`K_joint = K_f glued_at_E1 K_c + W_phys at E1`.

The seam node occurs once.  There is no pre-E0 arm, no `M_E0`, no dynamical
birth load, and no separately added seam force.  The reset lift is absorbed
by expressing the child coefficients in the common AE2 frame before the
element forms are assembled.

For scalar and factorized product-Dirac channels, each element is exactly the
retained action element already used by the C2 finite-core descriptor.  The
external nodes are eliminated by their fixed Dirichlet traces; this is not an
inverse of a kinetic or Euler--Dirac block.  The returned descriptor includes
the elementwise `D_x K`, `D_h K`, and `D_h M` arrays, so a reverse contraction
can act on the actual joint form without first constructing either arm's
Dirichlet-to-Neumann map.

For any positive shift, ordinary block elimination is only an equivalence
check.  Eliminating the formation and child interiors independently leaves

`S_AE2 = M_f + U_R^dagger M_C2 U_R + W_phys`.

Accordingly,

`det(P_joint) = det(P_f,int) det(P_c,int) det(S_AE2)`.

The implementation checks this identity with linear solves and never forms a
matrix inverse.  The direct and Schur routes are two representations of the
same operator and must not be summed.

This closes the exact finite-core one-seam descriptor type and its local
coefficient jets.  It does not select a member of the retained incoming
amplitude family, promote the 1,222-segment C2 edge to a physical endpoint,
or supply the maximal C2 quotient tail.  The remaining numerical owner is the
parametric interval realization of the incoming arm together with the
maximal graded C2 cotangent and projected Cauchy limit.

No selector, extra source, scale, recurrence condition, gate, or chord is
introduced.  Gate 7 remains open, Gate 8 remains locked, chord 3 remains
unauthorized, and `FULL_BHSM_COMPLETE=false`.
