# N12 reset-stratum moving-endpoint jets

Status: `RESET_STRATUM_TO_MOVING_ENDPOINT_TWO_JET_CHAIN_RULE_DERIVED`.

Let `Y(tau,xi)` be the retained maximal Euler--Dirac flow initialized by a
regular reset-stratum family.  Its fixed-time first and mixed second Jacobi
fields satisfy the triangular system

`D_tau J_h=DV J_h`,

`D_tau K_hk=DV K_hk+D2V[J_h,J_k]`.

The derivatives of `V` use the already-derived repeated implicit
Euler--Dirac solves; the ill-conditioned kinetic/Dirac block is not inverted
as a stored matrix.

Suppose the first action-owned event or regular stop is transverse and is
written `e(Y(T(xi),xi))=0`, with `alpha=De V != 0`.  Then

`T_h=-De J_h/alpha`,  `Z_h=J_h+V T_h`,

and

`T_hk=-[De(K_hk+DV J_h T_k+DV J_k T_h+DV V T_h T_k)`

`        +D2e[Z_h,Z_k]]/alpha`.

The mixed endpoint-state jet is the expression in parentheses plus
`V T_hk`.  Any terminal graph or endpoint observable follows by ordinary
composition: `mu_h=Dmu Z_h` and
`mu_hk=Dmu Z_hk+D2mu[Z_h,Z_k]`.

These formulas intrinsically remove autonomous time translation at the
moving endpoint.  For `J=cV`, the hitting-time variation is `T_h=-c` and
`Z_h=0`; the mixed identity cancels likewise.  This does not replace the
full hybrid history quotient, but it proves that no hand-projected endpoint
time direction or endpoint selector is missing.

The remaining task is quantitative rather than algebraic: propagate the
reset-stratum base and Jacobi family with certified continuum/domain margins
to the first actual event or canonical stop.  The resulting endpoint jets
then initialize the already-derived fixed-channel Weyl transfer.

No endpoint, selector, action term, scale, fit, time direction, or new gate is
introduced.  `Gate7=ACTIVE`, `Gate8=LOCKED`, chord 3 is unauthorized, and
`FULL_BHSM_COMPLETE=false`.
