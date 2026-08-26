# N12 C2 signed finite-core adjoint assembly

Status: `SIGNED_FINITE_CORE_COEFFICIENT_ADJOINT_ASSEMBLED_ACTUAL_FORCE_OPEN`.

For an exact member of the reset-generated finite-core family, write

`Y_(j+1)=Phi_j(Y_j)`, `x_j=log R4(Y_j)`, `h_j=H_j(Y_j)`.

The inverse-free Weyl recurrence already supplies the signed coefficient
cotangent `(C_x,C_h)` for every real `z<0`.  Therefore its exact state
pullback is the reverse recurrence

`p_N=C_x,N x_Y,N+g_T`,

`p_j=C_x,j x_Y,j+C_h,j h_Y,j+Phi_Y,j^dagger p_(j+1)`.

This is the coefficient-specific realization of the retained continuous
adjoint theorem.  It includes moving proper duration and needs one reverse
covector sweep, not one forward Jacobi column per reset direction.  It forms
no inverse of the full Euler--Dirac block.

At the reset seam, the downstream result composes with the existing launch
adjoint:

`g_reset=Z^dagger d_upstream_interface+B^dagger p_C2,0`.

Thus the signed assembly pattern is complete on every exact finite-core
family member.  The stored proof centers still cannot be substituted for
that member.  The current repository also does not yet supply the actual
graded heat-minus-zeta spectral contraction or the signed upstream-history
covector.  Accordingly no numerical zero-force value, saddle, endpoint, or
maximal-tail claim follows from this theorem.
