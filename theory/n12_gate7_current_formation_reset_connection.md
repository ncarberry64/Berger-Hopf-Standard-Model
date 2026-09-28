# Current formation history: reset connection checkpoint

Continuation of `01c7758cf9169943bd26139d8d9fb8ae3b78f8a5`.
The user's correction is adopted: no certified current incoming-parent
history is available to reuse. The required object remains
`CURRENT_CENTER_INCOMING_PARENT_FORMATION_HISTORY_AND_FIRST_JET`.

## New computations

The frozen node-13 center is on the outgoing C2 arm. Before constructing
an incoming arm, it must be connected to the two-sided reset. The new
predictor integrates the owned fixed-s field backward from this center
to `s=0`. It preserves the exact stored center midpoint, integrates
displacements, and evaluates new points with the 512-bit Arb action and
independently verified selected eigenline/index 24. It does not rerun
frozen endpoint, interval or 1,222-cell prefix producers.

| Computation | Result | Scope |
|---|---:|---|
| Outgoing predictor | reaches `s=0`, 108 new RHS evaluations, 9 accepted steps | Numerical trajectory only |
| Reset displacement in action coordinates | `1.3064804142013832e-4` | Relative to historical reset center |
| Historical 72-parameter fit norm | `1.3064804321954172e-4` | Initial guess only |
| Historical certified parameter radius | `1e-12` | Cannot cover this new point |
| Full 98-component outgoing fit residual | `1.818281765415385e-11` | No flow enclosure inferred |
| 58 nonlinear reset + 72 matching residual norm | `2.4444915881465874e-14` | High-precision action residual, float output |
| Preconditioned residual norm | `2.187708292540093e-14` | Historical Jacobian used only as preconditioner |

The matching routine accepted its initial linear predictor because its
preconditioned correction was below the declared numerical-guess threshold
`1e-10`; it did not perform a Newton correction. This threshold is not a
certificate tolerance and has not changed any frozen allowance. A small
residual does not certify either the trajectory or a current reset root.

Pointwise Arb evaluations of the two candidate endpoints give:

| Arm | Verified index | Selected descriptor at the numerical point | `ds/dell` at supplied `s=0` |
|---|---:|---:|---:|
| Outgoing C2, first 98 coordinates | 24 | `-6.254081396568035e-21` | `+2.077451161024447e-10` |
| Incoming E1, second 98 coordinates | 23 | `-4.266447879715766e-22` | `-2.292787693265354e-11` |

These narrow point enclosures exclude zero for the descriptor. They verify
the selected line and the expected orientation **at the guess**, not an
exact terminal fiber. The incoming implementation uses an explicit index-23
proposal followed by normalized eigenpair inclusion and inertia. The old
outgoing proposal hard-codes index 24 and cannot be used unchanged on E1.
No raw numerical eigenvalue is substituted for the physical signed descriptor.

The first binary64 predictor reached its 160-evaluation limit after only
two accepted steps. Its failed attempt is preserved. The high-precision
predictor is the usable numerical guess; neither attempt establishes decay
or loss of the physical branch.

## The incoming data still required

The exact reset owner is `aether_full_reset_action_jacobian.py`:
`full_reset_residual` and `full_reset_action_jacobian`. Its 57 rows are
outgoing constraints/energy (25), outgoing descriptor (1), configuration
matching (4), incoming constraints/energy (25), and momentum matching (2).
The terminal section appends the incoming descriptor as row 58.

The compact reset producer explicitly constructs a **proof section**:
138 terminal-reset tangent directions project to a 72-dimensional C2
seed image. The complementary 66 upstream directions are not selected
by that image. Before the extra terminal scalar/time restriction, the
existing fixed-seed theorem identifies 67 directions as the preceding
E1 tangent. These historical dimension statements are reused as provenance,
not newly certified current-center rank results.
The seed-invisible incoming directions are internal unknowns, not new
environment inputs and not the separately established 66D C2 child tangent.

The new numerical match uses the old 72+58 section only as an initial guess.
Setting the omitted 66 section coordinates to zero is not a proof that
their physical reactions vanish. The existing owner
`BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json` identifies their force as
the upstream formation plus interface-replacement action; it explicitly
leaves the actual joint base and adjoint open. Zero external forcing does
not set that internal action derivative to zero.

Thus the next solve must treat the incoming member and history together:

```
R_terminal(C2,E1) = 0,
F_upstream = D Gamma_joint_reduced | K_fixed_C2 = 0.
```

`F_upstream` is the already-owned stationarity condition, not an added
environment law. Its current numerical base, internally reduced derivative
and normal invertibility must be obtained in the coupled formation/reset
problem. The old proof-section convention supplies a starting guess only.

## Exact first-jet interface

For a transported fixed-arc jet `J`, regularized arc rate `V` and reset
event covector `g`, the moving hit correction is

```
dell_hit = -(g J)/(g V),
J_hit = J + V dell_hit.
```

The denominator must exclude zero. This is needed before pulling the 73
current directions to the reset; the current node-13 chart alone is not
that transported hit jet.

At a bound current reset, retain the 32 incoming-sensitive terminal rows
(configuration 4, constraints 25, momenta 2, incoming descriptor 1) and
the 66 reduced upstream stationarity rows. Differentiation gives

```
[R_in,E1 ; F_upstream,E1] J_E1
    = -[R_in,C2 ; F_upstream,C2] J_C2_hit.
```

`formation_reset_first_jet.py` implements this assembly and returns the
replay of **all 58** reset rows, including the 26 outgoing rows. It refuses
an absent upstream derivative. A focused exact test demonstrates that two
different upstream equations can satisfy the same reset derivative while
producing different incoming jets. No arbitrary kernel completion is
silently accepted as the physical 73D first jet.

After this current reset member/jet is bound, integrate the incoming
fixed-s arm with its negative descriptor arc rate and compose material
outputs into `FORMATION -> RESET -> CURRENT C2 -> CONTACT`. The existing
incoming tiny terminal segment supplies historical enclosure evidence;
its numerical base and endpoint cannot be promoted to the current history.

## Material derivative work retained

For the moving momentum seed `Pi=DGamma[B]`, the native flux uses
`F-Gamma_conormal-DPi[X]`. The new `material_momentum_rate.py` retains
all six contracted terms in its first variation:

```
D(DPi[X])[P] = D3Gamma[P,X,B]
             + D2Gamma[X,DB[P]] + D2Gamma[P,DB[X]]
             + DGamma[D2B[P,X]]
             + D2Gamma[DX[P],B] + DGamma[DB[DX[P]]].
```

The first four are `D2Pi[P,X]`; the last two are `DPi[DX[P]]`.
All are derivatives of the internally composed action and material seeds.
No generic operator derivative tensor is generated. Signed duration
contractions remain unbounded until composition. Identical interval
enclosures on different segments are not treated as the same uncertain
quantity. Atomic source IDs prevent counting a duration/adjoint term once
by geography and again by differentiation mechanism.

## Checkpoint and continuation

Packet: `artifacts/flagship_integration/gate7_current_reset_connection_20260927/`.
Producers: `predict_n12_gate7_reset_from_current_center.py`,
`match_n12_gate7_current_reset_candidate.py`, and
`evaluate_n12_gate7_reset_candidate_branches.py`.
The packet's validation/reproduction records contain exact commands and hashes.
The early `reset_match/candidate.npz` is preserved from an interrupted
report serialization; `reset_match_complete/` is the complete output.

First mathematical task: jointly correct/certify the current reset
connection and instantiate the owned upstream formation stationarity
response on its seed-invisible directions, using the saved predictor and
two-sided candidate as guesses. Then transport the actual 73D first jet
and evaluate the four material rows. This task is a coupled boundary/history
solve, not replacement of the absent incoming history by the C2 prefix.

`CURRENT_CENTER_INCOMING_PARENT_FORMATION_HISTORY_AND_FIRST_JET` remains
open. No incoming physical history, 73D history jet or material `4x73`
matrix is claimed by this checkpoint. No certificate tolerance was relaxed.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
