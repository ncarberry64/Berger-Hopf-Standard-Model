# N12 local reset terminal-transversality audit

Status: `CERTIFIED_LOCAL_RESET_CHART_DOES_NOT_SUPPLY_A_LATER_EVENT_OR_STOP_STRATUM`.

This audit asks only whether the already certified local event-to-child reset
chart can be used, without a new continuation theorem, to manufacture the
finite later-event/canonical-stop stratum required after the asymptotic NHIM
absolute-angular-force no-go.  It does not ask whether such a stratum exists
farther along the 66-dimensional physical reset quotient.

Let `C_E(Y_C)=0` denote the 31 fixed-event child rows.  At the authoritative
N12 event-child checkpoint,

`rank D C_E = 31`,  `dim ker D C_E = 67`.

The stored Jacobian is differentiated in the retained action coordinates.
An orthonormal basis `N` of its kernel therefore gives the raw reset-fiber
tangent without introducing a physical selector.

For the child ordered-event Hessian `D_C`, let `(lambda,psi)` be the retained
simple selected eigenpair and let

`b_psi=<psi,B_ED>`.

The exact center third variation gives, for an action tangent `v`,

`D lambda[v]=<psi,D D_C[v] psi>`

and

`D b_psi[v]=<D psi[v],B_ED>+<psi,D B_ED[v]>`,

where `D psi[v]` is evaluated on the simple-branch complement by the reduced
resolvent.  No kinetic or Dirac block is inverted in this jet calculation.

The deterministic N12 calculation finds

- `lambda_C = 1.430742563850721e-9`,
- `b_psi,C = 1.9239527443160043e-3`,
- `||D lambda N|| = 2.148219418892478e-8`,
- `||D b_psi N|| = 1.2020638178085508e-2`.

Thus the best first-order action-coordinate distances are

`d_lambda = |lambda_C|/||D lambda N|| = 6.660132346203003e-2`,

`d_b = |b_psi,C|/||D b_psi N|| = 1.6005412656239076e-1`.

They exceed the existing `1e-11` certified direct root ball by factors about
`6.66e9` and `1.60e10`, and exceed the continuum transfer neighborhood
`7.62939453125e-17` by still larger factors.  A centered direct-action check
at action step `1e-6` agrees with the analytic steepest-`b_psi` derivative to
within twenty percent; this is a reproducibility cross-check, not an interval
enclosure.

The conclusion is deliberately about proof scope.  The local reset
submersion theorem does not provide a nonlinear graph out to either
linearized target and therefore cannot certify a later event, reverse the
outgoing terminal orientation, or create a canonical stop.  The calculation
does not prove that the global reset quotient lacks such histories.  It also
does not authorize a favorable child choice.  A global reset-stratum
continuation/degree theorem, or an independently certified finite forward
event/stop stratum, is still required.

No equation, action term, selector, scale, endpoint, stop, time orientation,
gate, chord, or frozen prediction is changed.  Gate 7 remains active.
