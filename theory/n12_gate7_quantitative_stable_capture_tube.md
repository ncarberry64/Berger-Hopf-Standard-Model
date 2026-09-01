# N=12 Gate-7 quantitative stable capture tube

Status: `QUANTITATIVE_ASYMPTOTIC_CAPTURE_TUBE_CERTIFIED_RESET_ENTRY_OPEN`.

On the time/lapse quotient, let `a` denote the 24 boundary-shape
coordinates, let `eta` be the 25 physical velocity-normal coordinates, and
put `epsilon=R4^-2`.  The exact weight-seven center-family identity gives

`a'=eta_shape`, `eta'=-7 H0 eta`

at the round member.  This is stronger than a numerical spectral
classification: the zero section is the exact nonlinear leading center
family, and its velocity normal has the universal weight-seven damping.

The local full flow is a differential-algebraic system.  To control it
without inverting the ill-conditioned Euler--Dirac block, extract the 49 by
49 physical velocity/multiplier Dirac block from the directed Arb enclosure
of the exact weight-seven Hessian.  Scale it by the retained `H5` velocity
and `H6` multiplier weights.  Its directed determinant excludes zero, and

`sigma_min(D_tilde) >= |det(D_tilde)|/||D_tilde||_F^48`.

The resulting graph-to-product solve bound is below `1e774`.  No matrix
inverse is formed.  The existing projected third-variation bound `1e50`,
with an inflated factor `1e6` for the Euler--Lagrange product rules and
normal-coordinate contractions, gives

`M_flow = 1e830`.

The lower-weight and inverse-inertia derivative ledgers similarly give

`M_epsilon = 1e950`, `M_inverse = 1e1480`.

The parameter-dependent version of the already certified inverse-free
Krawczyk graph has slope bounded by `C_graph=2e1316`; this deliberately
inflates twice the complete lower-weight graph bound and the directed first
lift.  Write `h0_minus=195369153/500000000` and set

`rho_flow = h0_minus/(64 M_flow)`,

`epsilon_tube = rho_flow*(h0_minus/2)/(64 C_graph)`.

This gives a positive, extremely conservative existence scale.  It is not a
new physical threshold.  On the tube with center radius `rho_flow/2` and
stable radius `rho_flow/16`, the full normal Jacobian defect is below
`h0_minus/32`.  Hence, in the action-owned graph-normal coordinate,

`D+||eta|| <= -6 h0_minus ||eta||`.

Also `H4>=h0_minus/2`, so

`epsilon(t)<=epsilon(0) exp(-h0_minus t)`.

The exact kinematics and graph slope give

`||a'|| <= ||eta|| + C_graph epsilon`.

Integrating the two decays uses less than one quarter of the declared center
margin.  Thus the stable boundary is strictly inward, the center coordinate
cannot leave its outer ball, and the total state remains inside the much
larger certified geometric product ball.  Constraint/Dirac regularity,
metric positivity, positive lapse, shift admissibility, and positive
expansion are preserved.

The tube is understood inside the retained regular selected-line component.
If selected-eigenline simplicity or AE2/event regularity fails before entry
or during a connecting cover, that is an already canonical stop rather than
a failure of the trapping theorem.

Therefore every regular history entering this explicit tube is captured by
the retained finite-N12 asymptotic family and has the already certified
rank-72 relative tail.  What remains is to validate that a nonempty
event-generated reset-family stratum reaches the tube, or reaches an actual
later event/canonical stop first.  No selector, recurrence, chord, fitted
scale, new action term, or new physical time direction is introduced.  Gate
7 and full BHSM completion remain open.
