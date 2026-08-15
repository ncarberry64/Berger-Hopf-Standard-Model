# BHSM v16.14: N=3 KKT SR1 continuation

Starting from the exact accepted v16.13 state, this calculation reuses the
physical symmetric event-KKT Jacobian and applies symmetry-preserving SR1
secant updates.  Every step is trust-restricted and backtracked against the
complete nonlinear residual and the eta-Legendre domain.  The final state is
stored with hexadecimal floating-point values so the nonlinear solve can be
continued without rounding drift.
