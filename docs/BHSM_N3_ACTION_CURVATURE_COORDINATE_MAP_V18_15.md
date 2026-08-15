# BHSM N=3 action-curvature coordinate map v18.15

The v18.14 measurement reclassifies the apparent 1e-6 near-stall as not
explained by the action-normalized curvature scale.  This calculation derives
the permitted numerical response: an invertible change of variables built
from the exact retained action curvature.

The coordinate and canonical-velocity sector is pulled back through the
existing H6 amplitudes and the accepted period.  The multiplier sector uses
the existing Sobolev amplitudes.  Absolute-curvature normal modes define the
block coordinate map; only machine-precision numerical nulls retain unit
factors.  Period uses its independently measured global action curvature, and
the explicit event multiplier keeps its existing KKT normalization.

The new numerical variable is `x`, with

`y = y_v18.12 + P x`,

and its residual is exactly `F_exact(y_v18.12 + P x)`.  No residual row is
left-scaled.  Since `P` is invertible, the physical state and root set are
unchanged.  Direct source and nonzero-probe evaluations verify identical exact
376-row residuals, round-trip coordinates, eta domain, event definition, and
the complete-child persistence gate.
