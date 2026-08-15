# BHSM N=3 targeted filtered continuation v16.46

This checkpoint rebuilds the exact physical Hessian at v16.44 and probes a
small damping/trust grid around the previous winner. Every candidate is
evaluated through the complete projected nonlinear KKT residual and Sobolev
domain guard. No physical equation, event, variable, or normalization changes.

The calculation advances joint Hopf-anisotropy, fiber-localization, common
scale, multiplier, period and event stationarity of the existing N=3 parent.
