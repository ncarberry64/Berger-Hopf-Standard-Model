# N=12 Gate-7 recentered-cone bordered-response first variation

Status:
`RECENTERED_GATE7_CONE_COMPLETE_BORDERED_RESPONSE_FIRST_VARIATION_CERTIFIED`.

## Differentiated closed system

The complete action-owned internal equation is differentiated before norms:

`K x=f`,

`K D_xi x=D_xi f-(D_xi K)x`.

Only the external Cauchy/birth source is zero.  All child, contact,
configuration, transport, scalar/topographic, and retained AE2 seam terms
remain inside `f` and `D_xi f`.  No independent seam force is introduced and
no internal response is separately zeroed.

The 24,072 response cells and their 3,009 certified parents are consumed in
the exact existing order.  The selected branch is `24` and the physical
tangent quotient has dimension `101` everywhere.

## Common-frame child/parent lift

Each recentered product cone has coefficient projection

`P=sqrt(2)[A,rho I]`,

where `A` contains the three path columns and `rho I` is the full retained
98-dimensional nonlinear halo.  The squared norm of the minimum parent
coefficient lift of a child direction is the largest generalized eigenvalue
of

`A_child A_child^T+rho^2 I`

against

`A_parent A_parent^T+rho^2 I`.

Both metrics equal `rho^2 I` outside the at-most six-dimensional common frame
of the parent and child path columns.  The certificate therefore solves only
this small generalized descriptor problem.  It never forms a 98-dimensional
inverse.  The maximum lift is `1.0010097162557205`; the eight response
children are thus subordinate to their action-bound parents without the
artificial `1.46e5` amplification of a halo-only representation.

## Uniform derivative enclosure

The stored parent `D3` Hessian derivative and twice the stored half-`D4`
Taylor remainder give the uniform Hessian derivative.  The selected-line
graph derivative supplies the border derivative.  Consequently

`||D K|| <= 2 ||D H||+||D psi||`.

The complete internal-source cotangent is taken from the already certified
assembled product rule.  With the certified bordered inverse,

`||D x|| <= ||K^-1|| (||D f||+||D K|| ||x||)`.

All terms are finite on every cell.  Global bounds are:

- maximum common-frame direction lift: `1.0010097162557205`;
- maximum bordered-operator coefficient derivative: `0.03766827876244784`;
- maximum internal-source cotangent: `186771275.83134463`;
- maximum combined differentiated RHS: `186779845.7631688`;
- maximum complete response first variation: `9.698556455702094e14`.

The first-variation owner is the final response child of seam `45`, on
`[91.99609375,92.0]`.  The large ambient norm is a rigorous conditioning
bound, not a promoted instability: it retains the hard inverse outside the
signed source/operator cancellation so the next reverse-adjoint projection
can sharpen only the observable Cauchy cotangent actually needed.  The
physical nonlinear halo used on that child is
`1.243972269022099e-12`; the much larger matched Green center correction is
part of the proof center and is not misclassified as nonlinear radius.

## Claim boundary

This closes the maximal graded internal-source cotangent, the reverse-adjoint
response bound by duality, and the complete response first-variation tube.
The projected Cauchy tail, finite causal interval-vector radius, and
domain/first-hit transfer remain open.  Gate 7 remains active and
`FULL_BHSM_COMPLETE` remains false.
