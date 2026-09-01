# N12 weight-seven transverse descriptor

Status: `EXACT_WEIGHT_SEVEN_PHYSICAL_DESCRIPTOR_HAS_25_CENTER_AND_25_STABLE_MODES_LOWER_WEIGHT_MODULATION_OPEN`.

Let `H0=sqrt(kappa0/42)` and order the exact weight-seven second variation as
`z=(delta q,delta dot(q),delta m)`.  After removing the common factor
`R4^7`, its Hessian blocks are constant along the round expanding balance.
The exact quadratic action and its linearized DAE are

`S7^(2)=1/2 integral R4^7 z^T H7 z d tau`,

`Hvv qdd+(7H0 Hvv+Hvq-Hqv) qd+(7H0 Hvq-Hqq)q`
`+Hvm md+(7H0 Hvm-Hqm)m=0`,

`Hmq q+Hmv qd+Hmm m=0`.

This is the second jet of the retained ADM kinetic, cosmological, and
weight-seven shift-response terms.  No inverse of the singular combined
velocity/multiplier Euler--Dirac block is defined or used.

There are twelve exact polynomial local time--lapse gauge chains.  For every
complex descriptor parameter `sigma`, their mode-`k` representatives obey

`delta u_k=H0 theta_k`,
`delta dot(u_k)=H0 sigma theta_k`,
`delta log(N)_k=sigma theta_k`,

and lie in `ker(A-sigma E)`.  Quotienting these chains leaves the 25 physical
coordinates `q0`, `w_0,...,w_11`, and `b_0,...,b_11`.  The common scale `q0`
is retained.  On the exact exponential leading orbit its constant tangent is
collinear with an autonomous constant time translation, but lower action
weights and the boundary Casimir break full-action scale invariance, so this
leading coincidence does not authorize deleting the common-scale force.

The inverse-free bordered KKT pencil on this quotient is `74 x 74`.  It has
24 algebraic infinite modes and 50 finite modes:

- 25 `CENTER` roots at `sigma=0`;
- 25 `STABLE` roots at `sigma=-7H0`;
- no weight-seven `UNSTABLE` root.

A separate constraint-solved Schur calculation, using only a
residual-certified symmetric solve on the algebraic multiplier block and no
combined Euler--Dirac inverse, returns the same two clusters and
multiplicities.

Every center amplitude belongs to the coupled lower-weight modulation
system

`D_tau^2 a+7H0 D_tau a`
`=R4^-2 F5(a,D_tau a)+R4^-4 F3+R4^-6 F1+R4^-8 F_minus1`
`+ Casimir and constraint corrections`.

Thus the common-scale center and all 24 transverse centers have a leading
relative `R4^-2` lift.  A slow equation
`D_tau a=(R4^-2/(7H0))F5(a,0)+O(R4^-4)` is valid only after a uniform
remainder and constraint-reduction theorem.  No numerical root comparable
to `R4^-2` is promoted to a physical eigenvalue.

The weight-seven system alone gives constant center amplitudes and
`exp(-7H0 tau)` velocity transients.  The full retained remainder has not yet
been proved to preserve a positive limiting `H4`, force an Osgood decay to
zero, or drive an event/canonical stop: the sign and uniform control of `F5`
remain open.  Under the owner finite-encapsulation ontology, an infinite
nonencapsulating continuation remains a nonrealized mathematical branch;
the already-certified local realized formation branch instead reaches the
existing event in finite positive time.

The next mathematical descriptor object is the constraint-reduced
weight-five center force and a uniform lower-weight remainder estimate.  The
physical Gate-7 zero-source force remains separately open on the missing
action-owned two-sided finite-history Calderon oracle.

`FULL_BHSM_COMPLETE=false`.
