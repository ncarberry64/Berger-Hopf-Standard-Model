# N12 forward boundary-radius action projection

Status: `ACTION_OWNED_BOUNDARY_RADIUS_AND_JET_PROJECTION_DERIVED`.

The retained attachment chart already supplies the physical M4 radius. For
Galerkin order `N`, let

\[
 u_L=\sum_{k=1}^N(-1)^k u_k,\qquad
 v_L=\sum_{j=0}^{N-1}(-1)^j v_j.
\]

Then the action attachment coordinate and physical radius are

\[
 q_W=q_0+u_L-\tfrac12\log\cosh(2v_L),\qquad
 R_4=(RADIUS0/2)e^{q_W}.
\]

Thus `x=log R4` is not a new history variable. For state Jacobi fields
`q_h,q_k,q_hk`, its exact pullback is

\[
 x_h=D_qx[q_h],\qquad
 x_{hk}=D_qx[q_{hk}]+D_q^2x[q_h,q_k].
\]

The only nonlinear coordinate Hessian is the rank-one `v_L` block with
coefficient `-2 sech(2v_L)^2`. Globally in this finite action chart,
`||D_qx|| <= sqrt(1+2N)` and `||D_q^2x|| <= 2N`. Proper time gives
`d_tau x=D_qx[v]/N_boundary` with the already-positive action lapse.

The continuum maximal-flow theorem therefore owns the base radius history as
a composition with its unique maximal action flow. What remains is not a
radius postulate: it is the first and mixed-second state Jacobi cocycle,

\[
 J_h'=DV(Y)J_h,\qquad
 J_{hk}'=DV(Y)J_{hk}+D^2V(Y)[J_h,J_k].
\]

The existing N12 anchor ball has finite action third/fourth-variation,
Euler--Dirac inverse, and first-Jacobi generator bounds, but it covers only a
very short local interval and does not enclose the maximal component. The
next action task is to assemble `DV,D2V` from those retained identities on
general bounded-margin sets and propagate their cocycles. Terminal/Friedrichs
graph jets and a regular Weyl-chart cover remain open. No terminal return,
new selector, gate, chord, threshold, or physical variable is introduced.
