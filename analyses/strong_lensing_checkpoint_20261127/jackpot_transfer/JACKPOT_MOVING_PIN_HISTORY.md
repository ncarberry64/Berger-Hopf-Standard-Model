# Moving pin: same present location and velocity, different histories

The pin is continuously coupled and can move relative to the stars. The common core does not acquire a clock or a trajectory. The experiment uses an explicitly hypothetical, dissipative *spacetime-side* regular surface response, not BHSM's derived galactic time law.

Take the earlier positive shape operator with dimensionless Fourier eigenvalue A(k)=k²(1+k²) and the trial evolution d_t w+A w=j_S+j_P(x-X(t)). Normalize length by 5 kpc only for using the archived stellar shape ratios; time and force normalization are unspecified. Use the two fixed Salpeter shape profiles (spherical deprojections), a compact regularized pin profile, equal dimensionless integrated force weights, and a zero-mean periodic box. Gaussian smoothing is held fixed across histories. The source profile T(k) always moves with the pin; no relaxation is applied to the source itself. The zero mean is a numerical regularization, not a model for the cosmic return flow.

For constant opposite relative velocities ±v, the response multiplier observed as the pin arrives at the origin is 1/[A(k)∓i k_x v] under the exp(-ik·x) transform. This is the retarded time integral for a constant-drift prehistory. For the stopped pair, bring each pin to the origin at time -T, keep both stationary thereafter, and apply exp(-AT) to the difference from the static solution. The stopping control therefore compares **the same present positions and velocities**, not merely the same positions. Abrupt stopping is a diagnostic trajectory, not an inferred black-hole orbit. No clock inside the core is involved.

Project the snapshot graph term using (1/2)∫(∂_z w)² dz and take the screen gradient. This retains pin/star cross terms. The calculation is intentionally equal-time, not full light-cone propagation; it omits explicit time-gradient readout, bulk metric response, conventional moving-lens effects, and endpoint changes. For the stopped pair it isolates the part of the optical snapshot due to stored history under these approximations. On the same annulus measure half the plus-minus difference relative to RMS of the static **shape-only** deflection. Remove in turn a common translation, independent first-order pin/star offsets, uniform deflection, shear and affine isotropic convergence via nested orthogonal projections. This is a local degeneracy test, not a nonlinear refit of the full lens model or a fit to any observed positions.

| Comparison (dimensionless times) | Odd response, fraction of static shape | After all first-order offset and affine controls |
|---|---:|---:|
| Stationary | 0 | 0 |
| drift 0.08 | 1.54–1.60% | 0.283–0.300% |
| drift 0.24 | 4.40–4.53% | 0.814–0.855% |
| opposite prior drifts, both stopped for 0.10 | 3.72–3.86% | 0.680–0.717% |
| opposite prior drifts, both stopped for 1.00 | 1.88–2.05% | 0.328–0.354% |

Zero drift produces identical results, reflection reverses the odd signal as prescribed, the nuisance projection spaces are nested, and the nondegenerate component persists across the 96³, 144³, and 180³ grids and box enlargement. The reduction after stopping longer is consistent with positive eigenmode decay. These percentages normalize to this particular trial shape and never to the measured total bending. They cannot be converted to a Jackpot angular residual because no physical response time, orbital velocities or history, source normalization, or nonconformal metric response has been supplied. No third-source data (indeed no ray coordinates) were used.

Replay: OPENBLAS_NUM_THREADS=1 python jackpot_moving_pin_history.py. For an actual Jackpot test, independently source the relative trajectories and spacetime-side timescale/readout, project through the shared early-ring lens map, and only then assess the held-out image. Do not infer those parameters from the held-out image.
