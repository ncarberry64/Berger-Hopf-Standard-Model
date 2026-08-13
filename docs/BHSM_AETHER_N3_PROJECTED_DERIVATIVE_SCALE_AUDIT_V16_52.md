# BHSM N=3 projected derivative-scale audit v16.52

This checkpoint evaluates the same event-multiplier-eliminated merit derivative
over perturbations from `1e-8` to `1e-4`. The action covector itself uses a
`2e-6` relative finite-difference scale, so a stable derivative sign and
magnitude above that numerical floor is required before another continuation
step is promoted.

The audit changes no physical equation or normalization. It distinguishes a
real projected descent direction from nested finite-difference noise.
