# N12 weight-five multiprecision nonpromotion audit

Status: `MULTIPRECISION_SOLVE_CLOSED_QUADRATURE_STABILITY_OPEN_COEFFICIENT_NOT_PROMOTED`.

The weight-five bordered lift was rebuilt with genuine `mpmath` action jets,
high-precision Gauss nodes and trigonometry, and 70-digit linear solves. The
48-, 64-, and 80-node solve residuals are below `1e-70`, so bordered-solve
roundoff is no longer the limiting error.

The common-scale coefficients are respectively
`66.494409659373...`, `66.494452982548...`, and `66.494334392983...`.
The 64-to-80 change exceeds the 48-to-64 change. Thus conditioning amplifies
remaining quadrature changes and the sequence does not certify a tight
coefficient enclosure. The corresponding rate corrections are negative in
all three runs, but even that sign is retained as an empirical robustness
observation rather than promoted as a full-action theorem.

The next rigorous object is an analytic small-local-block assembly in a
preconditioned physical basis, or a directed-rounding interval quadrature
bound. Brute-force increases in generic object-jet node count are not a
certificate. No `R4^-2` stability eigenvalue or full-remainder outcome is
promoted.

`FULL_BHSM_COMPLETE=false`.
