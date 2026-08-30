# N12 Gate-7 exact-affine terminal stop transversality

The canonical first stop was initially certified by strict preterminal
positivity, a terminal sign bracket, and continuity.  That existence theorem
does not itself differentiate the hitting time.  The operator oracle needs
the endpoint motion, so a separate transversality certificate is required.

At the corrected endpoint `92.30513924040065`, the retained outward tensor
evaluator computes the mixed action derivative

`D^3 S[psi_24, psi_24, F] = Dlambda_24[F]`

inside `[-2.8366335400940093e-11, -2.836633533644921e-11]`.  The directions
are the materialized selected line and normalized exact-center field in
action coordinates; the interval evaluator divides by the retained Sobolev
weights and outward-rounds every elementary operation.

On the final Taylor--Volterra cone, write `rho` for the certified state
radius, `L_lambda` for the selected-descriptor second-derivative bound, and
`L_F` for the normalized-field first-derivative bound.  Then

`|Dlambda_x[F_x]-Dlambda_c[F_c]|
 <= rho (L_lambda + ||Dlambda|| L_F)`.

Using the retained final-node bounds gives the uniform interval
`[-2.8534925825891678e-11, -2.8197744911497624e-11]`.  It is strictly
negative.  Hence the selected eigenvalue is strictly decreasing along every
flow in the terminal cone, the terminal-cell zero is unique, and the local
first-stop time is differentiable with

`D_xi T = -D_xi lambda_24 / Dlambda_24[F]`.

This closes endpoint-motion differentiability only.  The 72-direction state
Jacobi path, compact Weyl first jet, heat-minus-zeta force, KKT root, and
physical Hessian remain open.  `FULL_BHSM_COMPLETE = FALSE`.
