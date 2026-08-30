# Gate-7 second block-Newton local trust predictor

Use the exact residual at the first damped sample to estimate the local
directional derivative of the projected/recentered Hermite--Simpson residual.
Minimize that local secant model inside the sampled damping radius and replay
the resulting smaller correction exactly.

`FULL_BHSM_COMPLETE = FALSE`.
