# BHSM N=3 complete-child chart reconstruction v18.24

The v18.12 child is a continuation germ, not a substitute for evaluating the
event-to-child correspondence at the new v18.22 event.  This calculation
recomputes the full 14 by 26 boundary/BVP Jacobian using all child coordinates,
velocities and multipliers.

Pivoted QR selects a full-rank 14-variable local chart.  Numerical row scaling
uses only local Jacobian row norms and leaves the physical zero set unchanged.
The solve enforces three trace rows, seven Dirac constraints, two attachment
momenta and two resolved dynamic-flux rows.

No equation is added to the global 376-variable KKT.  Nonzero child motion is
retained.  Promotion remains pending until the independent two-scale flux
envelope and positive-duration persistence checks pass.
