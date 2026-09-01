# N12 force adjoint pullback

Status: `GATE7_FORCE_COVECTOR_REDUCED_TO_NESTED_ADJOINT_PULLBACK`.

The Gate-7 heat-minus-zeta force is a covector on the physical reset
quotient.  It therefore does not require one forward Jacobi propagation for
each of the 66 physical tangent directions.  After the operator cotangent

`W_C=(s_C m_C/2) exp(-ell^2 P_C) P_C^-1`

is pulled back through the fixed-channel assembly, write the resulting state
covector density as `q(t)` and its endpoint part as `g_T`.  For

`J_h'=A(t)J_h`, `J_h(0)=B_reset h`,

the moving transverse endpoint has the exact projection

`Pi_T=I-V(Y_T) tensor De(Y_T)/(De(Y_T)V(Y_T))`,

so `Z_h=Pi_T J_h(T)`.  The backward problem

`-p'=A(t)^dagger p+q(t)`, `p(T)=Pi_T^dagger g_T`

then gives

`F_h=<B_reset^dagger p(0)+q_direct,h>`.

Consequently the complete physical covector is

`F_phys=N_phys^dagger(B_reset^dagger p(0)+q_direct)`.

This is exactly equivalent to all forward first-Jacobi columns.  It does not
select a reset representative.  Since `Pi_T V(Y_T)=0`, the already-retained
autonomous time shift is annihilated without a hand gauge slice.

The implicit Euler--Dirac adjoint is inverse-free.  From `D s=b` and
`D delta_s=delta_b-delta_D s`, solve only
`D^dagger lambda=r_acceleration`; then

`<r_acceleration,delta_s>=<lambda,delta_b-delta_D s>`.

Thus the same factorization (or its transpose) is reused and the highest
action derivative before the first force remains `D3 L`.  `D4 L`, second
operator jets, reset curvature, and the geometry KKT Hessian remain required
on the later nonzero-force/Hessian branch.

The adjoint theorem shortens evaluation at each reset parameter but does not
turn the set-valued reset into one action-selected representative.  Closing
the physical saddle still requires either a parametric maximal-base oracle on
a regular finite endpoint stratum followed by a quotient root solve, or the
equivalent coupled forward--adjoint KKT boundary-value solve.  Gate 7 remains
active, Gate 8 is locked, chord 3 remains unauthorized, and frozen
predictions are unchanged.
