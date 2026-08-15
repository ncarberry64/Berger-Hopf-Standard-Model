# BHSM N=3 invalid-model exact-merit promotion v18.33

Both the v18.29 source residual and v18.31 candidate residual are recomputed
independently.  The unchanged 376-row norm decreases from `0.828981635380544`
to `0.828979109495249`, with global eta `0.774408284487263`.

The freshly reconstructed child passes trace, seven constraints, momentum,
two-scale flux and positive-duration persistence while retaining nonzero
relative evolution.  This promotes the physical state only; the v18.31 MINRES
and Newton claims remain invalidated.
