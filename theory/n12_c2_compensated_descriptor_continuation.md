# C2 compensated signed-descriptor continuation

The binary64 extended cover stops because the certified signed step is less
than one unit in the last place of the accumulated selected eigenvalue.  This
is removed without changing the action: carry the signed coordinate, its
square, the center-path upper bound, and the endpoint-tube upper bound in
80-digit Decimal arithmetic.

The action jet and all derivative majorants remain the retained binary64 N=12
objects.  A predicted center is stored in binary64, and the action-norm defect
between the intended predictor step and the representable stored step is
computed explicitly and added to the endpoint tube.  Decimal bounds are
exported to the existing ball routines with directed outward rounding.

For each accepted step the exact Decimal difference
`(s+Delta s)^2-s^2` is strictly positive, so the existing `Delta` and lapse
bounds yield a strictly positive proper-duration interval even when binary64
addition would report zero.  Every accepted rounding defect is part of the
proof tube.

This is a validated arithmetic/recentering adapter for the existing action
field.  Its eventual ball or Jacobi-majorant exhaustion is not an event or a
canonical stop.  No recurrence, terminal condition, selector, scale, new
action term, or chord is introduced.
