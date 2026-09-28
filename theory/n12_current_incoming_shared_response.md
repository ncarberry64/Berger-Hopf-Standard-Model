# Current incoming shared local response and clock

Continuation of `6ccc130e`. **The requested common finite-history family and
numerical q66/H66/B66x73 are not complete.** This checkpoint evaluates a new
shared local internal subsystem and its first response, rather than another
ten-sector endpoint split. It does not replace temporal/contact/heat internals
with the local subsystem.

## Common current numerical calculation

The base is unchanged: the branch-23 incoming half of
`gate7_current_reset_connection_20260927/reset_match_complete/candidate.npz`.
The frozen Q66 and local sector packet are consumed unchanged. The original
rate evaluator also remains byte-identical to the earlier checkpoint.

The new producer `scripts/build_n12_current_incoming_response.py` evaluates
the unsplit local action derivatives needed by the eigenline/hard-response
linearization, including only its contracted third/fourth derivatives. The
full raw Hessian was not retained in the earlier sector packet. Consequently
this calculation invokes that unsplit derivative evaluator once per run;
it does not invoke the ten-sector producer or generate replacement sector
values. Its gradient and Q66 curvature replay the frozen operands.

A source-fingerprinted, scoped return observer exposes the existing rate
owner's solved variables. It does not change its arithmetic, normalization,
selected branch, or derivative inputs. All coefficient consumers share:

```
n_local = (psi[61], lambda, hard[61], b)
F_local = ((H-lambda I)psi, (psi^T psi-1)/2,
           (H-lambda I)hard+b psi-rhs, psi^T hard).
```

The saved response has shape **124x66**. Its complete coupled residual and
linearization are replayed, together with a bordered adjoint for the output b.
This is a local implicit system, not the complete `F_internal` requested for
formation. Its dimension is not the full history's internal dimension.

| Check | Arb512 Frobenius upper bound |
|---|---:|
| Shared local internal residual | 9.983974e-108 |
| Shared local internal first-response residual | 4.562889e-55 |
| b forward/adjoint discrepancy | 9.498281e-64 |
| Replay of frozen local gradient | 2.565281e-149 |
| Replay of frozen Q66 local curvature | 9.285619e-66 |

The common coefficient map retains log radius, log lapse, lapse, unit
scalar/gauge potential, unit Weyl superpotential, proper log-radius rate,
and proper/coordinate zeta density. Their full 66-column first maps are
stored. The original attached action's binary64 `59/30` constant is retained
explicitly, without silent rational replacement.

## Descriptor and proper-time consistency

The selected eigenvalue at the exact saved candidate is enclosed near
**-4.266447879715767e-22**, with an enclosure excluding zero. The previous
point-rate packet supplied `s=0`; that coordinate is not the exact selected
eigenvalue at this candidate. The new local rate uses the selected eigenvalue
and its saved first jet, checked against the new internal linearization.

Writing `Delta=c*b+s*R`, the incoming lookback proper clock is

```
d tau_minus / d lambda = -N*s/Delta.
```

The lapse factor converts coordinate time into proper time. The independent
normalized-arc expression `-(N*s/||G||)/(Delta/||G||)` replays this convention.
At the saved candidate the clock is **-2.0798153777702883e-7**; it is not a
positive incoming duration. No absolute value, zero clamp, or historical
positive-duration substitution is applied. This is a current candidate
consistency limitation, not evidence that the action lacks an incoming law.

The formal zero-descriptor germ, evaluated using this candidate's local
coefficients, is

```
a = -N/(2*c*b),
D a = a*(D log N-D c/c-D b/b),
T_minus(A) = a*A^2+o(A^2) at an actual event.
```

Here `c=-2.294566700382748e-11`, `b=9.999984319774862e-5`, and
`a=2.4374086317318447e14`. This is a **formal local germ**, not a selected
amplitude, finite duration, certified event, or propagated current history.
Signed composition gives `||D a|| <= 1.896642e16`. With the retained proper
log-radius rate v, `||D(a*v)|| <= 2.037110e15`; it is nonzero.

## Compression evidence and remaining inputs

The fixed endpoint radius removes an independent radius input and the direct
endpoint first variations of V, W, and proper zeta density. It does not
remove coordinate-density lapse dependence, duration response, interior
radius response, or mixed/moving-reset/contact derivatives.

The sufficient-state ledger contains a unit Q66 direction that annihilates
the endpoint log-lapse and proper-rate rows with replay below **1.489471e-58**.
The formal duration coefficient still changes by **1.7698777040285006e16**
in that direction. Thus even endpoint radius, lapse, and proper rate together
are insufficient to remove the local internal clock response. This witness
does not establish a global minimal input count or remove any Q66 column.

`FORMATION_SUFFICIENT_STATE_LEDGER.json` classifies the union of operands
and preserves the exact unresolved numerical work:

1. A current positive incoming finite history, its owned amplitude/endpoint
   binding, and proper durations, including resolution of the approximate
   candidate's event inconsistency.
2. Coefficient and classical action history propagation with their shared
   internal response; endpoint coefficients alone are insufficient.
3. The joint temporal operator, contact variables, incoming M11, and graded
   heat-minus-zeta response, with the current maximal-child scope retained.
4. The current incoming 73-column launch/event/reset incidence. The node13
   downstream chart is not substituted for this map.
5. Full same-functional internal elimination and moving constraint curvature
   before numerical q66, H66 and B66x73 can be assembled.

No pre-E0 response or B_birth is introduced. The external E0 trace remains
Dirichlet generating data and there is one internal E1/C2 seam. No finite
proof horizon is selected as a physical duration. No stationary root or
formation first jet is claimed; Gate 7 and full completion remain open.

## Verification and retained artifacts

Authoritative local packets are `current_incoming_response_20260928/run2`
and `run3`, with byte-identical arrays and reports. Arrays SHA256:
`0FE84E15DA977DFC166F4927BF1B61EE87C80F4BDB4D395E2928C5A82332C3E3`.

Independent centered secants perturb current Q66 column 41 at steps 2^-24
and 2^-25. Relative discrepancies fall by a factor of four:

| Quantity | First step | Half step |
|---|---:|---:|
| Local internal response | 8.109260e-14 | 2.027315e-14 |
| Formal duration coefficient | 6.419520e-12 | 1.604880e-12 |
| Formal radius-history coefficient | 6.426181e-12 | 1.606545e-12 |

These are directional numerical checks, not neighborhood/history proofs.
`secants2` and `secants3` reproduce byte-identically. `run1` is preserved as
an earlier instrumented-evaluator prototype, not current authority.
`secants1` retains arrays from a report-path serialization failure; the
complete repeated runs supersede it.

The frozen local sectors, Q66, reset matching, node13 connection, C2 prefix,
four retention files, and preexisting direct-physical-value work are
unchanged. Nothing is published or deleted.
