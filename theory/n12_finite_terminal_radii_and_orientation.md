# N12 finite terminal radii and orientation certificate

## Scope

This certificate concerns the unchanged AE2 event-to-child reset relation.
The 57 retained reset rows are augmented by the selected child eigenvalue,
normalized by its transverse gradient on the reset tangent.  The resulting
58-row map is solved only on the 58-dimensional action-normal quotient.  No
reset member, new endpoint, selector, action term, scale, chord, or physical
time direction is introduced.

## Root ball

At the high-precision terminal candidate, independent `1e-20` and `1e-24`
analytic action Jacobians have rank 58.  Directed Decimal accumulation gives

\[
Y\le 6.0880680164\,10^{-13},\qquad
Z_0\le 2.2919046408\,10^{-6}.
\]

Retained-action `D3`--`D5` majorants, both selected-line Schur bounds, all
four bordered canonical-lift bounds, the nonlinear boundary chart, and the
canonical-momentum Hessian enclosure give

\[
Z_2\le 2.2988090713\,10^{10}
\]

on the containing `1e-10` component ball.  At `r=1e-11`,

\[
p(r)=Y+Z_0r+\tfrac12 Z_2r^2-r
     \le -8.2417657446\,10^{-12},
\qquad Z_0+Z_2r\le0.229883200<1.
\]

The smaller radii root bounds the actual solution distance by
`6.1312913269e-13`.  Thus a unique root exists in the selected normal slice,
and the full ambient zero set is a local 138-dimensional terminal reset
stratum.  This is local existence, not global uniqueness or universal
reachability.

## Margin transfer

The event and child selected eigenlines remain simple, both Legendre blocks
remain positive, all four canonical lifts remain invertible, and the terminal
normal block remains regular.  A full unrestricted `D4 L` bound is too coarse
to preserve the small child cubic `c_psi`; that diagnostic is explicitly not
used as sign authority.

The sign certificate instead retains the selected-line cancellations.  A
Decimal symmetric difference of the exact retained Hessian at soft offsets
`+/-0.01`, together with the action-derived selected `D5[psi^5]` remainder,
gives

\[
-2.2947719428\,10^{-11}
\le c_\psi(E_0)\le
-2.2944163183\,10^{-11}.
\]

On the solution enclosure the child eigenline graph norm is at most
`1.4737345436e-10`.  Expanding the normalized graph in the exact multilinear
identity for `D3 L[psi^3]`, and bounding the fixed-line state variation by
`D4 L[N,psi,psi,psi]`, yields

\[
c_\psi(E_*)\le -9.5310240409\,10^{-12}<0.
\]

The corresponding product-rule enclosure gives

\[
b_\psi(E_*)\ge9.9808547843\,10^{-5}>0.
\]

Consequently `c_psi b_psi<0` at the certified root.  The retained
desingularized selected-eigenvalue normal form therefore supplies a nonempty
local forward history reaching this terminal event in finite positive
physical time.  This does not require recurrence from a previously selected
child and does not assert that every admissible history reaches the event.

## Consequence

The finite terminal stratum, its regular margins, and its local forward
orientation are closed.  Gate 7 remains open.  Its next owner is realization
of the compact finite-endpoint operator and first physical reset-quotient jet,
followed by evaluation of the already-derived heat-minus-zeta force covector.
Gate 8 remains locked, chord 3 remains unauthorized, and frozen predictions
are unchanged.
