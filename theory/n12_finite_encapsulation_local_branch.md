# N12 finite encapsulation local branch

Status: `FINITE_POSITIVE_TIME_ENCAPSULATION_EXISTENCE_CLOSED_LOCALLY`.

The certified reset image is post-event complete-child data.  It must not be
required to hit the encapsulation event again.  Formation is the pre-event
segment; the singular event completes encapsulation; the reset relation gives
the complete child; positive-duration child flow is the subsequent
decay/evolution phase.

Near the certified event, the retained gauge-fixed Euler--Dirac flow has the
exact simple-eigenline decomposition

`D_tau Y = (b_psi/lambda) Psi + V_hard(Y)`,

and

`D_tau lambda = (c_psi b_psi)/lambda + R(Y)`.

The continuum certificate gives `c_psi b_psi<0`, nonzero `c_psi` and
`b_psi`, and an invertible hard complement.  Taking `lambda`, rather than
physical time, as the independent variable produces

`dY/dlambda = (b_psi Psi + lambda V_hard)/(c_psi b_psi + lambda R)`.

This vector field is regular at `lambda=0`, with terminal tangent

`dY/dlambda|_E = Psi_E/c_psi(E)`.

Picard--Lindelof therefore supplies an `epsilon>0` and a unique local branch
`Y(lambda)`, `0<=lambda<=epsilon`, ending at the certified event.  Constraint
propagation keeps it on the retained constraint manifold.  The other metric,
lapse, eta, inertia, trace, gauge, and hard-Dirac margins remain positive after
shrinking `epsilon`; only the already-canonical selected eigenvalue reaches
zero.

Physical time satisfies

`dtau/dlambda = lambda/(c_psi b_psi + lambda R)`.

Because the denominator is negative near the event, forward physical time
decreases `lambda` to zero, and

`tau_E-tau(lambda) = lambda^2/(-2 c_psi(E)b_psi(E)) + o(lambda^2) > 0`.

Thus the local formation history completes encapsulation in finite positive
time.  At the endpoint, the certified regular set-valued event-to-complete-
child relation has a nonempty 67-dimensional fixed-event fiber.  The event
and child energy constraints both vanish, and the selected complete child has
certified positive-duration proper-time persistence.

This proves existence of at least one realized finite-encapsulation history.
It selects no reset-fiber representative, proves no post-event return, and
makes no universal reachability claim.  Infinite nonencapsulating histories
remain valid nonrealized mathematical histories.

The next Gate-7 owner is the zero-source weak geometry force on this retained
finite event/child operator, followed by the same-action saddle and the full
pair-plus-contact Hessian.
