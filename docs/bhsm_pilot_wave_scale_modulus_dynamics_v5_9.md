# BHSM v5.9 Pilot-Wave Scale-Modulus Dynamics

Primary result: `BHSM_PILOT_WAVE_DOES_NOT_LIFT_SCALE_MODULUS`.

This sprint tests whether a BHSM-native pilot-wave layer can lift the v5.8
global scale modulus and select a finite primordial size. It does not force
closure. The result is conservative: a minimal pilot-wave dynamics can describe
an outward compact-to-expanding actual configuration, but the construction
remains globally scale covariant and does not derive `ell_star`, `M_star`,
particle masses, gauge couplings, CKM values, rare-B observables, or full BHSM
completion.

## Ontology

BHSM v5.9 separates four objects:

- `Psi[Q]`: universal wavefunctional on BHSM configuration space.
- `Q_actual`: actual configuration guided by `Psi`.
- `T(x)` and `Phi(y)`: scalar/topographic fields inside `Q_actual`, not `Psi`.
- `R[Q]` and `S[Q]`: amplitude and phase in `Psi=R exp(iS/hbar)`.

The reduced configuration is

```text
q^A = (L, sigma_scale),    L > 0
```

and preserves the v5.7 relative branch

```text
sigma_scale,0 = 1/2
M_BH/M_star = 1/2
R_BH/ell_star = 2
```

These remain relative ratios. They are not converted into physical units.

## Configuration Metric

The minimal scale-covariant configuration metric is

```text
ds_Q^2 = d(ln L)^2 + d sigma_scale^2
G_LL = 1/L^2
G^LL = L^2
sqrt(|G|) = 1/L
dmu_Q = dL d sigma_scale / L
```

The corresponding Laplace-Beltrami operator is

```text
Delta_G = L^2 partial_L^2 + L partial_L + partial_sigma^2
```

Global rescaling `L -> lambda L` is translation in `chi=ln L`, so the reduced
operator does not select an absolute finite `L0`.

## Reduced Dynamics

The reduced lapse-parametrized action is

```text
S_red = integral d tau [(1/2N) G_AB qdot^A qdot^B - N U_BHSM(q)]
```

with

```text
U_BHSM(L,sigma) = -1/2 alpha_scale sigma^2 + 1/4 beta_scale sigma^4
alpha_scale = 2
beta_scale = 8
sigma_scale,0 = sqrt(alpha_scale/beta_scale) = 1/2
```

The Hamiltonian is

```text
H_red = N [1/2 L^2 p_L^2 + 1/2 p_sigma^2 + U_BHSM(sigma)]
```

and the current reduced potential has `dU/dL=0`, so it preserves the v5.8 flat
scale modulus before quantization.

## Pilot-Wave Equation

The reduced timeless wave equation is

```text
H_hat Psi = [-hbar^2/2 Delta_G + U_BHSM(sigma)] Psi = 0
```

with Laplace-Beltrami ordering. Any factor-ordering ambiguity is recorded as an
open dimensionless convention and is not selected to force scale generation.

For `Psi=R exp(iS/hbar)`, the Bohmian split is

```text
1/2 G^AB partial_A S partial_B S + U_BHSM + Q_BHSM = 0
partial_A[sqrt(|G|) R^2 G^AB partial_B S] = 0
Q_BHSM = -(hbar^2/2R) Delta_G R
qdot^A/N = G^AB partial_B S
```

The local WKB branch used for the scale audit is

```text
Psi(L,sigma) = R_sigma(sigma) exp(i k ln L / hbar)
R_sigma = exp[-(sigma-sigma0)^2/(2 w_sigma^2)]
S = k ln L
```

On this branch the quantum potential is independent of `L`, so the quantum
force in the global scale direction is zero.

## Guided Trajectory

For `k>0` and unit lapse,

```text
Ldot = k L
sigmadot = 0
L(tau) = L_initial exp(k tau)
sigma_scale(tau) = 1/2
```

This conditionally gives an outward compact-to-expanding actual configuration.
It does not determine `L_initial`, a turning radius, `ell_star`, or a physical
mass scale.

## Hidden-Scale Audit

The sprint rejects hidden scale insertion through grid boxes, regulator
cutoffs, Gaussian widths, endpoint singularities, initial coordinate choices,
or factor ordering. `chi=ln L` is a chart convention, the Gaussian width is a
dimensionless local sigma-sector convention, and `L=0` is an excluded degenerate
boundary rather than a stable finite scale.

## Boundary State And Relics

An outgoing branch can encode a compact-to-expanding release only after a
primordial quantum boundary state is supplied. The branch orientation, width,
turning point, and absolute `L` are not derived in v5.9.

Redshifted relic matter and radiation remain physical on-shell relics, not
virtual. The pilot wave continues on configuration space; effective or virtual
language is reserved for boundary/topographic or quantum-potential memory.

## Open Gates

- `OPEN_MISSING_PRIMORDIAL_QUANTUM_BOUNDARY_STATE_CLOSURE`
- `OPEN_MISSING_NONLINEAR_GEOMETRIC_BACKREACTION`
- `OPEN_MISSING_GLOBAL_SCALE_MODULUS_ACTION_SOURCE`
- `OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR`
- `OPEN_MISSING_ABSOLUTE_ACTION_QUANTUM_OR_BOUNDARY_TENSION`
- `OPEN_MISSING_ABSOLUTE_SPECTRAL_EIGENVALUE_SOURCE`
- `OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT`
- `OPEN_MISSING_ALPHA_I_ACTION_DERIVATION`
- `OPEN_MISSING_G2_BH_ACTION_SOURCE`
- `OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE`
- `CKM_EXPONENT_NOT_DERIVED`
- `OPEN_MISSING_NEUTRAL_SCALE`
- `OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION`
- `FULL_BHSM_NOT_COMPLETE`

## CLI

```bash
python -m bhsm.interface pilot-wave-scale-modulus-status --format markdown
```

Recommended next construction sprint:

```text
bhsm-nonlinear-geometric-backreaction-v5-10
```
