# N12 parametric exterior-oracle executable interface

Status: `STABLE_WEYL_VALUE_AND_TWO_JET_SOLVER_DERIVED_ACTUAL_FINITE_STRATUM_DATA_OPEN`.

The fixed-stratum Weyl--Calderón value and its first two directional geometry
jets now have one executable, inverse-free realization.  For

`P(xi,z)=K(xi)-z I`

split into an action-owned boundary/interior partition, solve

`P_ii X=P_ib`,

`P_ii X'=K_ib'-K_ii' X`,

`P_ii X''=K_ib''-K_ii'' X-2 K_ii' X'`.

Then

`M=P_bb-P_bi X`,

`M'=K_bb'-K_bi' X-P_bi X'`,

`M''=K_bb''-K_bi'' X-2 K_bi' X'-P_bi X''`.

The implementation checks Hermiticity and a positive shifted-interior
coercivity margin, then uses linear solves only.  It forms neither the full
operator inverse nor the interior inverse and never inverts the Euler--Dirac
kinetic block.  A noncommuting `4 x 4` witness has interior residuals below
`3.2e-17`, block-unitary covariance residuals below `2e-16`, and first/second
centered-difference residuals `1.26e-11` and `2.92e-8`.

The tracked two-chord center paths were also checked as possible missed
inputs.  Their exact shadowing is certified through `2e-8`, but the second
chord reaches neither terminal event nor canonical domain exit.  The retained
zeta extension force is strictly additive, so that numerical end cannot be
promoted to the complete physical force domain.  This is an admissibility
check only: terminal recurrence is not reopened and chord 3 remains
unauthorized.

The executable algebra is therefore closed.  The missing input remains the
action-owned nonempty complete finite endpoint/canonical-stop stratum with
`K(xi)`, its first two physical geometry jets, the endpoint partition, and
the intrinsic exact gauge/time quotient.  Once supplied, the solver returns
the exterior bundle needed by the replacement force and geometry/reset KKT
Hessian.

`FULL_BHSM_COMPLETE=false`.
