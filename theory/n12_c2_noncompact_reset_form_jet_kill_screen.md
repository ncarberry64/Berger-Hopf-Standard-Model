# C2 noncompact reset form-jet kill screen

Fix a real negative spectral parameter and a retained finite birth trace space.
For the nested C2 form cores, write `M_T(xi,z)` for the birth Weyl map,
`U_T(xi,z)` for its Poisson operator, and `h` for a physical reset-quotient
direction.  The finite-core first variation has the action-owned form

`<a,D_h M_T b> = B_T,h(U_T a,U_T b) + C_T,h(a,b)`.

Here `B_T,h` is the derivative of the action-owned child operator coefficient
form and `C_T,h` is its retained event/birth contact variation.  The graded
heat-minus-zeta sources contract this operator jet only in the subsequent
force assembly.  None of these objects is an external boundary condition or
force value.

Because the physical reset quotient and birth trace space are finite
dimensional, the noncompact reset jet exists in operator norm exactly when

`J_T(h;a,b)=B_T,h(U_T a,U_T b)+C_T,h(a,b)`

is uniformly Cauchy for unit `h`, `a`, and `b`.  Explicitly, for every
`epsilon>0` there is a core time `T0` such that for all `S,T>T0`,

`sup_{||h||=||a||=||b||=1} |J_T(h;a,b)-J_S(h;a,b)| < epsilon`.

This is the exact weakest criterion for convergence of the full first Weyl
operator jet.  A tail estimate in a
relative form norm, together with Cauchy contact terms and uniformly bounded
Poisson maps, is a stronger sufficient route.  The coupled forward-adjoint
weak root is a potentially weaker, source-contracted route to the Gate-7
force after the already derived reset pullback; it need not construct the full
operator jet.

The existing maximal Friedrichs theorem proves the values `M_T -> M_max` and
compact-support weak variations.  It does not prove the displayed criterion
for the noncompact reset Jacobi field.  This logical separation is sharp: the
scalar family `f_T(xi)=sin(T^2 xi)/T` converges uniformly to zero, while
`f_T'(0)=T` diverges.  Conversely, a divergent ambient derivative can be
annihilated by the physical pullback, so an ambient absolute bound is
sufficient but not necessary.

For the actual C2 history, the exact `exp(-x)` and `exp(-2x)` coefficient jets
and fixed-channel transfer pencils identify every local integrand.  The
98-segment certificate evaluates only a finite prefix.  No retained theorem
currently supplies a maximal-tail envelope for the reset Jacobi field,
uniform Poisson traces, the full graded `q_heat-q_zeta` contraction, or their
combined contact tail.  Therefore the noncompact reset form jet, projected
zero-source force, saddle, and Hessian remain open.

The next admissible closure is a direct action-owned proof of the combined
projected force Cauchy condition, a proof of the stronger uniform form-jet
Cauchy condition followed by the retained source contraction, or a certified
finite later event or canonical stop to which the retained compact endpoint
theorem applies.
This result adds no selector, scale, recurrence, endpoint box, time direction,
or chord.
