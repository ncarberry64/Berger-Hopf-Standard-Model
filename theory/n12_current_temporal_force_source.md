# Current temporal action source for the existing Gate-7 force

This supplies the residual term in the endpoint/adjoint representation of
the existing same-action force. It introduces no history, endpoint,
environment law, tolerance or completion gate.

## Owner identity

The source is bound to `_rate_enclosure` in
`scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py`, and to
`local_internal_system` in
`src/bhsm/interface/current_incoming_formation_family.py`. In raw coordinates,
with `z=(v,m)`, those retained equations are

```
H = L_zz
rhs = (L_q,0)-L_zq*v
r_e = (H-lambda I)*psi
r_h = (H-lambda I)*h+b*psi-rhs
G_raw = (s*v, b*psi+s*h)
nu = dt/d_arc = s/norm_G.
```

The existing metric weights are checked against the frozen state weights
before interpreting the raw/action conversion. Direct contraction gives

```
E = [H*(b*psi+s*h)-s*rhs]/norm_G
  = [b*r_e+s*r_h+b*(lambda-s)*psi+s*lambda*h]/norm_G.
```

The first 37 components are `D_arc(L_v)-nu*L_q`; the last 24 are
`D_arc(L_m)`. On the selected fiber and exact normal equations, E equals
`s^2*h/norm_G`. This is an algebraic description of the stored field, not a
change to it and not a claim that its Euler residual is identically zero.
No division by s occurs, so the identity remains usable at the event.

The first variation uses the frozen 124x66 normal response. Derivatives
of both normal residuals are retained through `F_n*Dn+F_xi`. The norm and
rate first derivatives reconstructed from these operands overlap the
stored derivatives. No action/Hessian producer is called.

## Temporal first variation and clock term

Let `pi=L_v`, `nu=dt/d_arc` and `m'=D_arc m`. Integration by parts, using
`q'=nu*v`, gives

```
D integral L dt = [pi*dq_total + (L-pi*v)*dt]_ends
                 + integral (S_Y*dY_arc + S_t*dt_arc) d_arc

S_Y = (-E_q, 0_v, nu*L_m)
S_t = E_q^T*v - L_m^T*m'.
```

The zero velocity slot only reflects integration by parts. The source and
adjoint still depend on velocity. Endpoint time motion and the time source
cannot be suppressed merely because the state source is small. The stored
candidate's clock retains its actual negative sign; no positive incoming
duration or event certificate is inferred from this point calculation.

For signed bookkeeping, the numerical packet uses

```
attached-action endpoints + attached-action residual integral
                         + heat-minus-zeta.
```

This equals the earlier classical-plus-heat representation, but its
attached time coefficient must not be replaced by the classical-only time
coefficient while still subtracting zeta. The packet supplies the attached
terminal time coefficient and verifies it against the frozen energy row.
All internal heat/contact/transport terms remain to be composed once.

## Current numerical result

Using the unchanged current branch-23 state, normal solution and Q66:

| Quantity | Outward upper bound |
|---|---:|
| Raw temporal Euler residual, Frobenius norm | 2.760225e-35 |
| Its first 66-column variation | 3.207066e-33 |
| State source | 7.797405e-32 |
| Fixed-time Q66 source contraction | 1.898782e-32 |
| Time source | 4.914544e-19 |

These are pointwise bounds in the frames stated in the report, not bounds
for an integrated force or an entire physical history. The residual was
not replaced by zero. The terminal momentum/time terms were not counted as
the complete force.

Reproduce with `scripts/contract_n12_current_temporal_residual.py --out ...`.
The primary/repeat directories and test result are recorded in
`artifacts/flagship_integration/current_temporal_residual_20260928/validation.json`.

## Remaining consumed contraction

The existing force obligation consumes the adjoint pullback of this source,
the other endpoint and its time dependence, and the signed joint heat-minus-
zeta cotangent. A source bound along the owned internal graph, or an
equivalent direct contracted integral bound, is enough; storing the graph
is unnecessary. The point packet alone cannot provide that integral bound.
The original complete q66/root/persistence objective remains active.

Gate7_closed=False. FULL_BHSM_COMPLETE=False.
