# Recovered descriptor owner: appended center linearization

Base: `b4c091f6aff19315039150dc1756c6f5f43e40c5`, on
`theory/gate7-66d-reduced-adjoint-integration`.

Required owner classification: **EULER_DIRAC_DESCRIPTOR_FIBER_OWNER_RECOVERED**.
This labels the existing scalar functional and its recovered row, not a passing
enlarged center certificate. Center adjudication is
**FAIL_FROZEN_FIBER_VALUE_AND_DESCRIPTOR_REACTION_REPLAY**.

The user's follow-up authorizes testing the appended linearization after
descriptor identity and nonzero null action. We retain the previous failed
value replay explicitly; no recentering or nonlinear work is performed.

## Frozen owner evidence

`n12_gate7_descriptor_fiber_owner_adjudication.md` supplies the side-by-side
provenance: identical finite N12 action, raw 61-by-61 velocity/multiplier
Hessian, same byte-identical branch reference and oriented normalized index-24
line. Historical lambda_event and the current carried signed s represent the
same scalar. A separately transported approximate (Y,s) pair need not lie on
the exact physical fiber.

The certified frozen point replay is unchanged:

```
s13               = 4.27486392211581918044e-10
lambda_event(Y13) = 4.27392731468065055923e-10
R_fiber           = -9.36607435168621208930e-14
R_fiber / 1e-7    = -9.366074351686212e-7.
```

Its rigorous enclosure excludes zero. No binary64 eigenvalue is used as a
replacement descriptor, and no point/action calculation is repeated. The
stored normalized null has dY13=0, giving
`D(R_fiber/1e-7)[u]=-0.5905685412122307`.

## Appended matrix and inverse

The external child coordinates are fixed in this internal linearization.
Therefore its first coordinate is the left descriptor and the last 74 are the
right reduced state/descriptor coordinates. Use the normalized physical fiber
row R_fiber/1e-7; keep all existing shooting-row scalings:

```
A75 = [ N13 e_s    M13 ]
      [   -1       0  ].
```

| Center linear-algebra test | Result |
| --- | ---: |
| Shape | 75 by 75 |
| Numerical rank | 75 |
| Stored-coefficient rank certified by inverse replay | 75 |
| Smallest singular value, diagnostic | 0.08965888937217105 |
| Condition number, diagnostic | 49.70557509373519 |
| Left inverse defect, Arb512 Frobenius upper | 5.531e-16 |
| Right inverse defect, Arb512 Frobenius upper | 7.298e-16 |

The inverse proposal is saved. These are rigorous arithmetic bounds for the
stored matrix, not neighborhood bounds on an implicit map. The old null with
left descriptor component 1 acquires last residual -1 and is eliminated. The
nonzero constant fiber residual is retained; invertibility does not make the
frozen center solve the enlarged equations. No Newton correction is applied.

## Existing reaction block as a Schur block

Use the original split P and stored inverse Pi. For the eight right reactions,
write `n_q=Pi_q N13 e_s`, `Q_actual=Pi_q M13 P_q`. In the coordinates consisting
of left descriptor followed by eight right reactions, the block is

```
Q9 = [ -1         0       ]
     [ n_q     Q_actual   ].
```

Eliminating the left descriptor leaves Q_actual exactly. Its Frobenius
difference from the archived Q is bounded by `7.175e-14`, with the signed defect
saved. Thus the old block is recovered with its stored-transform rounding
defect, not asserted bit-identical. The original Q and inverse are not changed.
This is the Schur block of the existing frozen coordinate split, not a new
nonlinear row-ownership theorem.

## Child tangent and full forcing replay

Keeping the state basis does not automatically keep its descriptor graph.
Let the saved diagnostic fiber row at node 13 be
`b=[Dlambda B13/1e-7,-1]`. On the frozen augmented child graph C13,
`||b C13||_F <= 9.396019467e-7` in stored-coefficient arithmetic. The 66 state
directions and all seven boundary directions are left unchanged, but exact
invariance of the augmented 66D tangent is not verified. Its stored descriptor
graph has a nonzero fiber defect. The diagnostic Dlambda still has no new
outward gradient-error certificate.

For an independent test against the prior passing full-history reaction replay,
use its frozen left history V0, which is parameterized by the node-14 child
coordinates. It is not interchangeable with C13. The fiber-consistent candidate
changes only its left descriptor row:

```
delta_s = b V0
Vnew    = V0 + e_s delta_s
Fnew    = F0 + Pi_q N13 e_s delta_s
Dnew    = -Q_frozen_inverse Fnew.
```

This retains the signed full shooting derivative; left/history forcing cannot
be left at its old value while claiming that its descriptor graph was changed.
The norm of delta_s is `9.503752405e-7`. The complete frozen N13 already includes
the direct left contribution and midpoint chain rule. No extra independent
history source is added.

| Reaction replay | Result |
| --- | ---: |
| Replay of old Dphi from saved F0 and Q inverse | <=5.317e-18 |
| New reaction equation residual Q Dnew+Fnew | <=2.685e-19 |
| New descriptor error against frozen truth | <=9.566859245e-7 |
| Frozen descriptor allowance | 8.915423761304125e-7 |
| Descriptor test | **fails** |
| Seven boundary tests | **all pass** |

The seven boundary error bounds are approximately
`(8.588e-10,5.222e-11,1.129e-10,8.535e-10,4.701e-9,1.287e-9,5.304e-9)`;
their frozen allowances are approximately `3.984e-8`. Exact bounds and original
allowances are retained in the packet, including a descriptor-error lower bound
strictly above the allowance. Neither the tolerance nor the expected
reaction map is fitted to the new result. Since b is a stored diagnostic
covector, this is a failed frozen-coefficient comparison, not a proof of
physical failure or a certified perturbed physical map.

## Stop

The existing fiber equation resolves the algebraic null and its descriptor
ownership is recovered. The requested enlarged center certificate nevertheless
does not pass: the frozen center has a certified nonzero fiber value defect,
the augmented child tangent is not unchanged, and the descriptor reaction
comparison exceeds its existing allowance. A successful center/slaving theorem
cannot be inferred from rank 75.

No scalar, seam rule, physical parameter, tolerance or endpoint was invented.
No seam search, scientific producer or nonlinear work was repeated.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.

Reproducer: `scripts/test_n12_gate7_appended_fiber_center.py`.
Packet: `artifacts/flagship_integration/gate7_appended_fiber_center_20260926/`.
Two fresh processes reproduce the arrays and report byte-identically.
`python -m pytest --noconftest tests/test_gate7_appended_fiber_center.py tests/test_gate7_descriptor_fiber_owner.py -q`
passes **8 tests**, including inverse replay, Schur elimination, changed left
forcing, frozen allowances and fail-closed flags.
The next prerequisite is an owner-bound treatment of the fiber value defect
and corresponding tangent/response changes; this checkpoint does not alter
the frozen center or claim that a nearby corrected center passes.
