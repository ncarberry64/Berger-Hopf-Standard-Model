# N=12 finite-stop action-owned bordered-response theorem

Status: `ALL_12032_ACTION_OWNED_BORDERED_RHS_RESPONSE_TUBES_CERTIFIED`.

## Closed-system source

Only the external Cauchy/birth source is zero.  The bordered right-hand side
used here is the retained internal Euler--Lagrange forcing

`r=W_red([W_q D_q S,0]-H_red,q (W_q qdot))`.

The gradient, connection/contact, and configuration terms are assembled with
their signs at the exact center before a norm is taken.  No independent seam
force is added, and no child/contact response is separately zeroed.

## Response-level preconditioning

For the center selected line, let

`K0=[[H0-lambda0 I,psi0],[psi0^T,0]]`.

In its spectral basis, `K0^-1 r` consists of the 60 hard source coefficients
divided by their own signed gaps plus the selected border coefficient.  The
calculation evaluates this complete center response first.  It then bounds
the variation of the already-assembled source through the retained `D2` and
`D3` action tensors using the center spectral preconditioner.

The relative bordered-operator perturbation combines the signed center `D3`
blocks, the correlated `D4` remainder, and the certified selected-eigenvalue
shift.  If its bound is `eta<1`, the local response is enclosed by

`chart_factor * (1-eta)^-1
 * (||K0^-1 r0|| + ||K0^-1(r-r0)||)`.

The 64-way spectrum/projector balls remain valid parents.  The response proof
uses a fourfold local refinement, giving 256 cells per macro seam and
`47*256=12032` cells total.  This is proof mesh refinement only; it changes no
action, event, time, selector, or physical scale.

## Certified result

All 12032 response cells close.  Global bounds are:

- maximum center internal-source norm: `1300.8933303110653`;
- maximum center bordered-response norm: `13528.777126559336`;
- maximum preconditioned source variation: `202454.86639159566`;
- maximum relative bordered perturbation: `0.8826360121338405`;
- maximum Neumann factor: `8.52050120553494`;
- maximum complete bordered-response radius: `1596665.024471732`.

The response owner is seam 45, refined subspan 255.  Its certified parent is
64-way subspan 63.

The direct solve and spectral preconditioned center formula are compared by
backward error.  The maximum norm discrepancy is `0.005157922447324381`,
below the dimension-62 residual/inverse bound `0.056117521234508166`.

## Claim boundary

This closes the complete internal bordered response, but not its full first
variation as a physical vector field.  The next object is the differentiated
closed bordered system on the same mesh, followed by the finite
Green/Hermite shadowing radius, scalar first-hit interval Newton step, and
strict earlier domain-margin exclusion.  Gate 7 remains active and frozen
predictions remain unchanged.
