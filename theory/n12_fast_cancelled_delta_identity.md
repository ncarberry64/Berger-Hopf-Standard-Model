# N=12 combined-direction cancelled-descriptor identity

Status: `EXACT_ALGEBRAIC_ACCELERATION_VALIDATED`.

On the retained selected eigenline, the denominator-free state numerator is

`W=b_psi Psi+s V_hard`.

The descriptor numerator used by the same forward field is

`Delta=b_psi Dlambda[Psi]+s Dlambda[V_hard]`.

Because the eigenvalue differential is linear in its direction,

`Delta=Dlambda[W]`.

Thus the retained action Hessian needs one directional jet along `W`, rather
than separate jets along `Psi` and `V_hard`.  The state numerator, selected
line, hard response, and normalization are unchanged.  This identity does
not divide by `Delta`, invert the full Euler--Dirac block, or alter the
action, flow, event, selector, scale, gate, or chord.

`scripts/audit_n12_fast_cancelled_delta_identity.py` replays the split and
combined forms on five nodes of the global stop center.  The largest absolute
binary64 `Delta` difference is `3.483930015261985e-23`; the state numerator
and `b_psi` agree within the stated `1e-12` audit tolerances.  The combined
form is therefore the exact retained realization used for finer direct
centers and retained residual replays.

The optional JAX directional path is explicitly predictor-only and is not
covered by this authority statement.
