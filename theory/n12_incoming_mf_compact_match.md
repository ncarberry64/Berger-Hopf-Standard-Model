# N12 incoming formation response compact match

Status: `INCOMING_MF_IDENTIFIED_AS_COMPACT_TERMINAL_BLOCK_AND_LAURENT_GERM`.

The physical incoming leg is the compact formation history from `C1` to the
new event `E1`.  Its already-derived two-boundary Calderon map has ordered
traces `(birth,new_event)`:

`[n_birth,n_event]^T = [[M00,M01],[M10,M11]] [u_birth,u_event]^T`.

The endpoint-role theorem identifies `u_birth=0` as the retained external
zero-source Dirichlet reference.  It is not an added physical boundary
condition.  Restricting the existing graph to this reference gives

`M_f(z;xi,lambda_0)=M11(z;xi,lambda_0)`.

This is the same object as the formation Schur complement already appearing
in the joint gluing identity,

`M_f=H-C^dagger A^-1 C`.

Thus the incoming diagram slot does not require a new C1 theory or a second
exterior response.

The stored terminal Weyl germ immediately induces the incoming germ.  For
proper duration `T` and finite real spectral parameter `z`,

`M_f_scalar=T^-1+T*(c exp(-2x_E)-z)/3+O(T^2)`,

and for the factorized Dirac channel,

`M_f_Dirac=T^-1+s_E+T*(s_E^2-z-s_dot_E)/3+O(T^2)`,

where `s_E=chi lambda_spatial exp(-x_E)`.  The action-owned formation
amplitude obeys `T(lambda_0)=a lambda_0^2+o(lambda_0^2)` with certified
positive `a`, so the response is finite for every sufficiently small
`lambda_0>0` and has leading term `(a lambda_0^2)^-1`.  No positive amplitude
or history member is selected.

What remains open is the complete finite-duration coefficient path and its
joint coupling to the action-owned C2 seam over the full graded spectrum.
The Laurent germ is not promoted to the full heat trace, and the event load
is still exactly `U_R^dagger M_C2 U_R+W_phys`.

`FULL_BHSM_COMPLETE=false`.
