# Gate-7 Hermite--Simpson Newton nonlinear source

After the first direct block-Newton step, reconstruct the exact midpoint field
from the nonlinear Gauss replay and reevaluate the 370 Hermite--Simpson block
residuals.  This residual—not the endpoint-field-matched cubic derivative
defect—is the equation linearized by the direct block operator.

The first block step reduces its own nonlinear residual and therefore remains
the active center solver.  Continuous and interval authority remain open.

`FULL_BHSM_COMPLETE = FALSE`.
