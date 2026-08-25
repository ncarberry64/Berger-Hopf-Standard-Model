# N12 C2 bordered-response second-variation ball

Differentiate the complete constrained response equation

`K(Y) x(Y)=f(Y)`, `x=(V_h,b_psi)`.

The exact-center tensor `K_0^-1 DK_0` is assembled before norms.  Across the
fixed-descriptor tube its variation is bounded by the retained `D4`, selected
eigenvalue Hessian, and selected-line second variation.  The dimensionless
self-consistency condition is

`2 r sup ||K^-1 DK|| < 1`.

Once this closes, the standard differentiated bordered identities give

`Dx=K^-1(Df-DK x)`,

`D2x=K^-1(D2f-D2K x-2 DK Dx)`.

The resulting fixed point encloses the response value and its first and second
variations on the incoming physical tangent tube.  The coefficient
`b_psi=<Psi,rhs>` is bounded separately; this preserves its exact structure
and proves positivity without importing the much larger hard-response norm.

This theorem removes the hard-response wrapping artifact.  It does not yet
enclose the second variation of the complete cancelled fixed-descriptor field
and therefore does not promote an event, stop, endpoint, or Gate-7 closure.
