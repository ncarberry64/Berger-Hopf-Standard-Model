# N12 finite terminal reset-stratum candidate

## Result and scope

The unchanged 57-row event-to-child reset relation has been continued in its
full 139-dimensional action-coordinate tangent, then intersected with the
child selected-event equation.  A numerical center is found with all reset
rows near zero and with the invariant one-sided hitting product strictly
negative.  This is a reproducible terminal-stratum candidate, not yet an
interval existence certificate.

No fixed-event slice is used.  The event and child states move together while
the retained event constraints, selected event row, four reset traces, child
constraints, and canonical momentum match are enforced.  A temporary
affine numerical slice locates one witness; it is coordinate machinery for an
existence search and is not a physical child selector or observable readout.

## Terminal test

For the child reduced Euler--Dirac Hessian, let `(lambda,psi)` be the simple
selected eigenpair transported by the retained reference.  Define

```text
b_psi = <psi,B_ED>,
c_psi = D^3 L[psi,psi,psi],
K_hit = c_psi*b_psi.
```

The finite one-sided normal form is terminal in forward physical time when
`lambda=0` and `K_hit<0`.  The product is invariant under changing the sign of
`psi`, even though both factors change sign.

The candidate is checked with the high-precision retained action blocks for
the reset residual and eigenvalue, and with a direct complex-step contraction
of the retained Hessian for `c_psi`.  The event and child Legendre margins,
selected-line gaps, full reset rank, and bordered 58-row rank are recorded.

## Remaining proof obligation

The center residual and Newton correction are numerical.  Gate 7 does not
close until independent directed-rounding linear algebra and retained-action
ball majorants prove a negative radii polynomial for the 58-row normal slice,
and the strict simplicity, Legendre, canonical-lift, boundary, and hitting
orientation margins transfer to that root ball.  No global uniqueness or
universal reachability is required.

