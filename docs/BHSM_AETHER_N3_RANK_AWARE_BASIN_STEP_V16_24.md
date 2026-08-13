# BHSM v16.24: accepted rank-aware nonlinear basin step

The v16.23 rank-184 spectral direction continues to reduce the complete
nonlinear residual far beyond its initial radius-0.2 probe. The merit function
is nonmonotone on the full line, so v16.24 resolves the descent basin with an
explicit bracket and accepts its measured minimum before refreshing the
physical KKT Jacobian.

The accepted state uses the same anchored replacement action and an exact
event-multiplier projection. It changes no endpoint equation, derivative
stencil, quadrature, field content, gauge normalization, or Yukawa
normalization. Its role is only to advance the independently solved N=3 orbit
toward simultaneous stationarity and the physical soft-event equation.
